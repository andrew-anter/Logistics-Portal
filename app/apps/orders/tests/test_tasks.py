from pathlib import Path

import pytest

from apps.orders.tasks import generate_export_file_task

from ..models import Export


@pytest.mark.django_db
def test_generate_export_file_task(test_data, company, mocker, settings, tmp_path):
    # 1. Arrange: Override Django's MEDIA_ROOT to use the temporary directory
    settings.MEDIA_ROOT = tmp_path

    # Create an Export object to track the task
    export = Export.objects.create(
        requested_by=test_data["profile"],
        company=test_data["company"],
    )

    # 2. Act: Call the task function directly
    generate_export_file_task(
        export_id=export.pk,
        order_ids=test_data["order_ids"],
        company_id=company.pk,
    )

    # 3. Assert: Check that the task updated the Export object correctly
    export.refresh_from_db()

    assert export.status == Export.Status.READY
    assert export.file is not None
    assert export.file.name.endswith(f"export_{export.pk}.csv")

    # Check the content of the generated file
    with export.file.open("r") as f:
        content = f.read()
        assert content.startswith("Reference Code,Product SKU")
        assert len(content.strip().split("\n")) == 6  # Assuming 5 orders + header

    # NO manual cleanup needed. pytest will delete the tmp_path directory.
