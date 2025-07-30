# starlette-rfc7807

A simple middleware and exception class to enable any Starlette (including FastAPI) project to always return an https://datatracker.ietf.org/doc/html/rfc7807 formatted response.


## Example Use

```python
import uvicorn
from fastapi import FastAPI, HTTPException
from starlette_rfc7807.middleware import http_exception_handler, ProblemMiddleware
from loguru import logger

from myservice.routers import health



def get_application() -> FastAPI:
    logger.info("Creating FastAPI application")

    application = FastAPI()
    # overwrite the default http exception handler
    application.add_exception_handler(HTTPException, http_exception_handler)  
    # your other middleware
    application.add_middleware(SentryMiddleware)
    # must be last
    application.add_middleware(ProblemMiddleware)

    application.include_router(health.router) # example route

    return application


app = get_application()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
```