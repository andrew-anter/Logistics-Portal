from apps.companies.models import Company
from apps.products.services import create_product_service
from apps.users.roles import Role
from apps.users.services import create_profile_service
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seeds the database with sample data for demonstration."

    def handle(self, *args, **options) -> None:  # noqa: ANN002, ANN003, ARG002
        self.stdout.write("Seeding database with sample data...")

        # Ensure roles exist
        for role_enum in Role:
            Group.objects.get_or_create(name=role_enum)

        # Create Company A
        company_a, _ = Company.objects.get_or_create(name="MegaCorp", domain="megacorp")
        admin_role = Group.objects.get(name=Role.ADMIN)

        # Create an admin for Company A
        try:
            create_profile_service(
                email="admin@megacorp.com",
                password="password123",
                company=company_a,
                role=admin_role,
                first_name="Admin",
                last_name="A",
            )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(
                    f"Could not create admin for MegaCorp (may already exist): {e}",
                ),
            )

        # Create products for Company A
        create_product_service(company=company_a, name="Widget A", stock_quantity=100)
        create_product_service(company=company_a, name="Gadget A", stock_quantity=250)

        # Create Company B
        company_b, _ = Company.objects.get_or_create(name="LogiPro", domain="logipro")
        operator_role = Group.objects.get(name=Role.OPERATOR)

        # Create an operator for Company B
        try:
            create_profile_service(
                email="operator@logipro.com",
                password="password123",
                company=company_b,
                role=operator_role,
                first_name="Operator",
                last_name="B",
            )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(
                    f"Could not create operator for LogiPro (may already exist): {e}",
                ),
            )

        self.stdout.write(self.style.SUCCESS("Database seeding complete."))
