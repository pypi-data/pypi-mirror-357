"""
RFC 7807 Problem middleware

Example usage:

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler() # any other exception handler
app.add_middleware(ProblemMiddleware) # must be last
"""

from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from .exception import Problem


async def http_exception_handler(request: Request, exc: HTTPException):
    """Work around Starlette's HTTPException middleware by re-raising the exception"""
    raise exc


class ProblemMiddleware(BaseHTTPMiddleware):
    """Return RFC 7807 Problem response for any exception raised"""

    async def dispatch(self, request: Request, call_next):
        """Dispatch the request to the next middleware or handler."""
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            if isinstance(e, Problem):
                return JSONResponse(
                    content=e.to_dict(),
                    status_code=e.status,
                    media_type="application/problem+json",
                )
            else:
                new_error = Problem(
                    type="urn:ldc:error:unknown",
                    title="Unknown Error",
                    status=e.status_code if hasattr(e, "status_code") else 500,
                    detail=str(e),
                    error_type=e.__class__.__name__,
                    sentry_url=e.sentry_url if hasattr(e, "sentry_url") else None,
                )

                return JSONResponse(
                    content=new_error.to_dict(),
                    status_code=new_error.status,
                    media_type="application/problem+json",
                )
