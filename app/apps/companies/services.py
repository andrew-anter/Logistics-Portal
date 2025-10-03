from .models import Company


def create_company(*, name: str, domain: str, active: bool = True) -> Company:
    company = Company(name=name, domain=domain, is_active=active)
    company.full_clean()
    company.save()
    return company
