from fastapi_users.exceptions import UserNotExists
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from auth.auth_manager import UserManager
from auth.auth_models import User
from database import async_session_maker
from utilties.password_manager import PasswordManager


async def authenticate_service(email: str, password: str) -> bool | None:
    # Get user by email
    db = SQLAlchemyUserDatabase(async_session_maker(), User)
    password_helper = PasswordManager().password_helper
    user_manager = UserManager(db, password_helper)

    try:
        user_taken = await user_manager.get_by_email(email)

        if not user_taken:
            password_helper.hash(password)
            # raise exceptions.UserNotExists()

        print(user_taken)
    except UserNotExists:
        # Run the hasher to mitigate timing attack
        # Inspired from Django: https://code.djangoproject.com/ticket/20760
        return False

    verified, updated_password_hash = password_helper.verify_and_update(
        password, user_taken.hashed_password
    )
    if not verified:
        return False

    if user_taken.role_id != 3:
        return False

    return None
