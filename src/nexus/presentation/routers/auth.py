
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from nexus.application.users.authenticate_user import (
    AuthenticateUser,
    InvalidCredentialsError,
)
from nexus.application.users.errors import EmailAlreadyRegisteredError
from nexus.application.users.register_user import RegisterUser
from nexus.infrastructure.database.repositories.user_repository import (
    SqlAlchemyUserRepository,
)
from nexus.presentation.dependencies.db import get_db_session


router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_and_validate_email(cls, value: str) -> str:
        value = value.strip().lower()

        if (
            not value
            or "@" not in value
            or value.startswith("@")
            or value.endswith("@")
            or "." not in value.rsplit("@", 1)[-1]
        ):
            raise ValueError("A valid email address is required.")

        return value


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: UUID
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    session: Session = Depends(get_db_session),
) -> UserResponse:
    repository = SqlAlchemyUserRepository(session)

    try:
        user = RegisterUser(repository).execute(
            email=request.email,
            password=request.password,
        )
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        # Handles concurrent registrations that pass the initial email check.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from exc

    return UserResponse(id=user.id, email=user.email)


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    session: Session = Depends(get_db_session),
) -> TokenResponse:
    repository = SqlAlchemyUserRepository(session)

    try:
        token = AuthenticateUser(repository).execute(
            email=request.email,
            password=request.password,
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return TokenResponse(access_token=token)
