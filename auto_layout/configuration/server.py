from fastapi import FastAPI
from server.configuration.routes import __routes__


class Server:

    __app: FastAPI

    def __init__(self, app: FastAPI):
        self.__app = app
        self.__register_routers(app=app)

    def get_app(self) -> FastAPI:

        return self.__app

    @staticmethod
    def __register_events(app):
        ...

    @staticmethod
    def __register_routers(app):
        __routes__.register_routes(app)


