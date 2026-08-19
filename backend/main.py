from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time

from backend.app.main import app as pricepilot_app
from backend.utils.logger import logger

app = FastAPI(title="PricePilot AI - Dynamic Pricing Optimization & Revenue Intelligence System", description="FastAPI Backend for PricePilot AI dynamic pricing and demand forecasting", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        logger.info(f"{request.method} {request.url.path} {response.status_code} {(time.time()-start)*1000:.2f}ms")
        return response

app.add_middleware(StructuredLoggingMiddleware)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"success": False, "message": exc.detail})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"success": False, "message": "Validation error", "error": str(exc.errors())})

for route in pricepilot_app.routes:
    app.routes.append(route)

@app.get("/health", tags=["system"])
def health_check():
    return {"status": "healthy", "version": "3.0.0"}

@app.get("/ready", tags=["system"])
def readiness_check():
    return {"status": "ready"}
