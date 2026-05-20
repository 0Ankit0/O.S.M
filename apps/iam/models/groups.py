from core.models import BaseModel
from django.contrib.auth.models import Group as BaseGroupModel
from django.utils.translation import gettext_lazy as _


class Group(BaseGroupModel,BaseModel):
    pass

    class Meta:
        app_label = 'iam'
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)
