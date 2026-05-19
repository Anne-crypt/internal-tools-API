from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import exc as sqlalchemy_exc
from starlette.exceptions import HTTPException as StarletteHTTPException


async def validation_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Intercepte les erreurs de validation (HTTP 400) et les formate selon la consigne."""

    if not isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Validation failed", "message": str(exc)},
        )

    details = {}
    for error in exc.errors():
        # Extrait le nom du champ qui a échoué (ex: "name", "monthly_cost")
        field_name = error["loc"][-1] if error["loc"] else "body"
        details[str(field_name)] = error["msg"]

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Validation failed", "details": details},
    )


async def custom_http_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Intercepte les HTTP 404 et autres codes levés manuellement."""
    if not isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error", "message": str(exc)},
        )

    # Format personnalisé pour le 404 introuvable
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        # On essaie de dynamiser le message si l'ID est disponible, sinon message standard
        tool_id = request.path_params.get("tool_id", "requested")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "Tool not found",
                "message": f"Tool with ID {tool_id} does not exist"
                if "introuvable" in str(exc.detail).lower()
                or "not found" in str(exc.detail).lower()
                else str(exc.detail),
            },
        )

    # Format générique pour les autres HTTPException (comme le 400 levé par le routeur)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Bad request" if exc.status_code == 400 else "Error",
            "message": str(exc.detail),
        },
    )


async def global_exception_handler(request: Request, exc: Exception):
    """Intercepte TOUTES les autres erreurs non gérées (HTTP 500 / Crash DB)."""
    # logger l'erreur ici pour le debug interne : print(f"CRASH: {exc}")

    print(f"--- CRASH DETECTED --- Type: {type(exc)} | Message: {str(exc)}")

    error_msg = str(exc)

    if (
        isinstance(exc, ValueError)
        or "coût" in error_msg.lower()
        or "supérieur" in error_msg.lower()
        or "existe déjà" in error_msg.lower()
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Bad request", "message": error_msg},
        )
    if "connection" in error_msg.lower() or "dialing" in error_msg.lower():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "message": "Database connection failed",
            },
        )

    if isinstance(exc, sqlalchemy_exc.DBAPIError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "message": "Database error occurred",
            },
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
        },
    )
