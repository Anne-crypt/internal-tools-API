from fastapi import FastAPI
from collections.abc import Awaitable, Callable
from typing import cast
from starlette.requests import Request
from starlette.responses import Response
from app.api.v1.endpoints.tool import router as tool_router
from importlib import import_module
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    validation_exception_handler,
    custom_http_exception_handler,
    global_exception_handler,
)

app = FastAPI(
    title="Internal Tools Management API",
    description="API de gestion et d'optimisation des coûts des outils internes",
    version="1.0.0",
)

analytics_router = import_module("app.api.v1.endpoints.anatytics").router

ExceptionHandler = Callable[[Request, Exception], Response | Awaitable[Response]]

# On écrase les réponses d'erreurs par défaut de FastAPI par les tiennes :
app.add_exception_handler(
    RequestValidationError, cast(ExceptionHandler, validation_exception_handler)
)  # type: ignore[arg-type]
app.add_exception_handler(
    StarletteHTTPException, cast(ExceptionHandler, custom_http_exception_handler)
)  # type: ignore[arg-type]
app.add_exception_handler(Exception, global_exception_handler)

# Inclusion des routes avec le préfixe demandé /api/tools
app.include_router(tool_router, prefix="/api/tools", tags=["Tools"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])


@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Welcome to Internal Tools Management API"}
