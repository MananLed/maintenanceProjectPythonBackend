from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from internal.errors.base_exception import AppException
from internal.response.response import Response
from internal.handler.user_handler import user_router
from internal.handler.auth_handler import auth_router
from internal.handler.society_handler import society_router
from internal.handler.feedback_handler import feedback_router
from internal.handler.notice_handler import notice_router
from internal.handler.invoice_handler import invoice_router
from internal.handler.request_handler import request_router

app = FastAPI()

origins = ["*"]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(society_router)
app.include_router(feedback_router)
app.include_router(notice_router)
app.include_router(invoice_router)
app.include_router(request_router)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=Response.error_response(
            error_code=exc.error_code,
            message=exc.detail,
        ),
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=Response.error_response(
            error_code="SYS_001",
            message=exc.detail,
        ),
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=Response.error_response(
            error_code="SYS_001",
            message="Internal server error",
        ),
    )

