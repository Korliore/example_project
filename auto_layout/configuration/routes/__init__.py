from server.configuration.routes.routes import Routes
from server.internal.routes import route
from server.internal.routes import auth

__routes__ = Routes(routes=(route.router, auth.router))
