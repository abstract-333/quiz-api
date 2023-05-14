from sqladmin import ModelView

from auth.models import User
from auth.schemas import Role
from question.schemas import SoftwareQuestion, NetworkQuestion, AIQuestion
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


class SoftwareQuestionAdmin(ModelView, model=SoftwareQuestion):
    name = "Software Question"
    name_plural = "Software Questions"
    column_list = [SoftwareQuestion.id, SoftwareQuestion.resolve_time, SoftwareQuestion.question_title, SoftwareQuestion.choices, SoftwareQuestion.answer, SoftwareQuestion.added_by, SoftwareQuestion.added_at, SoftwareQuestion.section_id]
    can_edit = True
    can_delete = True
    can_create = True
    can_view_details = True
    form_include_pk = True


class NetworkQuestionAdmin(ModelView, model=NetworkQuestion):
    name = "Network Question"
    name_plural = "Network Questions"
    column_list = [NetworkQuestion.id, NetworkQuestion.resolve_time, NetworkQuestion.question_title, NetworkQuestion.choices, NetworkQuestion.answer, NetworkQuestion.added_by, NetworkQuestion.added_at, NetworkQuestion.section_id]
    can_edit = True
    can_delete = True
    can_create = True
    can_view_details = True
    form_include_pk = True


class AIQuestionAdmin(ModelView, model=AIQuestion):
    name = "AI Question"
    name_plural = "AI Questions"
    column_list = [AIQuestion.id, AIQuestion.resolve_time, AIQuestion.question_title, AIQuestion.choices, AIQuestion.answer,
                   AIQuestion.added_by, AIQuestion.added_at, AIQuestion.section_id]
    can_edit = True
    can_delete = True
    can_create = True
    can_view_details = True
    form_include_pk = True
