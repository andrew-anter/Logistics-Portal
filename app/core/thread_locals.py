from threading import local

from apps.companies.models import Company
from django.contrib.auth.models import User

_thread_locals = local()


def get_current_tenant() -> Company:
    return getattr(_thread_locals, "company", None)  # pyright: ignore


def set_current_tenant(company: Company) -> None:
    _thread_locals.company = company


def set_current_user(user: User) -> None:
    _thread_locals.user = user


def get_current_user() -> User:
    return getattr(_thread_locals, "user", None)  # pyright: ignore
