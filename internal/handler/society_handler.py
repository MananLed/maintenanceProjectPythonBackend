from fastapi import APIRouter, Request, Depends
from internal.dto.user import OfficerDetails
from internal.utils.jwt import verify_jwt



society_router = APIRouter(dependencies=[Depends(verify_jwt)])


@society_router.get("/society/residents")
def get_residents(request: Request):
    pass


@society_router.get("/society/officers")
def get_officers():
    pass


@society_router.delete("/credentials/officer")
def delete_officer():
    pass


@society_router.delete("/credentials/resident")
def delete_resident():
    pass


@society_router.post("/officers")
def add_officer(officer_details_input: OfficerDetails):
    pass


@society_router.get("/society/residents/count")
def get_resident_count():
    pass


@society_router.get("/society/officers/count")
def get_officer_count():
    pass
