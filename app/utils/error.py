"""Error handlers"""

from http import HTTPStatus

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.exceptions.auth_exceptions import (
    AuthenticationFailedException,
    InsufficientPermissionsException,
    InvalidEmailException,
    InvalidPasswordException,
    InvalidUsernameException,
    UserAlreadyExistsException,
    UserNotFoundException as AuthUserNotFoundException,
)
from app.domain.exceptions.user_exceptions import (
    UserNotFoundException as UserUserNotFoundException,
    UserAlreadyExistsException as UserUserAlreadyExistsException,
)
from app.schema.response import StandardResponse


def register_error_handlers(app) -> None:
    """Register custom error handlers with the FastAPI app"""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content=StandardResponse(success=False, message=exc.detail, payload=None).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content=StandardResponse(
                success=False,
                message="Validation error",
                payload={"errors": exc.errors()},
            ).model_dump(),
        )

    # Domain exception handlers for auth
    @app.exception_handler(AuthUserNotFoundException)
    async def auth_user_not_found_exception_handler(request, exc):
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content=StandardResponse(
                success=False, message=str(exc), payload=exc.details
            ).model_dump(),
        )

    @app.exception_handler(UserUserNotFoundException)
    async def user_user_not_found_exception_handler(request, exc):
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content=StandardResponse(
                success=False, message=str(exc), payload=None  # user_exceptions version doesn't have details
            ).model_dump(),
        )

    @app.exception_handler(UserAlreadyExistsException)
    async def auth_user_already_exists_exception_handler(request, exc):
        return JSONResponse(
            status_code=HTTPStatus.CONFLICT,
            content=StandardResponse(
                success=False, message=str(exc), payload=exc.details
            ).model_dump(),
        )

    @app.exception_handler(UserUserAlreadyExistsException)
    async def user_user_already_exists_exception_handler(request, exc):
        return JSONResponse(
            status_code=HTTPStatus.CONFLICT,
            content=StandardResponse(
                success=False, message=str(exc), payload=None  # user_exceptions version doesn't have details
            ).model_dump(),
        )

    @app.exception_handler(InvalidEmailException)
    async def invalid_email_exception_handler(request, exc):
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=StandardResponse(
                success=False, message=str(exc), payload=exc.details
            ).model_dump(),
        )

    @app.exception_handler(InvalidUsernameException)
    async def invalid_username_exception_handler(request, exc):
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=StandardResponse(
                success=False, message=str(exc), payload=exc.details
            ).model_dump(),
        )

    @app.exception_handler(InvalidPasswordException)
    async def invalid_password_exception_handler(request, exc):
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=StandardResponse(
                success=False, message=str(exc), payload=exc.details
            ).model_dump(),
        )

    @app.exception_handler(AuthenticationFailedException)
    async def authentication_failed_exception_handler(request, exc):
        return JSONResponse(
            status_code=HTTPStatus.UNAUTHORIZED,
            content=StandardResponse(
                success=False, message=str(exc), payload=exc.details
            ).model_dump(),
        )

    @app.exception_handler(InsufficientPermissionsException)
    async def insufficient_permissions_exception_handler(request, exc):
        return JSONResponse(
            status_code=HTTPStatus.FORBIDDEN,
            content=StandardResponse(
                success=False, message=str(exc), payload=exc.details
            ).model_dump(),
        )
