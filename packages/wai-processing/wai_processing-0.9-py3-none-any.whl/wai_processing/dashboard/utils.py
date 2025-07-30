import asyncio
import logging
import time
from pathlib import Path

import aiofiles.os
import plotly.express as px
import plotly.io as pio
import polars as pl
from tqdm import tqdm

from wai.io import get_processing_state

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("dashboard")


def filter_datasets(dashboard_handler, datasets_option):
    """
    Filters datasets based on the provided options.
    Args:
        dashboard_handler: An object containing information about the available datasets.
        datasets_option (dict): A dictionary containing the filtering options. It should have a "names" key with a list of dataset names to include. If the list contains the string "all", all datasets are included.
    Returns:
        list[Path]: A list of Path objects representing the filtered datasets.
    Notes:
        If "all" is in the list of dataset names, all datasets from the dashboard handler are returned. Otherwise, only the specified datasets are returned, sorted alphabetically.
    """
    if "all" in datasets_option["names"]:
        return dashboard_handler.datasets
    else:
        return sorted(
            [
                Path(f"{dashboard_handler.cfg.root}/{path}")
                for path in datasets_option["names"]
            ]
        )


async def get_mtime(file_path, semaphore):
    """
    Asynchronously retrieves the modification time of a file.
    This function uses a semaphore to limit the number of concurrent file access operations,
    ensuring that system resources are not overwhelmed.
    :param file_path: The path to the file whose modification time is to be retrieved.
    :param semaphore: An asyncio.Semaphore object used to control concurrency.
    :return: A tuple containing the file path and its modification time, or None if the file is not found.
    """
    async with semaphore:
        try:
            mtime = await aiofiles.os.path.getmtime(file_path)
            return file_path, mtime
        except FileNotFoundError as err:
            logging.error(f"Error while reading {err}")
            return file_path, None


async def gather_mtime_process_logs(root, max_concurrent_tasks):
    """
    Asynchronously gathers the modification times of all files in a dataset (directory).
    the modification times for each file.
    :param root: The root directory to scan for files.
    :param max_concurrent_tasks: The maximum number of concurrent tasks allowed for file access.
    :return: A list of tuples, each containing a file path and its modification time.
    """
    # Create a semaphore to control the number of concurrent tasks
    semaphore = asyncio.Semaphore(max_concurrent_tasks)
    # Asynchronously scan the directory for entries
    entries = await aiofiles.os.scandir(root)
    # Use a TaskGroup to manage concurrent tasks for retrieving file modification times
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(get_mtime(entry, semaphore)) for entry in entries]
    return [task.result() for task in tasks]


async def scan_process_logs(df_dataset, dashboard_handler, root, max_concurrent_tasks):
    """
    Scans a directory for _process_log.json files and updates the SQLite database.
    This function checks for modified or new process log files in the specified directory,
    processes them, and updates the database with the latest information.
    :param df_dataset: A Polars DataFrame containing the current dataset information.
    :param dashboard_handler: An instance of DashboardConnectionHandler for database operations.
    :param root: The root directory to scan for process log files.
    :param max_concurrent_tasks: The maximum number of concurrent tasks allowed for file access.
    :return: A tuple containing the updated DataFrame, dataset name, and elapsed time for the operation.
    """
    dname = Path(root).stem

    # Start timing
    start_time = time.time()

    last_modified = await gather_mtime_process_logs(root, max_concurrent_tasks)

    logger.debug(f"gather_mtime_process_logs took {time.time() - start_time}")
    # retrieve all the file_mtime from the df dataset by building a dict scene -> file_mtime for fast O(1) lookup
    dict_file_mtime = (
        df_dataset.group_by("scene")
        .agg(pl.col("file_mtime").first())
        .rows_by_key(key=["scene"], named=True, unique=True)
    )
    # alternative: dict_file_mtime = df_dataset.rows_by_key(key=["scene"], named=True, unique=True)
    # Scan for changed files
    rows_to_insert_or_replace = []
    for entry, mtime in tqdm(last_modified, f"Scanning '{dname}'"):
        scene_root = Path(entry.path)
        scene_name = entry.name
        # Check if file has been modified since last scan
        try:
            result = dict_file_mtime.get(scene_name, None)
            # result = dict_file_mtime[]
            if not result or result["file_mtime"] < mtime:
                # File is new or modified, process it
                processing_state = get_processing_state(scene_root, retry_delay=0.001)
                # Update or add entries
                for stage, stage_log in processing_state.items():
                    # cumulate all the inserts or replace to make a single query
                    rows_to_insert_or_replace.append(
                        [
                            dname,
                            scene_name,
                            stage,
                            stage_log["state"],
                            stage_log["date"],
                            stage_log["message"],
                            mtime,
                        ]
                    )
        except Exception as err:
            logger.error(f"Error {err} accessing {scene_root / scene_name} stats")

    logger.debug(
        f"Detected {len(rows_to_insert_or_replace)} entries to insert or update in {dname}."
    )
    # at least one element to insert or replace is found, we need to commit changes
    if len(rows_to_insert_or_replace) >= 1:
        df_scene = pl.DataFrame(
            rows_to_insert_or_replace, schema=dashboard_handler.columns, orient="row"
        )
        df_dataset = df_dataset.update(df_scene)
        await dashboard_handler.db.executemany(
            """
            INSERT OR REPLACE INTO process_logs (dataset, scene, stage, state, date, message, file_mtime)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows_to_insert_or_replace,
        )
        await dashboard_handler.db.commit()
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    return df_dataset, dname, elapsed_time


async def process_data(dashboard_handler, selected_datasets_option, client):
    """
    Processes data for the selected datasets.
    Args:
        dashboard_handler: An object handling the dashboard connection.
        selected_datasets_option (dict): A dictionary containing the dataset filtering options.
    Returns:
        dict: A dictionary containing the processed data, including HTML figures for each dataset, failed scenes, total failed scenes, and load times.
    Notes:
        This function filters the datasets based on the provided options, retrieves the SQLite database, and processes the logs for each dataset. It then generates Plotly bar charts for each dataset and prepares the data to be sent to the client.
    Raises:
        Exception: If an error occurs while processing the data.
    """
    selected_datasets = filter_datasets(dashboard_handler, selected_datasets_option)
    start_time = time.time()
    dataset_figs_html = []
    failed_scenes = {}
    total_failed_scenes = {}
    load_times = {}  # Store load times for each dataset

    logger.info(
        f"Client {client} Currently selected {len(selected_datasets)} dataset(s): {selected_datasets}"
    )
    # retrieve the sqlite database
    async with dashboard_handler.db.execute("SELECT * FROM process_logs") as cursor:
        result = await cursor.fetchall()
        df_complete = pl.DataFrame(
            result, schema=dashboard_handler.columns, orient="row"
        )

    # iterate over all the datasets
    for wai_path in selected_datasets:
        dataset_name = wai_path.stem
        # filter current dataset
        df_dataset = df_complete.filter(pl.col("dataset") == dataset_name)
        # Process logs and update the database
        df, dname, elapsed_time = await scan_process_logs(
            df_dataset,
            dashboard_handler,
            wai_path,
            max_concurrent_tasks=dashboard_handler.cfg.get(
                "max_concurrent_os_reads", 100
            ),
        )
        load_times[dname] = elapsed_time
        logger.info(f"{dname}: {len(df)} records loaded in {elapsed_time:.2f}s")
        if len(df) == 0:
            continue
        # Extract failed scenes for this dataset
        failed_df = df.filter(pl.col("state") == "failed")
        total_failed_scenes[dname] = failed_df.height
        if not failed_df.is_empty():
            # could add this before to dicts to limit the size of object .head(dashboard_handler.cfg.error_page_size)
            failed_scenes[dname] = failed_df[
                ["scene", "stage", "date", "message"]
            ].to_dicts()
        state_summary = df.group_by(["stage", "state"]).agg(pl.len().alias("count"))
        if dashboard_handler.cfg.show_all_stages:
            for stage in dashboard_handler.cfg.stages:
                if stage not in state_summary["stage"]:
                    new_row = pl.DataFrame(
                        {"stage": [stage], "state": ["missing"], "count": [0]},
                        schema={
                            "stage": pl.Utf8,
                            "state": pl.Utf8,
                            "count": pl.UInt32,
                        },
                    )
                    state_summary = pl.concat([state_summary, new_row])

        stage_to_display = list(state_summary["stage"].unique())
        # Generate a Plotly bar chart for the dataset
        fig = px.bar(
            state_summary,
            x="stage",
            y="count",
            color="state",
            title=f"{dname} (loaded in {elapsed_time:.2f}s)",  # Add load time to title
            color_discrete_map={
                "finished": px.colors.qualitative.Plotly[2],
                "running": px.colors.qualitative.Plotly[0],
                "failed": px.colors.qualitative.Plotly[1],
                "missing": px.colors.qualitative.Plotly[4],
            },
            category_orders={"stage": stage_to_display},
        )
        dataset_fig_html = pio.to_html(fig, full_html=False)
        dataset_figs_html.append(dataset_fig_html)

    # prepare data to send it to client
    data = {
        "dataset_figs_html": dataset_figs_html,
        "failed_scenes": failed_scenes,
        "total_failed_scenes": total_failed_scenes,
        "load_times": load_times,  # Include load times in the data
    }
    logging.info(f"Client {client} generation took: {time.time() - start_time}s.")
    return data


async def handle_client_request(websocket, dashboard_handler, selected_datasets_option):
    """
    Handles a client request to process data.
    Args:
        websocket (WebSocket): The WebSocket object representing the client connection.
        dashboard_handler: An object handling the dashboard connection.
        selected_datasets_option (dict): A dictionary containing the dataset filtering options.
    Notes:
        This function creates two tasks: one to process the data and another to wait for a new request from the client.
        It then waits for the first task to complete and cancels the other task.
        If the completed task is the data processing task, it sends the result to the client.
        If the completed task is the new request task, it recursively calls itself with the new request because if we receive a new request from the client
        that means we need to immediatly cancel the previous task and start a new one.
    Raises:
        Exception: If an error occurs while processing the data or handling the client request.
    """

    # we either process the dataset the user asked, or cancel it if user sends a cancel signal
    process_data_task = asyncio.create_task(
        process_data(dashboard_handler, selected_datasets_option, websocket.client)
    )
    trigger_new_task = asyncio.create_task(
        websocket.receive_json(), name="trigger_new_process"
    )
    done, pending = await asyncio.wait(
        [process_data_task, trigger_new_task], return_when=asyncio.FIRST_COMPLETED
    )
    # no matter which tasks are pending, just cancel them
    for task in pending:
        task.cancel()
    # we are guaranteed that the set contains a single element with the completed task
    completed_task = done.pop()
    if completed_task.get_name() == "trigger_new_process":
        logger.info(f"client {websocket.client} triggered new process")
        await handle_client_request(
            websocket, dashboard_handler, completed_task.result()
        )
    else:
        await websocket.send_json(completed_task.result())
        # setting delay to 0 provides an optimized path to allow other tasks to run
        # check: https://docs.python.org/3/library/asyncio-task.html#sleeping
        await asyncio.sleep(0)


async def error_pagination(dashboard_handler, dataset, page_number):
    offset = (page_number - 1) * dashboard_handler.cfg.error_page_size
    # retrieve the errors directly from sqlite db.
    async with dashboard_handler.db.execute(
        "SELECT scene, stage, message FROM process_logs WHERE dataset = ? AND state = 'failed' ORDER BY stage LIMIT ? OFFSET ?",
        (dataset, dashboard_handler.cfg.error_page_size, offset),
    ) as cursor:
        return await cursor.fetchall()
