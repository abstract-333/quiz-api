from sqladmin import ModelView

from auth.models import User
from auth.schemas import Role
from feedback.schemas import Feedback
from question.schemas import Question
from section.schemas import Section
from university.schames import University


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    column_list = [User.id, User.username, User.email]
    can_edit = True
    can_delete = True
    can_view_details = True
    form_include_pk = True


class UniversityAdmin(ModelView, model=University):
    name = "University"
    name_plural = "Universities"
    column_list = [University.id, University.name]
    can_edit = True
    can_delete = True
    can_view_details = True


class SectionAdmin(ModelView, model=Section):
    name = "Section"
    name_plural = "Sections"
    column_list = [Section.id, Section.name]
    can_edit = True
    can_delete = True
    can_view_details = True


class RoleAdmin(ModelView, model=Role):
    name = "Role"
    name_plural = "Roles"
    column_list = [Role.id, Role.name, Role.permissions]
    can_edit = True
    can_delete = True
    can_view_details = True


class QuestionAdmin(ModelView, model=Question):
    name = "Question"
    name_plural = "Questions"
    column_list = [Question.id, Question.question_title, Question.choices, Question.answer,
                   Question.added_by, Question.added_at, Question.section_id]
    can_edit = True
    can_delete = True
    can_create = True
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
    can_view_details = True
    form_include_pk = True
