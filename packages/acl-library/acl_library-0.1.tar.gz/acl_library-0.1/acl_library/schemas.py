from rest_framework import serializers
from django.contrib.auth.models import Permission
from acl_library.models import Group, ModulePermissions, Modules, PermissionList, Role

class ModuleSchema(serializers.ModelSerializer):
    
    class Meta:
        model = Modules
        fields = ['title','code','parent']



class PermissionListApi(serializers.ModelSerializer):
    
    
    # module = serializers.SerializerMethodField('get_module',allow_null=True)
    permission = serializers.CharField(source='permission.name',allow_null=True)
    
    class Meta:
        model = ModulePermissions
        fields = ['id','name','codename','module','permission']
    
""" Role Section """

class RoleListingSchema(serializers.ModelSerializer):
    
    class Meta:
        model = Role 
        fields = ['id','slug','name','is_active']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
    
        for field in representation:
            if representation[field] is None:
                representation[field] = ""
        
        return representation

class RoleListingApiSchema(serializers.ModelSerializer):
    label = serializers.CharField(source ='name')
    value = serializers.CharField(source='id')
    class Meta:
        model = Role 
        fields = ['value','label']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
    
        for field in representation:
            if representation[field] is None:
                representation[field] = ""
        
        return representation


class RoleDetailsSchema(serializers.ModelSerializer):
    
    permissions = serializers.SerializerMethodField('get_permissions',allow_null=True)
    
    class Meta:
        model = Role 
        fields = ['id','slug','name','permissions','is_active']
    
    def get_permissions(self,instance):
        
        permission = self.context.get('permissions')
        return PermissionListApi(permission,many=True).data
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
    
        for field in representation:
            if representation[field] is None:
                representation[field] = ""
        
        return representation
    
""" Group Section """

class GroupListingSchema(serializers.ModelSerializer):
    
    class Meta:
        model = Group 
        fields = ['id','slug','name','is_active']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
    
        for field in representation:
            if representation[field] is None:
                representation[field] = ""
        
        return representation


class GroupDetailsSchema(serializers.ModelSerializer):
    
    roles = serializers.SerializerMethodField('get_roles',allow_null=True)
    
    class Meta:
        model = Group 
        fields = ['id','slug','name','roles','is_active']
    
    def get_roles(self,instance):
        
        roles = self.context.get('roles')
        return RoleListingApiSchema(roles,many=True).data
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
    
        for field in representation:
            if representation[field] is None:
                representation[field] = ""
        
        return representation
    

class PermissionListSerializer(serializers.ModelSerializer):
    
    type = serializers.SerializerMethodField('get_type',allow_null=True)
    class Meta:
        model = ModulePermissions
        fields = ['id','name', 'codename','type']
        
    def get_type(self,instance):
        return instance.permission.name

class PermissionSchema(serializers.ModelSerializer):
    
    class Meta:
        model = PermissionList
        fields = ['name']


class PermissionListingAPISerializers(serializers.ModelSerializer):
    
    
    module_permissions = PermissionListSerializer(many=True, source='module_permission') 
    permission = serializers.SerializerMethodField('get_permission',allow_null=True)
    sub_module = serializers.SerializerMethodField('get_sub_module',allow_null=True)
    
    
    class Meta:
        model = Modules
        fields = ['id','parent','title','code','sort_order','status','permission','sub_module','module_permissions']
        
    def get_permission(self,instance):
        
        permission = self.context.get('permission')
        if permission is not None:
            return [p['name'] for p in permission.values('name')]  
        return [] 
    
    
    def get_sub_module(self,instance):
        sub_module  =  instance.children.all()        
         
        module_permission = ModulePermissions.objects.filter(module__in=sub_module).values_list('permission')
        
        permission = PermissionList.objects.filter(id__in=module_permission)
        return PermissionListingAPISerializers(sub_module,many=True,context={'permission':permission}).data