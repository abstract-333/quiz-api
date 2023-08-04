import re
from typing import Union
from fastapi_users import InvalidPasswordException
from fastapi_users.password import PasswordHelper
from passlib.context import CryptContext

from api.auth.auth_models import User
from api.auth.auth_schemas import UserCreate


class PasswordManager:
    _context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
    password_helper = PasswordHelper(_context)

    @staticmethod
    def validate_password(password: str,
                          user: Union[UserCreate, User], ):
        uppercase_pattern = re.compile(r'[A-Z]')
        lowercase_pattern = re.compile(r'[a-z]')
        digit_pattern = re.compile(r'\d')
        special_pattern = re.compile(r'[!@#$%^&*()_+{}|\[\]:";<>,.?/~`]')

        # Check password length
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )

        # check if does not contain user's email
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )

        # Check if password contains uppercase letters
        if not uppercase_pattern.search(password):
            raise InvalidPasswordException(
                reason="Password must contain at least one uppercase letter"
            )

            # Check if password contains lowercase letters
        if not lowercase_pattern.search(password):
            raise InvalidPasswordException(
                reason="Password must contain at least one lowercase letter"
            )

            # Check if password contains digits
        if not digit_pattern.search(password):
            raise InvalidPasswordException(
                reason="Password must contain at least one digit"
            )

            # Check if password contains special characters
        if not special_pattern.search(password):
            raise InvalidPasswordException(
                reason="Password must contain at least one special character"
            )
