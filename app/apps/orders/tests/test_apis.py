import pytest

from apps.orders.models import Order
from apps.orders.services import create_order_service


@pytest.mark.django_db
class TestOrderAPI:
    def test_list_orders_as_operator(
        self,
        api_client,
        operator_profile,
        admin_profile,
        product,
        company,
        mocker,
        setup_current_tenant,
    ):
        mock_process_task = mocker.patch(
            "apps.orders.tasks.process_order_task.delay",
        )
        # Arrange: Operator creates one order, admin creates another
        order1 = create_order_service(
            product=product,
            quantity=1,
            created_by=operator_profile,
            company=company,
        )
        mock_process_task.assert_called_once_with(order1.pk)

        create_order_service(
            product=product,
            quantity=2,
            created_by=admin_profile,
            company=company,
        )

        api_client.force_authenticate(user=operator_profile.user)

        # Act
        response = api_client.get("/api/orders/")

        # Assert: Operator sees only their own order
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["quantity"] == 1

    def test_list_orders_as_admin(
        self,
        api_client,
        operator_profile,
        admin_profile,
        product,
        company,
        mocker,
        setup_current_tenant,
    ):
        mocker.patch(
            "apps.orders.tasks.process_order_task.delay",
        )
        # Arrange: Operator and admin both create orders
        create_order_service(
            product=product,
            quantity=1,
            created_by=operator_profile,
            company=company,
        )
        create_order_service(
            product=product,
            quantity=2,
            created_by=admin_profile,
            company=company,
        )
        api_client.force_authenticate(user=admin_profile.user)

        # Act
        response = api_client.get("/api/orders/")

        # Assert: Admin sees all orders for the company
        assert response.status_code == 200
        assert len(response.data) == 2

    def test_create_order_success(
        self,
        api_client,
        operator_profile,
        product,
        mocker,
        setup_current_tenant,
    ):
        # Arrange
        api_client.force_authenticate(user=operator_profile.user)
        mock_create_service = mocker.patch("apps.orders.views.create_order_service")
        order_data = {"product": product.pk, "quantity": 10}

        # Act
        response = api_client.post("/api/orders/", data=order_data)

        # Assert
        assert response.status_code == 201  # 201 Created
        mock_create_service.assert_called_once()

    def test_bulk_create_orders_success(
        self,
        api_client,
        operator_profile,
        product,
        mocker,
        setup_current_tenant,
    ):
        # Arrange
        api_client.force_authenticate(user=operator_profile.user)
        mock_create_service = mocker.patch("apps.orders.views.create_order_service")
        orders_data = [
            {"product": product.pk, "quantity": 5},
            {"product": product.pk, "quantity": 3},
        ]

        # Act
        response = api_client.post(
            "/api/orders/bulk-create/",
            data=orders_data,
            format="json",
        )

        # Assert
        assert response.status_code == 202  # 202 Accepted
        assert mock_create_service.call_count == 2

    def test_retry_order_success(
        self,
        api_client,
        operator_profile,
        product,
        company,
        mocker,
    ):
        # Arrange
        order = Order.objects.create(
            product=product,
            quantity=1,
            created_by=operator_profile,
            company=company,
            status=Order.Status.FAILED,
        )
        api_client.force_authenticate(user=operator_profile.user)
        mock_retry_service = mocker.patch("apps.orders.views.retry_order_service")

        # Act
        response = api_client.post(f"/api/orders/{order.pk}/retry/")

        # Assert
        assert response.status_code == 200
        mock_retry_service.assert_called_once()

    def test_unauthenticated_access_denied(self, api_client):
        # Act
        response = api_client.get("/api/orders/")
        # Assert
        assert response.status_code == 401  # Unauthorized
