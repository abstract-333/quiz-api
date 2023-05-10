from enum import Enum


class ErrorCode(str, Enum):
    REGISTER_INVALID_PASSWORD = "REGISTER_INVALID_PASSWORD"
    REGISTER_USER_ALREADY_EXISTS = "REGISTER_USER_ALREADY_EXISTS"
    OAUTH_NOT_AVAILABLE_EMAIL = "OAUTH_NOT_AVAILABLE_EMAIL"
    OAUTH_USER_ALREADY_EXISTS = "OAUTH_USER_ALREADY_EXISTS"
    LOGIN_BAD_CREDENTIALS = "LOGIN_BAD_CREDENTIALS"
    LOGIN_USER_NOT_VERIFIED = "LOGIN_USER_NOT_VERIFIED"
    RESET_PASSWORD_INVALID_PASSWORD = "RESET_PASSWORD_INVALID_PASSWORD"
    RESET_PASSWORD_BAD_TOKEN = "RESET_PASSWORD_BAD_TOKEN"
    VERIFY_USER_BAD_TOKEN = "VERIFY_USER_BAD_TOKEN"
    VERIFY_USER_ALREADY_VERIFIED = "VERIFY_USER_ALREADY_VERIFIED"
    UPDATE_USER_EMAIL_ALREADY_EXISTS = "UPDATE_USER_EMAIL_ALREADY_EXISTS"
    UPDATE_USER_INVALID_PASSWORD = "UPDATE_USER_INVALID_PASSWORD"
    USER_NOT_EXISTS = "USER_NOT_EXISTS"
    USER_INACTIVE = "USER_INACTIVE"
    USER_NOT_AUTHENTICATED = "USER_NOT_AUTHENTICATED"
    USER_NOT_ADMIN_SUPERVISOR = "USER_NOT_ADMIN_SUPERVISOR"
    QUIZ_DUPLICATED = "QUIZ_DUPLICATED"
