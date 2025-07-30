from django.db import models
from django.utils.translation import gettext_lazy as _
from random import randint
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType

class PermissionList(models.Model):
    name = models.CharField(max_length=250,null=True,blank=True)
    
    class Meta:
        verbose_name = _("PermissionList")
        verbose_name_plural = _("PermissionLists")

    def __str__(self):
        return self.name
    
class Modules(models.Model):
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='children')
    code = models.CharField(max_length=250,null=True,blank=True)
    title = models.CharField(max_length=250,null=True,blank=True)
    sort_order = models.CharField(max_length=250,null=True,blank=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
class ModulePermissions(models.Model):
    module = models.ForeignKey(Modules,on_delete=models.CASCADE,related_name='module_permission')
    permission = models.ForeignKey(PermissionList,on_delete=models.CASCADE,null=True,blank=True,related_name='permission_set')
    name = models.CharField(_("name"), max_length=255)
    content_type = models.ForeignKey(
        ContentType,
        models.CASCADE,
        verbose_name=_("content type"),
    )
    codename = models.CharField(_("codename"), max_length=100)
    
    
    def __str__(self):
        return str(self.name)



class Role(models.Model):
    name = models.CharField(_("name"), max_length=150)
    slug  = models.SlugField(max_length=256,editable=False, blank = True, null = True)

    permissions = models.ManyToManyField(
        ModulePermissions,
        verbose_name=_("permissions"),
        blank=True,
    )  
        
    
    def save(self, *args, **kwargs):    
      
        if not self.slug or not self.name:
            self.slug = slugify(str(self.name))
            if Role.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = slugify(str(self.name)) + '-' + str(randint(1, 9999999))
            
        super(Role, self).save(*args, **kwargs)
    
    
    
    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

class Group(models.Model):
    name = models.CharField(_("name"), max_length=150)
    slug  = models.SlugField(max_length=256, editable=False, blank = True, null = True)
    roles = models.ManyToManyField(
        Role,
        verbose_name=_("roles"),
        blank=True,
    )  
    
    class Meta:
        verbose_name = _("group")
        verbose_name_plural = _("groups")
    
    def save(self, *args, **kwargs):
        if not self.slug or not self.name:
            self.slug = slugify(str(self.name))
            if Group.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = slugify(str(self.name)) + '-' + str(randint(1, 9999999))
        super(Group, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)





