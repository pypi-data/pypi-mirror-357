from typing import Any
from django.shortcuts import render
from django.contrib.auth.models import Permission
from rest_framework.generics import ListAPIView,GenericAPIView
from acl_library.models import Group, ModulePermissions, Modules, PermissionList, Role
from acl_library.schemas import GroupDetailsSchema, GroupListingSchema, PermissionListApi, PermissionListingAPISerializers, PermissionSchema, RoleDetailsSchema, RoleListingSchema
from acl_library.serializers import CreateUpdateGroupSerializer, CreateUpdateRoleSerializer, DestroyGroupApiSerializer, DestroyRoleApiSerializer, GroupStatusChangeSerializer, RoleStatusChangeSerializer
from acl_permissions.utils import ResponseInfo,APIUtils,RestPagination
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated

"""List Permissions"""


class PermissionListingApi(ListAPIView):
    
    def __init__(self, **kwargs: Any) -> None:
        self.response_format = ResponseInfo().response
        super(PermissionListingApi,self).__init__(**kwargs)
        
    serializer_class = PermissionListApi
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(tags=["Permission"])
    def get(self, request):
        try:
            queryset = self.get_queryset()
            serializer = self.serializer_class(queryset,many=True)
            
            
            self.response_format['status_code'] = status.HTTP_200_OK
            data = {'permissions': serializer.data}
            self.response_format["data"] = data
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_200_OK)
        
        
        except Exception as e:
            return APIUtils.handle_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get_queryset(self):
       
        user = self.request.user

        if user.is_superuser:
            permissions = ModulePermissions.objects.all().select_related('permission')
        else:
            permissions = user.user_permissions.all().select_related('permission')
        return permissions
    
class PermissionApi(ListAPIView):
    def __init__(self, **kwargs: Any) -> None:
        self.response_format = ResponseInfo().response
        super(PermissionApi,self).__init__(**kwargs)
        
    serializer_class = PermissionListingAPISerializers
    
    
    @swagger_auto_schema(tags=["Permission"])
    def get(self, request):
        try:
            
            queryset = Modules.objects.filter(parent__isnull=True).prefetch_related('module_permission__permission')
           
            
            serializer = self.serializer_class(queryset,many=True)
            permission = PermissionList.objects.all()

            
            self.response_format['status_code'] = status.HTTP_200_OK
            data = {'modules': serializer.data,"permissions":PermissionSchema(permission,many=True).data}
            self.response_format["data"] = data
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_200_OK)
        
        except Exception as e:
            return APIUtils.handle_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


"""Create update Role"""

class RoleDetails(GenericAPIView):
    
    def __init__(self, **kwargs: Any) -> None:
        self.response_format = ResponseInfo().response
        super(RoleDetails,self).__init__(**kwargs)
        
    pagination_class = RestPagination
    
    permission_classes = (IsAuthenticated,)
    ordering_fields = ['name','is_active']
    
    
    serializer_class = CreateUpdateRoleSerializer
    
    @swagger_auto_schema(tags=["Role"],request_body=serializer_class)
    def post(self,request):
        
        try:
            serializer = self.serializer_class(data=request.data,context={'request':request})
            if not serializer.is_valid():
                return Response({"errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)            
            
            instance = serializer.validated_data.get('instance_id',None)
            serializer = self.serializer_class(instance,data=request.data,context={'request':request})
            
            if not serializer.is_valid():
                return Response({"errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)            
            serializer.save()
            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = "Success"
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED) 
        
        except Exception as e:
            return APIUtils.handle_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    queryset = Role.objects.filter().order_by('-id')  
    
    role_serializer_class = RoleListingSchema
    details_serializer_class = RoleDetailsSchema
      
    id = openapi.Parameter('id', openapi.IN_QUERY,
                                    type=openapi.TYPE_STRING, required=False,
                                    description="Enter id for the detail view")
    
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name'] 
    
    @swagger_auto_schema(pagination_class=RestPagination, tags=["Role"],
                         manual_parameters=[id])
    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        id = request.GET.get('id')
        is_paginated = request.GET.get('is_paginated')
        is_active =  request.GET.get('is_active')
        
        
        if id:
            
            queryset = queryset.filter(id=id)
        
        if is_active:
            
            queryset = queryset.filter(is_active=is_active.title())
            
       
        page = self.paginate_queryset(queryset)
        serializer_class = self.get_serializer_class() 
        
        if is_paginated == 'false':
            serializer = self.details_serializer_class(queryset, many=True, context={'request': request})
            
            self.response_format['data'] = serializer.data
            self.response_format['status_code'] = status.HTTP_200_OK
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_200_OK) 
   
        serializer = serializer_class(page, many=True,context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)      
    
    def get_serializer_class(self):
        
        if self.request.GET.get('id'):    
            return self.details_serializer_class
        
        return self.role_serializer_class
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.GET.get('id'):
            
            id = self.request.GET.get('id')
            role = Role.objects.filter(id=id).first()
            if role: 
                context['permissions'] = role.permissions.all()
        return context
    

        
    status_serializer_class = RoleStatusChangeSerializer
        
    @swagger_auto_schema(tags=["Role"],request_body=status_serializer_class)
    def put(self,request):
        
        try:
            serializer = self.status_serializer_class(data=request.data)
            
            if not serializer.is_valid():
                return APIUtils.handle_error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
           
            instance_ids = serializer.validated_data.get('instance_ids', None)
            
            for instance in instance_ids:
                # Since the instance is already retrieved, we can directly toggle the status
                instance.is_active = not instance.is_active
                instance.save()
        
            # Prepare successful response
            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = "Success"
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)    
        except Exception as e:
            return APIUtils.handle_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


    delete_serializer_class = DestroyRoleApiSerializer
    @swagger_auto_schema(tags=["Role"], request_body=delete_serializer_class)
    def delete(self, request):
        try:
         
            serializer = self.delete_serializer_class(data=request.data)
            if serializer.is_valid():
              
                instance_ids = serializer.validated_data.get('id',None)

                for instance in instance_ids:
                    instance.delete()
                
                self.response_format['status_code'] = status.HTTP_200_OK
                self.response_format["message"] = "Success"
                self.response_format["status"] = True
                return Response(self.response_format, status=status.HTTP_200_OK)

            else:
                return APIUtils.handle_error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return APIUtils.handle_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

"""Create update Group"""

class GroupDetailsAPI(GenericAPIView):
    
    def __init__(self, **kwargs: Any) -> None:
        self.response_format = ResponseInfo().response
        super(GroupDetailsAPI,self).__init__(**kwargs)
        
    serializer_class = CreateUpdateGroupSerializer
    group_serializer_class = GroupListingSchema
    details_serializer_class = GroupDetailsSchema
    delete_erializer_class = DestroyGroupApiSerializer
    
    queryset = Group.objects.filter().order_by('-id')  
    pagination_class = RestPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name'] 
    ordering_fields = ['name','is_active']
    
    
    @swagger_auto_schema(tags=["Group"],request_body=serializer_class)
    def post(self,request):
        
        try:
            serializer = self.serializer_class(data=request.data,context={'request':request})
            if not serializer.is_valid():
                return Response({"errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)            
            
            instance = serializer.validated_data.get('instance_id',None)
            serializer = self.serializer_class(instance,data=request.data,context={'request':request})
            
            if not serializer.is_valid():
                return Response({"errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)            
            
            serializer.save()
            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = ''
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED) 
        
        except Exception as e:
            return APIUtils.handle_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    
    
       
    id = openapi.Parameter('id', openapi.IN_QUERY,
                                    type=openapi.TYPE_STRING, required=False,
                                    description="Enter id for the detail view")
    
    @swagger_auto_schema(pagination_class=RestPagination, tags=["Group"],
                         manual_parameters=[id])
    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        id = request.GET.get('id')
        is_paginated =  request.GET.get('is_paginated')
        is_active =  request.GET.get('is_active')
       
        if id:
            queryset = queryset.filter(id=id)
            
        if is_active:
            queryset = queryset.filter(is_active=is_active.title())

       
        page = self.paginate_queryset(queryset)
        serializer_class = self.get_serializer_class() 
    
        if is_paginated == 'false':
            serializer = serializer_class(queryset, many=True,context=self.get_serializer_context())
            
            self.response_format['data'] = serializer.data
            self.response_format['status_code'] = status.HTTP_200_OK
            self.response_format["message"] = _success
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_200_OK) 
  
        serializer = serializer_class(page, many=True,context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)        
    
    def get_serializer_class(self):
     
        if self.request.GET.get('id'):
            return self.details_serializer_class
        
        return self.group_serializer_class
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.GET.get('id'):
            
            id = self.request.GET.get('id')
            group = Group.objects.filter(id=id).first()
            if group: 
                context['roles'] = group.roles.all()
        return context


    status_serializer_class = GroupStatusChangeSerializer
        
    @swagger_auto_schema(tags=["Group"],request_body=status_serializer_class)
    def patch(self,request):
        
        try:
            serializer = self.status_serializer_class(data=request.data)
            
            if not serializer.is_valid():
                return APIUtils.handle_error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
            
            instance = serializer.validated_data.get('instance_ids',None)
            for data in instance:
                serializer = self.status_serializer_class(data,data=request.data,context={'request':request})
            
                if not serializer.is_valid():
                    return APIUtils.handle_error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
                
                serializer.save()
            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format["message"] = "Success"
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED) 
        
        except Exception as e:
            return APIUtils.handle_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(tags=["Group"], request_body=delete_erializer_class)
    def delete(self, request):
        try:
            serializer = self.delete_erializer_class(data=request.data)
            if serializer.is_valid():

                instance_ids = serializer.validated_data['id']

                for instance in instance_ids:
                    instance.delete()
                
                self.response_format['status_code'] = status.HTTP_200_OK
                self.response_format["message"] = "Success"
                self.response_format["status"] = True
                return Response(self.response_format, status=status.HTTP_200_OK)

            else:
                return APIUtils.handle_error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return APIUtils.handle_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)