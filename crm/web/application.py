from importlib import metadata

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse

from rsouvenir_crm.web.api.router import api_router
from rsouvenir_crm.web.lifetime import register_shutdown_event, register_startup_event


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="rsouvenir_crm",
        version=metadata.version("rsouvenir_crm"),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Добавляем middleware для разрешения CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Разрешаем все домены
        allow_credentials=True,
        allow_methods=["*"],  # Разрешаем все HTTP методы
        allow_headers=["*"],  # Разрешаем все заголовки
    )

    # Добавляем события запуска и завершения
    register_startup_event(app)
    register_shutdown_event(app)

    # Основной маршрутизатор для API
    app.include_router(router=api_router, prefix="/api")

    return app
