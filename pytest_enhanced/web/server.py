import uvicorn
from .api import app

def run_server(host: str = "127.0.0.1", port: int = 8000):
    """
    Starts and runs an ASGI server using Uvicorn.

    This function is used to run an ASGI application on the specified host and port,
    providing network availability for client requests. It utilizes Uvicorn as the
    ASGI server implementation.

    :param host: Host address for the server, defaults to "127.0.0.1".
    :param port: Port number for the server, defaults to 8000.
    :return: None.
    """
    uvicorn.run(app, host=host, port=port)
