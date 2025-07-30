from django.urls import path, include, re_path
from . import views



app_name = 'acl'

urlpatterns = [
    re_path(r'^permission/', include([
        path('list-permissions/',views.PermissionListingApi.as_view(),name='list-permissions'),
        path('permissions',views.PermissionApi.as_view(),name='permissions'),

    ])),
    re_path(r'^role/', include([
        path('role-details',views.RoleDetails.as_view(),name='role-details'),


    ])),
    
    re_path(r'^group/', include([
        path('group-details',views.GroupDetailsAPI.as_view(),name='group-details'),
    ])),
]