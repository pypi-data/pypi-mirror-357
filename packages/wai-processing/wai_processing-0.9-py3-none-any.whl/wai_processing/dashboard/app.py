import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from wai.dashboard.dashboard_handler import DashboardConnectionHandler
from wai.dashboard.routes import router as dashboard_router

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("dashboard")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifespan of the FastAPI application, specifically handling the setup
    and teardown of the database connection.
    This function is used to initialize resources when the application starts and
    clean them up when the application shuts down.

    More info here: https://fastapi.tiangolo.com/advanced/events/#lifespan

    :param app: The FastAPI application instance.
    """
    dashboard_handler = DashboardConnectionHandler()
    await dashboard_handler.init_db_connection()
    await dashboard_handler.db.execute("""
        CREATE TABLE IF NOT EXISTS process_logs (
            dataset TEXT,
            scene TEXT,
            stage TEXT,
            state TEXT,
            date TEXT,
            message TEXT,
            file_mtime REAL,
            PRIMARY KEY (dataset, scene, stage)
        )
        """)
    await dashboard_handler.db.commit()
    yield
    await dashboard_handler.close_db_connection()


# Initialization of app
app = FastAPI(title="wai dashboard", lifespan=lifespan)
app.include_router(dashboard_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5124, timeout_keep_alive=300)
