class DuplicatedQuestionException(Exception):
    """QUESTION_DUPLICATED"""
    pass


class UserNotAdminSupervisor(Exception):
    """USER_NOT_ADMIN_SUPERVISOR"""
    pass


class OutOfSectionIdException(Exception):
    """OUT_SECTION_ID_EXCEPTION"""
    pass


class AnswerNotIncluded(Exception):
    """ANSWER_NOT_INCLUDED_IN_CHOICES"""
    pass


class NumberOfChoicesNotFour(Exception):
    """NUMBER_OF_CHOICES_NOT_EQUAL_FOUR"""
    pass


class FeedbackAlreadySent(Exception):
    """FEEDBACK_ALREADY_SENT_FOR_THIS_QUESTION"""
    pass


class QuestionNotExists(Exception):
    """QUESTION_NOT_EXISTS"""
    pass


class QuestionNotEditable(Exception):
    """NOT_ALLOWED_EDIT_QUESTION"""
    pass


class QuestionsInvalidNumber(Exception):
    """QUESTIONS_INVALID_NUMBER"""
    pass


class RatingException(Exception):
    """RATING_EXCEPTION"""
    pass


class DuplicatedTitle(Exception):
    """DUPLICATED_TITLE"""
    pass


class InvalidPage(Exception):
    """INVALID_PAGINATION"""
    pass


class FeedbackNotExists(Exception):
    """FEEDBACK_NOT_EXISTS"""
    pass


class FeedbackNotEditable(Exception):
    """FEEDBACK_NOT_EDITABLE_NOW"""
    pass


class NotAllowed(Exception):
    """NOT_ALLOWED"""
    pass


class NotAllowedDeleteBeforeTime(Exception):
    """NOT_ALLOWED_DELETE_BEFORE_TIME"""
    pass


class NotUser(Exception):
    """ONLY_USER_IS_ALLOWED"""
    pass
