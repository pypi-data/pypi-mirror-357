import asyncio
import logging
import traceback
from pathlib import Path

import aioboto3
import aiofiles.os
from aiobotocore.session import ClientCreatorContext
from argconf import argconf_parse
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential
from tqdm import tqdm
from wai import get_scene_frame_names, load_data
from wai.io import set_processing_state
from wai_processing import WAI_PROC_CONFIG_PATH

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("copy_to_s3")


async def async_recursive_scandir(path: str):
    """Recursively scans a directory asynchronously."""
    entries = await aiofiles.os.scandir(path)
    for entry in entries:
        if entry.is_dir():
            async for sub_entry in async_recursive_scandir(entry.path):
                yield sub_entry
        elif entry.is_file():
            yield entry.path


@retry(
    wait=wait_exponential(min=1, max=8),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logger=logger, log_level=logging.INFO),
)
async def check_if_valid_aws_credentials(s3_client):
    """Raises a RuntimeError if the AWS credentials are invalid or incomplete."""
    try:
        # Attempt to list S3 buckets
        await s3_client.list_buckets()
        logger.info("AWS credentials are valid.")
    except (NoCredentialsError, PartialCredentialsError, ClientError):
        # Re-raise with more context
        raise RuntimeError("AWS credentials are invalid or incomplete.")


@retry(
    wait=wait_exponential(min=1, max=8),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logger=logger, log_level=logging.INFO),
)
async def get_bucket_content(s3_client, bucket_name, folder):
    """
    Retrieves the contents of an S3 bucket folder.
    This function uses the `list_objects_v2` paginator to retrieve the contents of the specified S3 bucket folder.
    It returns a dictionary where the keys are the object keys and the values are tuples containing the object size and last modified date.
    Args:
        s3_client: An S3 client object.
        bucket_name (str): The name of the S3 bucket.
        folder (str): The prefix of the folder to retrieve contents from.
    Returns:
        dict: A dictionary containing the contents of the S3 bucket folder.
    Raises:
        botocore.exceptions.ClientError: If an error occurs while retrieving the bucket contents.
    """
    bucket_contents = {}
    paginator = s3_client.get_paginator("list_objects_v2")
    async for result in paginator.paginate(Bucket=bucket_name, Prefix=folder):
        for c in result.get("Contents", []):
            bucket_contents[c["Key"]] = (c["Size"], c["LastModified"])
    return bucket_contents


@retry(
    wait=wait_exponential(min=1, max=8),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logger=logger, log_level=logging.INFO),
)
async def s3_upload_file(s3_client, src_path, bucket_name, dest_path, semaphore):
    """
    Uploads a file to an S3 bucket.

    This function uses the `upload_file` method of the S3 client to upload a file to the specified S3 bucket.
    It acquires the semaphore before uploading the file to ensure that the upload is done in a thread-safe manner.

    Args:
        s3_client: An S3 client object.
        src_path (str): The path to the local file to be uploaded.
        bucket_name (str): The name of the S3 bucket to upload the file to.
        dest_path (str): The key of the object in the S3 bucket where the file will be uploaded.
        semaphore: A semaphore object used to synchronize access to the S3 client.

    Returns:
        None

    Raises:
        botocore.exceptions.ClientError: If an error occurs while uploading the file.
    """
    async with semaphore:
        logger.debug(f"Uploading {src_path} to s3://{bucket_name}/{dest_path}")
        await s3_client.upload_file(src_path, bucket_name, dest_path)


async def copy_file_to_s3(
    semaphore: asyncio.Semaphore,
    s3_client: ClientCreatorContext,
    src_path: str,
    bucket_name: str,
    dest_path: str,
    bucket_content,
):
    """
    Asynchronously uploads a source file to an S3 bucket if it is missing or outdated.

    :param semaphore: An asyncio.Semaphore object to limit the number of concurrent uploads.
    :param s3_client: An S3 client object for interacting with the AWS S3 service.
    :param src_path (str): The local file path of the source file to be uploaded.
    :param bucket_name (str): The name of the S3 bucket where the file will be uploaded.
    :param dest_path (str): The destination path within the S3 bucket for the uploaded file.
    """

    if await file_needs_upload(src_path, dest_path, bucket_content):
        await s3_upload_file(s3_client, src_path, bucket_name, dest_path, semaphore)
    else:
        logger.debug(
            f"Skipping {src_path}, already up-to-date on s3://{bucket_name}/{dest_path}"
        )


async def file_needs_upload(src_path, dest_path, bucket_content):
    """
    Determines whether a file needs to be uploaded to S3.

    This function checks if the file already exists in the S3 bucket and if its size and last modified timestamp match the local file.
    If the file does not exist in the bucket or its metadata has changed, it returns True indicating that the file needs to be uploaded.

    Args:
        src_path (str): The path to the local file.
        dest_path (str): The key of the object in the S3 bucket where the file will be uploaded.
        bucket_content (dict): A dictionary containing the contents of the S3 bucket.

    Returns:
        bool: True if the file needs to be uploaded, False otherwise.
    """

    # lookup if bucket already contains the file, in that case check size and timestamp
    s3_size, s3_last_modified = bucket_content.get(dest_path, (None, None))

    if s3_size and s3_last_modified:
        src_metadata = await aiofiles.os.stat(src_path)
        src_size = src_metadata.st_size
        src_last_modified = src_metadata.st_mtime

        return src_size != s3_size or src_last_modified > s3_last_modified.timestamp()

    return True


def get_rel_paths_frame_modalites(cfg, scene_meta) -> list[str]:
    """Returns a list of relative paths for frame modalities to be transferred."""
    rel_paths = set()

    for modality, modality_meta in scene_meta["frame_modalities"].items():
        if (
            cfg.frame_modalities_to_transfer != "all"
            and modality not in cfg.frame_modalities_to_transfer
        ):
            continue

        # Add the relative directory path of the respective frame modality
        rel_paths.add(
            str(Path(scene_meta["frames"][0][modality_meta["frame_key"]]).parent)
        )

    return list(rel_paths)


def get_rel_paths_scene_modalites(cfg, scene_meta) -> list[str]:
    """Returns a list of relative paths for scene modalities to be transferred."""
    rel_paths = set()

    for modality, modality_meta in scene_meta["scene_modalities"].items():
        if (
            cfg.scene_modalities_to_transfer != "all"
            and modality not in cfg.scene_modalities_to_transfer
        ):
            continue

        # Add the relative file or directory path of the respective scene modality
        if "path" in modality_meta:
            rel_paths.add(modality_meta["path"])
        elif "scene_key" in modality_meta:
            rel_paths.add(modality_meta["scene_key"])
        else:
            for v in modality_meta.values():
                if "path" in v:
                    rel_paths.add(v["path"])
                elif "scene_key" in v:
                    rel_paths.add(v["scene_key"])

    return list(rel_paths)


async def copy_scene_to_s3(
    s3_client: ClientCreatorContext, cfg, scene_name: str, semaphore: asyncio.Semaphore
):
    """Asynchronously copies a scene to an S3 bucket by creating a separate transfer task for each individual file."""
    src_root = Path(cfg.root) / scene_name
    dest_root = Path(cfg.s3_prefix) / scene_name

    rel_paths = []

    if (
        cfg.frame_modalities_to_transfer == "all"
        and cfg.scene_modalities_to_transfer == "all"
    ):
        rel_paths.append("")
    else:
        # Choose subdirectories based on requested frame and/or scene modalities
        scene_meta = load_data(src_root / "scene_meta.json")
        if (src_root / "scene_meta_distorted.json").exists():
            scene_meta_distorted = load_data(src_root / "scene_meta_distorted.json")
        else:
            scene_meta_distorted = None

        # Add relative paths for frame modalities (either a single file or the root directory)
        if cfg.frame_modalities_to_transfer == "all" or (
            isinstance(cfg.frame_modalities_to_transfer, list)
            and len(cfg.frame_modalities_to_transfer) > 0
        ):
            rel_paths += get_rel_paths_frame_modalites(cfg, scene_meta)
            if scene_meta_distorted:
                rel_paths += get_rel_paths_frame_modalites(cfg, scene_meta_distorted)

        # Add relative paths for scene modalities (either a single file or the root directory)
        if cfg.scene_modalities_to_transfer == "all" or (
            isinstance(cfg.scene_modalities_to_transfer, list)
            and len(cfg.scene_modalities_to_transfer) > 0
        ):
            rel_paths += get_rel_paths_scene_modalites(cfg, scene_meta)
            if scene_meta_distorted:
                rel_paths += get_rel_paths_scene_modalites(cfg, scene_meta_distorted)

        # Additionally, also transfer the scene meta and process log json files
        rel_paths += [
            str(file.relative_to(src_root)) for file in src_root.glob("*.json")
        ]

    # get all the files from the given bucket 'folder' (folder associated with the current scene)
    bucket_content = await get_bucket_content(
        s3_client, cfg.bucket_name, str(dest_root)
    )

    async with asyncio.TaskGroup() as task_group:
        for path in rel_paths:
            src_path = src_root / path
            src_path_str = str(src_path)
            dest_path = dest_root / path

            if await aiofiles.os.path.isfile(src_path_str):
                # Process individual file or symbolic link
                task_group.create_task(
                    copy_file_to_s3(
                        semaphore,
                        s3_client,
                        src_path_str,
                        cfg.bucket_name,
                        str(dest_path),
                        bucket_content,
                    )
                )

            elif await aiofiles.os.path.isdir(src_path_str):
                # Process each file within the directory separately
                async for file_path in async_recursive_scandir(src_path_str):
                    if await aiofiles.os.path.isfile(file_path):
                        task_group.create_task(
                            copy_file_to_s3(
                                semaphore,
                                s3_client,
                                str(file_path),
                                cfg.bucket_name,
                                str(dest_path / Path(file_path).relative_to(src_path)),
                                bucket_content,
                            )
                        )


async def process_scene(s3_client, cfg, scene_name, semaphore) -> bool:
    logger.info(f"Processing: {scene_name}")
    scene_root = Path(cfg.root, scene_name)
    set_processing_state(scene_root, "copy_to_s3", "running")
    try:
        # Check if AWS credentials are valid before starting to process the scene
        await check_if_valid_aws_credentials(s3_client)
        await copy_scene_to_s3(s3_client, cfg, scene_name, semaphore)
        set_processing_state(scene_root, "copy_to_s3", "finished")
        # Copy final _process_log.json
        await s3_upload_file(
            s3_client=s3_client,
            src_path=str(Path(cfg.root) / scene_name / "_process_log.json"),
            bucket_name=cfg.bucket_name,
            dest_path=str(Path(cfg.s3_prefix) / scene_name / "_process_log.json"),
            semaphore=semaphore,
        )

        logger.info(
            f"Scene '{scene_name}' successfully transferred to s3://{cfg.bucket_name}/{cfg.s3_prefix}/{scene_name}"
        )
        status = True
    except Exception:
        trace_message = traceback.format_exc()
        logger.warning(
            f"Copying WAI dataset to s3://{cfg.bucket_name}/{cfg.s3_prefix} failed on scene: {scene_name}"
            f"\nError message: \n{trace_message}\n"
        )
        set_processing_state(scene_root, "copy_to_s3", "failed", message=trace_message)
        status = False

    return status


async def main():
    cfg = argconf_parse(
        str(Path(WAI_PROC_CONFIG_PATH) / "data_transfer/to_s3_default.yaml")
    )

    if cfg.get("root") is None:
        raise ValueError(
            "Specify the root via: 'python scripts/run_copy_to_s3.py root=<root_path>'"
        )

    if cfg.get("bucket_name") is None:
        raise ValueError(
            "'bucket_name' is missing in the config. Please specify the name of the S3 bucket."
        )

    if "max_concurrent_tasks" not in cfg:
        raise ValueError(
            "'max_concurrent_tasks' is missing in the config. Please specify the maximum number of concurrent tasks."
        )

    if not isinstance(cfg.get("max_concurrent_tasks"), int):
        raise ValueError("'max_concurrent_tasks' is expected to be an integer value.")

    cfg.s3_prefix = cfg.get("s3_prefix") or ""
    cfg.s3_wai_dataset_name = cfg.get("s3_wai_dataset_name") or Path(cfg.root).name
    cfg.s3_prefix = f"{cfg.s3_prefix}/{cfg.s3_wai_dataset_name}"

    for key in ["frame_modalities_to_transfer", "scene_modalities_to_transfer"]:
        if not (cfg[key] == "all" or isinstance(cfg[key], list)):
            raise ValueError(
                f"Expected '{key}' to be a list of strings or the string 'all', but received {cfg[key]}."
            )

    scene_names = get_scene_frame_names(cfg)
    logger.info(f"Copying {len(scene_names)} scenes to s3.")
    session = aioboto3.Session()
    success_count = 0

    # Create a semaphore to control the number of concurrent tasks
    semaphore = asyncio.Semaphore(cfg.max_concurrent_tasks)

    async with session.client("s3", region_name=cfg.get("region_name")) as s3_client:
        for scene_name in tqdm(scene_names):
            status = await process_scene(s3_client, cfg, scene_name, semaphore)
            success_count += status

    logger.info(
        f"{success_count} / {len(scene_names)} scenes successfully transferred to s3."
    )


if __name__ == "__main__":
    asyncio.run(main())
