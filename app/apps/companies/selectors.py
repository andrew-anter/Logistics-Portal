from .models import Company


def get_company(*, pk: int) -> Company:
    return Company.objects.get(pk=pk)
