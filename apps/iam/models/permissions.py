from django.contrib.auth.models import Permission as BasePermissionModel
from django.utils.translation import gettext_lazy as _


class Permission(BasePermissionModel):
    pass

    class Meta:
        app_label = 'iam'
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')

    def __str__(self):
        return '%s | %s' % (self.content_type, self.name)
