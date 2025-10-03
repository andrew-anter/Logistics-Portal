from threading import local

from apps.companies.models import Company

_thread_locals = local()


def get_current_tenant() -> Company:
    return getattr(_thread_locals, "company", None)  # pyright: ignore


def set_current_tenant(tenant: Company) -> None:
    _thread_locals.tenant = tenant
