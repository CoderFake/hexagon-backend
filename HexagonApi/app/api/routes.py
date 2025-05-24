import logging
import secrets
from typing import Annotated

from app.config import ApplicationSettings, Environment
from app.model.errors import Errors
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .route.front import me
from .route.internal import docs
from .shared.errors import ValidationErrorResponse, errorModel, setup_handlers

security = HTTPBasic()
authError = errorModel(Errors.UNAUTHORIZED, Errors.NOT_SIGNED_UP)


def setup_api(app: FastAPI, env: Environment, logger: logging.Logger):
    """
    Configure API routing and application error handling.

    Args:
        app: Application instance.
        env: Environment object.
        logger: Logger instance.
    """
    router = APIRouter(
        prefix="",
        responses={422: dict(model=ValidationErrorResponse, description="Validation error.")},
    )

    router.include_router(
        prefix="/me",
        router=me.router,
        tags=["Me"],
        responses={
            401: dict(model=authError, description="Authentication failed."),
        },
    )


    # Set up docs authentication if needed (staging/production)
    if env.settings.docs.enabled and env.settings.docs.username:
        # Add HTTP Basic Auth to the OpenAPI schema for Swagger UI
        from fastapi.openapi.utils import get_openapi
        from fastapi.security import HTTPBasic
        
        # Add security scheme to OpenAPI
        def custom_openapi():
            if app.openapi_schema:
                return app.openapi_schema
            
            openapi_schema = get_openapi(
                title=app.title,
                version=app.version,
                description=app.description,
                routes=app.routes,
            )
            
            # Add security scheme for HTTP Basic Auth
            openapi_schema["components"]["securitySchemes"] = {
                "HTTPBasic": {
                    "type": "http",
                    "scheme": "basic"
                }
            }
            
            # Apply security to all paths
            for path in openapi_schema["paths"]:
                for method in openapi_schema["paths"][path]:
                    openapi_schema["paths"][path][method]["security"] = [{"HTTPBasic": []}]
            
            app.openapi_schema = openapi_schema
            return app.openapi_schema
        
        app.openapi = custom_openapi
        
        # Create custom docs endpoints with authentication
        @app.get("/docs", include_in_schema=False)
        async def get_docs(credentials: HTTPBasicCredentials = Depends(DocumentAuth(env.settings.docs))):
            from fastapi.openapi.docs import get_swagger_ui_html
            return get_swagger_ui_html(openapi_url="/openapi.json", title="API Documentation")
        
        @app.get("/redoc", include_in_schema=False)  
        async def get_redoc(credentials: HTTPBasicCredentials = Depends(DocumentAuth(env.settings.docs))):
            from fastapi.openapi.docs import get_redoc_html
            return get_redoc_html(openapi_url="/openapi.json", title="API Documentation")
        
        @app.get("/openapi.json", include_in_schema=False)
        async def get_openapi_json(credentials: HTTPBasicCredentials = Depends(DocumentAuth(env.settings.docs))):
            return app.openapi()

    app.include_router(router)

    setup_handlers(app, env.settings.errors, logger)


class DocumentAuth:
    """
    Basic authentication for document-related APIs.

    See also: https://fastapi.tiangolo.com/advanced/security/http-basic-auth/
    """

    def __init__(self, auth: ApplicationSettings.DocumentAuth) -> None:
        self.auth = auth
        self.encoded_username = auth.username.encode("utf-8")
        self.encoded_password = auth.password.encode("utf-8")

    def __call__(
        self, credentials: Annotated[HTTPBasicCredentials, Depends(security)]
    ) -> str:
        username = credentials.username.encode("utf-8")
        password = credentials.password.encode("utf-8")

        if not (
            secrets.compare_digest(username, self.encoded_username)
            and secrets.compare_digest(password, self.encoded_password)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )

        return credentials.username
