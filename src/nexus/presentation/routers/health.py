from fastapi import APIRouter, status
from pydantic import BaseModel


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


class HealthResponse(BaseModel):
    status: str


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
