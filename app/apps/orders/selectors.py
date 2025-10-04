from django.db.models import QuerySet

from apps.companies.selectors import get_company
from apps.orders.models import Export, Order


def get_export_for_company(*, pk: int, company_pk: int) -> Export:
    company = get_company(pk=company_pk)
    return Export.objects.for_tenant(company).get(pk=pk)  # pyright: ignore[reportAttributeAccessIssue]


def get_orders_for_company(*, company_pk: int) -> QuerySet[Order]:
    company = get_company(pk=company_pk)
    return Order.objects.for_tenant(company).all()  # pyright: ignore[reportAttributeAccessIssue]
