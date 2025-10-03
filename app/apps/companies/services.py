from .models import Company
from .validators import validate_subdomain_name


def create_company(*, name: str, domain: str, active: bool = True) -> Company:
    validate_subdomain_name(domain)
    company = Company(name=name, domain=domain, is_active=active)
    company.full_clean()
    company.save()
    return company
