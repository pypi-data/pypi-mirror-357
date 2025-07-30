from django.contrib import admin

from acl_library.models import Modules, PermissionList, Role,ModulePermissions,Group

# Register your models here.

admin.site.register(PermissionList)
admin.site.register(Modules)
admin.site.register(ModulePermissions)

admin.site.register(Role)
admin.site.register(Group)