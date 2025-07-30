from django.utils.deprecation import MiddlewareMixin # type: ignore
from .models import Tenant
from .utils import set_current_tenant

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host().split(':')[0]
        try:
            tenant = Tenant.objects.get(domain=host, is_active=True)
            request.tenant = tenant
            set_current_tenant(tenant)
        except Tenant.DoesNotExist:
            request.tenant = None
