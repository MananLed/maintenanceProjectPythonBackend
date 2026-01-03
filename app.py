from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from internal.handler.user_handler import user_router
from internal.handler.auth_handler import auth_router
from internal.handler.society_handler import society_router
from internal.handler.feedback_handler import feedback_router
from internal.handler.notice_handler import notice_router


app = FastAPI()

origins = ["*"]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(society_router)
app.include_router(feedback_router)
app.include_router(notice_router)

# @app.post("/user")
# async def create_user(user_input: SignUpInput):
#     user = User(**user_input.model_dump())
#     return {
#         "user_made": f"{user}"
#     }


# @app.post("/notice")
# async def create_notice(notice_input: NoticeInput):
#     now = datetime.utcnow()

#     notice = Notice(
#         **notice_input.model_dump(),
#         date_issued=now,
#         month=now.month,
#         year=now.year,
#     )

#     return {"notice": f"{notice}"}


# @app.post("/feedback")
# async def create_feedback(feedback: FeedbackInput):
#     return {"status": f"feedback with {feedback} created successfully"}


# @app.post("/invoice")
# async def create_invoice(invoice_input: InvoiceInput):
#     now = datetime.utcnow()

#     invoice = Invoice(
#         **invoice_input.model_dump(),
#         month = now.month, 
#         year = now.year,
#     )

#     return {"invoice": f"{invoice}"}


# @app.post("/request")
# async def create_request(request: ServiceRequestInput):
#     return {"status": f"service request with {request.time_slot} created successfully"}
