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


class RatingException(Exception):
    """RATING_EXCEPTION"""
    pass


class DuplicatedTitle(Exception):
    """DUPLICATED_TITLE"""
    pass
