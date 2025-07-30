from django.db import models # type: ignore
from .utils import get_current_tenant

class TenantQuerySet(models.QuerySet):
    def for_current_tenant(self):
        return self.filter(tenant=get_current_tenant())

class TenantManager(models.Manager):
    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db).for_current_tenant()
