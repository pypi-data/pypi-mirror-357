import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from wai import WAI_MAIN_PATH
from wai.dashboard.dashboard_handler import DashboardConnectionHandler
from wai.dashboard.models import ErrorRequest, HealthCheck
from wai.dashboard.utils import error_pagination, handle_client_request

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("dashboard")

router = APIRouter()
templates = Jinja2Templates(directory=WAI_MAIN_PATH / "wai" / "dashboard" / "templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Handles the root endpoint of the application, serving the main HTML page.
    This function responds to GET requests at the root URL ("/") and returns
    an HTML page rendered from a Jinja2 template.
    :param request: The incoming HTTP request.
    :return: An HTML response generated from the "index.html" template.
    """
    return templates.TemplateResponse(request=request, name="index.html")


@router.websocket("/data")
async def get_data(
    dashboard_handler: Annotated[
        DashboardConnectionHandler, Depends(DashboardConnectionHandler)
    ],
    websocket: WebSocket,
):
    """
    Establishes a WebSocket connection to handle client requests for data and process it. The client will send request from the
    websocket connection so we always wait on the new reequest and then process the data.
    Args:
        dashboard_handler (DashboardConnectionHandler): An object handling the dashboard connection.
        websocket (WebSocket): The WebSocket object representing the client connection.
    Notes:
        This endpoint establishes a WebSocket connection with the client and listens for incoming JSON messages containing dataset filtering options. It then handles these requests by calling the `handle_client_request` function.
    Raises:
        WebSocketDisconnect: If the client disconnects from the WebSocket.
    """
    await dashboard_handler.ws_connect(websocket)
    try:
        while True:
            # Wait for a json message from the client containing which dataset to filter
            selected_datasets_option = await websocket.receive_json()
            await handle_client_request(
                websocket, dashboard_handler, selected_datasets_option
            )
    except WebSocketDisconnect as err:
        # check websocket rfc for defined status code: https://datatracker.ietf.org/doc/html/rfc6455#section-7.4.1
        if err.code == 1000:
            logger.info(f"Client {websocket.client} disconnected normally.")
        elif err.code == 1001:
            logger.info(f"Client {websocket.client} disconnected due to going away.")
        elif err.code == 1005:
            logger.error(f"Server closed the connection to client {websocket.client}.")
        else:
            logger.error(
                f"Client {websocket.client} disconnected with code {err.code}."
            )
        dashboard_handler.ws_disconnect(websocket)
        logger.error(f"Client {websocket.client} disconnected!")


@router.get("/config")
async def get_config(
    dashboard_handler: Annotated[
        DashboardConnectionHandler, Depends(DashboardConnectionHandler)
    ],
):
    """
    Returns the current configuration.
    Args:
        dashboard_handler: An object handling the dashboard connection.
    Returns:
        dict: A dictionary containing the list of available datasets and the refresh rate.
    Notes:
        This endpoint returns the list of dataset names and the refresh rate as specified in the configuration at the start of the frontend, this will be called.
    """
    return {
        "datasets": [path.stem for path in dashboard_handler.datasets],
        "refresh_rate": dashboard_handler.cfg.refresh_rate,
        "page_size": dashboard_handler.cfg.error_page_size,
    }


@router.post("/errors")
async def get_errors(
    dashboard_handler: Annotated[
        DashboardConnectionHandler, Depends(DashboardConnectionHandler)
    ],
    request: ErrorRequest,
):
    return await error_pagination(dashboard_handler, request.dataset, request.page)


@router.get(
    "/health",
    response_model=HealthCheck,
)
async def get_health() -> HealthCheck:
    """
    Endpoint to perform a healthcheck on. This endpoint can primarily be used
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        Healthcheck: Returns a JSON response with the health status

    """
    return HealthCheck(status="OK")
