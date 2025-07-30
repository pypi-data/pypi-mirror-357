from rest_framework import serializers
from acl_library.models import Group, ModulePermissions, Modules, PermissionList, Role
from django.contrib.auth.models import Permission


""" Role section"""

class PermissionDetailSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    value = serializers.CharField(max_length=50)


class CreateUpdateRoleSerializer(serializers.ModelSerializer):
    
    instance_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(),default=None)
    name = serializers.CharField(required=False)
    # # permissions = serializers.PrimaryKeyRelatedField(queryset= ModulePermissions.objects.all(),many=True,required=False)
    # codename = serializers.ListField()
    permissions = PermissionDetailSerializer(many=True)
    
    class Meta:
        model = Role 
        fields = ['instance_id','name','permissions']
        
    
    def validate(self, attrs):
        
        name = attrs.get('name')
        instance_id = attrs.get('instance_id',None)
        role = Role.objects.filter(name=name)
        if role is not None:
            if instance_id is not None:
                role = role.exclude(pk=instance_id.pk)
            if role.exists():
                raise serializers.ValidationError({'name':"Role name already exists"})
        return attrs
    
    def create(self, validated_data):
        
        request               = self.context.get('request')
        permissions_data = validated_data.pop('permissions')
        instance = Role()
        instance.name = validated_data.get('name')
        instance.save()
        
        for permission_detail in permissions_data:
            permission_name = permission_detail['name']
            permission_value = permission_detail['value']

            permission = ModulePermissions.objects.get(codename=permission_name)
            
            if permission_value == 'allowed':
                instance.permissions.add(permission)
            elif permission_value == 'denied':
                instance.permissions.remove(permission)
                

        return instance
    
    def update(self, instance, validated_data):
   
        request               = self.context.get('request')
        instance.name         = validated_data.get('name',None)
        old_permissions = set(instance.permissions.all())
        instance.permissions.clear()

        instance.save()

        
        permissions_data = validated_data.pop('permissions')
        for permission_detail in permissions_data:
            permission_name = permission_detail['name']
            permission_value = permission_detail['value']

            permission = ModulePermissions.objects.get(codename=permission_name)
            
            if permission_value == 'allowed':
                instance.permissions.add(permission)
            elif permission_value == 'denied':
                instance.permissions.remove(permission)

        new_permissions = set(instance.permissions.all())

        permissions_added = new_permissions - old_permissions
        permissions_removed = old_permissions - new_permissions

        self.update_user_permissions_for_role_change(instance, permissions_added, permissions_removed)

        return instance
    
    def update_user_permissions_for_role_change(self, role, permissions_added, permissions_removed):
    
        related_groups = role.group_set.all()

        affected_users = set()
        for group in related_groups:
            affected_users.update(group.custom_user_set.all())


        for user in affected_users:
    
            if permissions_added:
                user.user_permissions.add(*permissions_added)

        
            if permissions_removed:
                user.user_permissions.remove(*permissions_removed)        

class RoleStatusChangeSerializer(serializers.ModelSerializer):
    
    instance_ids = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(),many=True)
    
    class Meta:
        model = Role
        fields = ['instance_ids']
    
    def update(self, instance, validated_data):
        
        instance.is_active = not instance.is_active
        instance.save()
        return instance
    
class DestroyRoleApiSerializer(serializers.ModelSerializer):
    id   = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(),many=True,default=None)
    
    class Meta:
        model = Role
        fields = ['id']
        

""" Group section"""

class CreateUpdateGroupSerializer(serializers.ModelSerializer):
    
    instance_id = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(),default=None)
    name = serializers.CharField(required=False)
    roles = serializers.PrimaryKeyRelatedField(queryset= Role.objects.all(),many=True,required=False)
    
    class Meta:
        model = Group 
        fields = ['instance_id','name','roles']
        
    def validate(self, attrs):
        
        name = attrs.get('name')
        instance_id = attrs.get('instance_id',None)
        group = Group.objects.filter(name=name)
        if group is not None:
            if instance_id is not None:
                group = group.exclude(pk=instance_id.pk)
            if group.exists():
                raise serializers.ValidationError({'name':"Group name already exists"})
        return attrs
        
    def create(self, validated_data):
        request               = self.context.get('request')
        instance = Group()
        instance.name         = validated_data.get('name',None)
        instance.save() 
        
        roles = validated_data.get('roles')
        
        if roles:
            for role in roles:
                instance.roles.add(role)
        
        return instance
    
    def update(self, instance, validated_data):
        
        request               = self.context.get('request')
        instance.name         = validated_data.get('name',None)
        instance.save()
        
        instance.roles.clear()
        roles = validated_data.get('roles')
        for role in roles:
                instance.roles.add(role)
        
        return instance
    
class GroupStatusChangeSerializer(serializers.ModelSerializer):
    
    instance_ids = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(),many=True,default=None)
    
    class Meta:
        model = Group
        fields = ['instance_ids']
    
    def update(self, instance, validated_data):
        
        instance.is_active = not instance.is_active
        instance.save()
        return instance
    
    
class DestroyGroupApiSerializer(serializers.ModelSerializer):
    id   = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(),many=True,default=None)
    
    class Meta:
        model = Group
        fields = ['id']
        
""" Permission Listing """

class DistinctPermissionSchema(serializers.ModelSerializer):
    
    class Meta:
        model = PermissionList
        fields = ['name']


