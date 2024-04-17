from fastapi import FastAPI
from server.configuration.server import Server
from fastapi.middleware.cors import CORSMiddleware


def create_app(_=None) -> FastAPI:
    app = FastAPI(openapi_url="/auto_layout_dev/v1/openapi.json", docs_url="/auto_layout_dev/v1/docs")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    return Server(app).get_app()
