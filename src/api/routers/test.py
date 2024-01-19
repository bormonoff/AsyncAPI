from http import HTTPStatus

from fastapi import APIRouter

router = APIRouter(prefix="/test")


@router.get("/check/")
async def check():
    """Handler for testing FastAPI"""

    return HTTPStatus.OK
