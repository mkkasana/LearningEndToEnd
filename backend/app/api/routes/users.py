import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.exceptions import EmailAlreadyExistsError, PermissionDeniedError
from app.schemas.common import Message
from app.schemas.user import (
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.services.item_service import ItemService
from app.services.user_service import UserService
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    user_service = UserService(session)
    users, count = user_service.get_users(skip=skip, limit=limit)
    return UsersPublic(data=users, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user_service = UserService(session)
    
    if user_service.email_exists(user_in.email):
        raise EmailAlreadyExistsError()

    user = user_service.create_user(user_in)
    
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """
    user_service = UserService(session)
    
    if user_in.email:
        if user_service.email_exists(user_in.email, exclude_user_id=current_user.id):
            raise EmailAlreadyExistsError()
    
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    user_service = UserService(session)
    
    if not user_service.verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    
    user_service.update_password(current_user, body.new_password)
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise PermissionDeniedError("Super users are not allowed to delete themselves")
    
    user_service = UserService(session)
    user_service.delete_user(current_user)
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    Creates both User and Person records.
    """
    from datetime import datetime
    
    from app.schemas.person import PersonCreate
    from app.services.person.gender_service import GenderService
    from app.services.person.person_service import PersonService
    
    user_service = UserService(session)
    gender_service = GenderService(session)
    person_service = PersonService(session)
    
    # Check if email already exists
    if user_service.email_exists(user_in.email):
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    
    # Get gender by code
    gender = gender_service.get_gender_by_code(user_in.gender)
    if not gender:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid gender: {user_in.gender}. Must be MALE or FEMALE",
        )
    
    # Parse date of birth
    try:
        dob = datetime.strptime(user_in.date_of_birth, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD",
        )
    
    # Create full_name from first, middle, last names
    full_name_parts = [user_in.first_name]
    if user_in.middle_name:
        full_name_parts.append(user_in.middle_name)
    full_name_parts.append(user_in.last_name)
    full_name = " ".join(full_name_parts)
    
    # Create user
    user_create = UserCreate(
        email=user_in.email,
        password=user_in.password,
        full_name=full_name,
        is_active=True,
        is_superuser=False,
    )
    user = user_service.create_user(user_create)
    
    # Create person
    person_create = PersonCreate(
        user_id=user.id,
        first_name=user_in.first_name,
        middle_name=user_in.middle_name,
        last_name=user_in.last_name,
        gender_id=gender.id,
        date_of_birth=dob,
    )
    person_service.create_person(person_create)
    
    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user_service = UserService(session)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user == current_user:
        return user
    
    if not current_user.is_superuser:
        raise PermissionDeniedError()
    
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    user_service = UserService(session)
    db_user = user_service.get_user_by_id(user_id)
    
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    
    if user_in.email:
        if user_service.email_exists(user_in.email, exclude_user_id=user_id):
            raise EmailAlreadyExistsError()

    db_user = user_service.update_user(db_user, user_in)
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user_service = UserService(session)
    item_service = ItemService(session)
    
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user == current_user:
        raise PermissionDeniedError("Super users are not allowed to delete themselves")
    
    # Delete user's items first
    item_service.delete_items_by_owner(user_id)
    
    # Delete user
    user_service.delete_user(user)
    return Message(message="User deleted successfully")
