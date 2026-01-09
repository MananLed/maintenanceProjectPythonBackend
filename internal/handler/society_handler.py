from fastapi import APIRouter, Depends, Query
from typing import Annotated
from http import HTTPStatus
from uuid import UUID
from internal.models.user import UserRole
from internal.dto.user import OfficerDetails, SignInInput
from internal.response.response import Response
from internal.dependencies.dependencies import sqs_client
from internal.utils.jwt import verify_jwt
from internal.dependencies.authorization import require_roles
from internal.service import society_service_instance, user_service_instance
from internal.constants.constants import *
import json


society_router = APIRouter(dependencies=[Depends(verify_jwt), Depends(require_roles(UserRole.ROLEADMIN))])


@society_router.get("/society/residents")
async def get_residents():

    residents = await society_service_instance.get_all_users_by_role(
        UserRole.ROLERESIDENT
    )

    return Response.success_response(
        residents, "Residents fetched successfully", HTTPStatus.OK
    )


@society_router.get("/society/officers")
async def get_officers():

    officers = await society_service_instance.get_all_users_by_role(
        UserRole.ROLEOFFICER
    )

    return Response.success_response(
        officers, "Officers fetched successfully", HTTPStatus.OK
    )


@society_router.delete("/credentials/officer")
async def delete_officer(id: Annotated[UUID, Query()]):
    
    await society_service_instance.delete_user(id, UserRole.ROLEOFFICER)
    
    return Response.success_response(None, "Officer deleted successfully", HTTPStatus.OK)


@society_router.delete("/credentials/resident")
async def delete_resident(id: Annotated[UUID, Query()]):

    await society_service_instance.delete_user(id, UserRole.ROLERESIDENT)
    msg_body = {
        "userId": str(id)
    }
    sqs_client.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(msg_body)
    )
    
    return Response.success_response(None, "Resident deleted successfully", HTTPStatus.OK)


@society_router.post("/officers")
async def add_officer(officer_details_input: OfficerDetails):

    new_officer = SignInInput(
        first_name="xxxxxx",
        middle_name="",
        last_name="xxxxxx",
        mobile_number="9876543210",
        email=officer_details_input.email,
        flat="001",
        password=officer_details_input.password,
    )

    await user_service_instance.add_user(new_officer, True)

    return Response.success_response(
        None, "Officer created successfully", HTTPStatus.CREATED
    )


@society_router.get("/society/residents/count")
async def get_resident_count():

    residents = await society_service_instance.get_all_users_by_role(
        UserRole.ROLERESIDENT
    )

    residents_count = len(residents)

    return Response.success_response(
        residents_count, "Residents count fetched successfully", HTTPStatus.OK
    )


@society_router.get("/society/officers/count")
async def get_officer_count():

    officers = await society_service_instance.get_all_users_by_role(
        UserRole.ROLEOFFICER
    )

    officers_count = len(officers)

    return Response.success_response(
        officers_count, "Officers count fetched successfully", HTTPStatus.OK
    )
