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
    USER_INACTIVE_OR_NOT_EXISTS = "USER_INACTIVE_OR_NOT_EXISTS"
    QUESTION_DUPLICATED = "QUESTION_DUPLICATED"
    QUESTIONS_NUMBER_INVALID = "QUESTIONS_NUMBER_INVALID"
    ANSWER_NOT_INCLUDED_IN_CHOICES = "ANSWER_NOT_INCLUDED_IN_CHOICES"
    OUT_OF_SECTION_ID = "OUT_OF_SECTION_ID"
    NUMBER_OF_CHOICES_NOT_FOUR = "NUMBER_OF_CHOICES_NOT_FOUR"
    FEEDBACK_ALREADY_SENT = "FEEDBACK_ALREADY_SENT_FOR_THIS_QUESTION"
    QUESTION_NOT_EXISTS = "QUESTION_NOT_EXISTS"
    FEEDBACK_NOT_EXISTS = "FEEDBACK_NOT_EXISTS"
    FEEDBACK_NOT_EDITABLE = "FEEDBACK_NOT_EDITABLE"
    RATING_EXCEPTION = "RATING_EXCEPTION"
    DUPLICATED_TITLE = "DUPLICATED_TITLE"
    INVALID_PAGE = "INVALID_PAGE"
    NOT_QUESTION_OWNER = "NOT_QUESTION_OWNER"

