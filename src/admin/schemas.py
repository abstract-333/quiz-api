from sqladmin import ModelView

from auth.models import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.email, ]
    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True
