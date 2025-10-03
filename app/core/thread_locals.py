from threading import local

_thread_locals = local()


def get_current_tenant():
    return getattr(_thread_locals, "company", None)
