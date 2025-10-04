from threading import local

from apps.companies.models import Company

_thread_locals = local()


def get_current_tenant() -> Company:
    return getattr(_thread_locals, "company", None)  # pyright: ignore


def set_current_tenant(company: Company) -> None:
    _thread_locals.company = company


def delete_current_tenant() -> None:
    delattr(_thread_locals, "company")


def set_current_user(user) -> None:  # noqa: ANN001
    _thread_locals.user = user


def get_current_user():  # noqa: ANN201
    return getattr(_thread_locals, "user", None)  # pyright: ignore
