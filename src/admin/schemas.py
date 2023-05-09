
from sqladmin import ModelView

from auth.models import User
from auth.schemas import Role
from quiz.schemas import Quiz
from section.schemas import Section
from university.schames import University


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    column_list = [User.id, User.username, User.email]
    can_edit = True
    can_delete = False
    can_view_details = True


class UniversityAdmin(ModelView, model=University):
    name = "University"
    name_plural = "Universities"
    column_list = [University.id, University.name]
    can_edit = True
    can_delete = False
    can_view_details = True


class SectionAdmin(ModelView, model=Section):
    name = "Section"
    name_plural = "Sections"
    column_list = [Section.id, Section.name]
    can_edit = True
    can_delete = False
    can_view_details = True


class RoleAdmin(ModelView, model=Role):
    name = "Role"
    name_plural = "Roles"
    column_list = [Role.id, Role.name, Role.permissions]
    can_edit = True
    can_delete = False
    can_view_details = True


class QuizAdmin(ModelView, model=Quiz):
    name = "Quiz"
    name_plural = "Quizzes"
    column_list = [Quiz.id, Quiz.resolve_time, Quiz.question, Quiz.choices, Quiz.answer, Quiz.added_by, Quiz.added_at]
    can_edit = True
    can_delete = False
    can_view_details = True


