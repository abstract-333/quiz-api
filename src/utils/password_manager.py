from typing import Union
from fastapi_users import InvalidPasswordException
from fastapi_users.password import PasswordHelper
from passlib.context import CryptContext
from auth.models import User
from auth.schemas import UserCreate


class PasswordManager:
    _context = CryptContext(schemes=["argon2"], deprecated="auto")
    password_helper = PasswordHelper(_context)

    def validate_password(password: str,
                          user: Union[UserCreate, User], ):
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )
