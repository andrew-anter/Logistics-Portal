import pytest

from apps.orders.tasks import generate_export_file_task

from ..models import Export


@pytest.mark.django_db
def test_generate_export_file_task(test_data, company, celery_app):
    # 1. Arrange: Create an Export object to track the task
    export = Export.objects.create(
        requested_by=test_data["profile"],
        company=test_data["company"],
    )

    # 2. Act: Call the task function directly with the required arguments
    generate_export_file_task.delay(
        export_id=export.pk,
        order_ids=test_data["order_ids"],
        company_id=company.pk,
    )

    # 3. Assert: Check that the task updated the Export object correctly
    export.refresh_from_db()

    assert export.status == Export.Status.READY
    assert export.file is not None
    assert export.file.name.endswith(f"export_{export.pk}.csv")

    # Optional: Check the content of the generated file
    with export.file.open("r") as f:
        content = f.read()
        # Check that it looks like a CSV with a header and two data rows
        assert content.startswith("Reference Code,Product SKU")
        assert len(content.strip().split("\n")) == 3
