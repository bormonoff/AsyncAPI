from fastapi import FastAPI

from api.app import app as api_app


def get_app() -> FastAPI:
    server = FastAPI(title="Async API", root_path="", docs_url="/docs")

    server.mount("/api", api_app)

    return server


app = get_app()
