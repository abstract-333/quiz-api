# from fastapi_amis_admin.admin.settings import Settings
# from fastapi_amis_admin.admin.site import AdminSite
# from fastapi_amis_admin.admin import admin
# from fastapi_amis_admin.amis.components import PageSchema
#
# # Create AdminSite instance
# from database import DATABASE_URL
#
# site = AdminSite(settings=Settings(database_url_async=DATABASE_URL))
#
#
# # Registration management class
# @site.register_admin
# class GitHubIframeAdmin(admin.IframeAdmin):
#     # Set page menu information
#     page_schema = PageSchema(label='AmisIframeAdmin', icon='fa fa-github')
#     # Set the jump link
#     src = 'https://github.com/amisadmin/fastapi_amis_admin'