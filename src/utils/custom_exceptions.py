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
