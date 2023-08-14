from sqladmin import ModelView

from api.auth.auth_models import User
from api.auth.auth_schemas import Role
from api.blacklist.blacklist_models import Blacklist, BlockedLevel
from api.feedback.feedback_schemas import Feedback
from api.question.question_schemas import Question
from api.rating.rating_schemas import Rating
from api.section.section_models import Section
from api.university.university_schames import University
from api.warning.warning_schemas import WarningClass


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    column_list = [User.id, User.username, User.email]
    can_edit = True
    can_delete = True
    can_create = True
    can_export = True
    can_view_details = True
    form_include_pk = True


class UniversityAdmin(ModelView, model=University):
    name = "University"
    name_plural = "Universities"
    column_list = [University.id, University.name]
    can_edit = True
    can_delete = True
    can_create = True
    can_export = True
    can_view_details = True
    form_include_pk = True


class SectionAdmin(ModelView, model=Section):
    name = "Section"
    name_plural = "Sections"
    column_list = [Section.id, Section.name]
    can_edit = True
    can_delete = True
    can_create = True
    can_export = True
    can_view_details = True
    form_include_pk = True


class RoleAdmin(ModelView, model=Role):
    name = "Role"
    name_plural = "Roles"
    column_list = [Role.id, Role.name, Role.permissions]
    can_edit = True
    can_delete = True
    can_create = True
    can_export = True
    can_view_details = True
    form_include_pk = True


class QuestionAdmin(ModelView, model=Question):
    name = "Question"
    name_plural = "Questions"
    column_list = [Question.id, Question.question_title, Question.choices, Question.answer, Question.reference,
                   Question.reference_link, Question.added_by, Question.added_at, Question.section_id, Question.active]
    can_edit = True
    can_delete = True
    can_create = True
    can_export = True
    can_view_details = True
    form_include_pk = True


class FeedbackAdmin(ModelView, model=Feedback):
    name = "Feedback"
    name_plural = "Feedbacks"
    column_list = [Feedback.id, Feedback.rating, Feedback.feedback_title, Feedback.user_id, Feedback.question_id,
                   Feedback.question_author_id]
    can_edit = True
    can_delete = True
    can_create = True
    can_export = True
    can_view_details = True
    form_include_pk = True


class RatingAdmin(ModelView, model=Rating):
    name = "Rating"
    name_plural = "Ratings"
    column_list = [Rating.id, Rating.user_id, Rating.university_id,
                   Rating.questions_number, Rating.solved, Rating.added_at]

    can_edit = True
    can_delete = True
    can_create = True
    can_export = True
    can_view_details = True
    form_include_pk = True


class BlockedLevelAdmin(ModelView, model=BlockedLevel):
    name = "BlockedLevel"
    name_plural = "BlockedLevel"
    column_list = [BlockedLevel.id, BlockedLevel.unblocked_after, BlockedLevel.description]

    can_edit = True
    can_delete = True
    can_create = True
    can_export = True
    can_view_details = True
    form_include_pk = True


class BlacklistAdmin(ModelView, model=Blacklist):
    name = "BlackList"
    name_plural = "Blacklist"
    column_list = [Blacklist.id, Blacklist.user_id, Blacklist.blocking_level, Blacklist.blocked_at]

    can_edit = True
    can_delete = True
    can_create = True
    can_export = True
    can_view_details = True
    form_include_pk = True


class WarningAdmin(ModelView, model=WarningClass):
    name = "Warning"
    name_plural = "Warnings"
    column_list = [WarningClass.id, WarningClass.user_id, WarningClass.warning_level]

    can_edit = True
    can_delete = True
    can_create = True
    can_export = True
    can_view_details = True
    form_include_pk = True
