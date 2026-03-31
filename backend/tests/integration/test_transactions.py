import pytest


class TestCreateTransaction:

    def test_create_expense_success(self, client, auth_headers, transaction_data):
        """Crear un gasto devuelve 201 con los datos correctos."""
        response = client.post(
            "/api/v1/transactions",
            json=transaction_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert float(data["amount"]) == transaction_data["amount"]
        assert data["type"] == "expense"
        assert data["description"] == transaction_data["description"]

    def test_create_income_success(self, client, auth_headers, income_data):
        """Crear un ingreso devuelve 201."""
        response = client.post(
            "/api/v1/transactions",
            json=income_data,
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["type"] == "income"

    def test_create_without_auth(self, client, transaction_data):
        """Sin autenticación devuelve 403."""
        response = client.post("/api/v1/transactions", json=transaction_data)
        assert response.status_code == 403

    def test_create_negative_amount(self, client, auth_headers):
        """Monto negativo devuelve 422."""
        response = client.post(
            "/api/v1/transactions",
            json={
                "amount": -100,
                "type": "expense",
                "date": "2024-01-15T10:00:00Z",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_zero_amount(self, client, auth_headers):
        """Monto cero devuelve 422."""
        response = client.post(
            "/api/v1/transactions",
            json={
                "amount": 0,
                "type": "expense",
                "date": "2024-01-15T10:00:00Z",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestGetTransactions:

    def test_list_returns_only_own_transactions(
        self, client, auth_headers, second_user_data, transaction_data
    ):
        """
        Un usuario solo debe ver SUS transacciones, no las de otros.
        Este es un test de seguridad crítico.
        """
        # Usuario 1 crea una transacción
        client.post(
            "/api/v1/transactions",
            json=transaction_data,
            headers=auth_headers,
        )

        # Usuario 2 se registra y crea su propia transacción
        reg_response = client.post(
            "/api/v1/auth/register",
            json=second_user_data,
        )
        user2_token = reg_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        client.post(
            "/api/v1/transactions",
            json={**transaction_data, "amount": 999.99},
            headers=user2_headers,
        )

        # Usuario 1 solo debe ver SU transacción
        response = client.get("/api/v1/transactions", headers=auth_headers)
        data = response.json()

        assert data["pagination"]["total"] == 1
        assert float(data["data"][0]["amount"]) == transaction_data["amount"]

    def test_pagination_works(self, client, auth_headers, transaction_data):
        """La paginación debe devolver el número correcto de items."""
        # Creamos 5 transacciones
        for i in range(5):
            client.post(
                "/api/v1/transactions",
                json={**transaction_data, "amount": float(i + 1) * 10},
                headers=auth_headers,
            )

        response = client.get(
            "/api/v1/transactions?page=1&limit=3",
            headers=auth_headers,
        )
        data = response.json()

        assert len(data["data"]) == 3
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["total_pages"] == 2

    def test_filter_by_type(self, client, auth_headers, transaction_data, income_data):
        """El filtro por tipo debe devolver solo ese tipo."""
        client.post("/api/v1/transactions", json=transaction_data, headers=auth_headers)
        client.post("/api/v1/transactions", json=income_data, headers=auth_headers)

        response = client.get(
            "/api/v1/transactions?type=expense",
            headers=auth_headers,
        )
        data = response.json()

        assert all(t["type"] == "expense" for t in data["data"])

    def test_search_by_description(self, client, auth_headers):
        """La búsqueda por descripción debe funcionar."""
        client.post("/api/v1/transactions", json={
            "amount": 100, "type": "expense",
            "date": "2024-01-15T10:00:00Z",
            "description": "Pizza italiana",
        }, headers=auth_headers)

        client.post("/api/v1/transactions", json={
            "amount": 50, "type": "expense",
            "date": "2024-01-16T10:00:00Z",
            "description": "Cine",
        }, headers=auth_headers)

        response = client.get(
            "/api/v1/transactions?search=pizza",
            headers=auth_headers,
        )
        data = response.json()

        assert data["pagination"]["total"] == 1
        assert "Pizza" in data["data"][0]["description"]


class TestUpdateDeleteTransaction:

    def test_update_transaction(self, client, auth_headers, transaction_data):
        """Actualizar una transacción debe cambiar solo los campos enviados."""
        create_response = client.post(
            "/api/v1/transactions",
            json=transaction_data,
            headers=auth_headers,
        )
        transaction_id = create_response.json()["id"]

        response = client.put(
            f"/api/v1/transactions/{transaction_id}",
            json={"amount": 200.00, "description": "Actualizado"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert float(data["amount"]) == 200.00
        assert data["description"] == "Actualizado"
        # El tipo no cambió
        assert data["type"] == "expense"

    def test_delete_transaction(self, client, auth_headers, transaction_data):
        """Eliminar una transacción devuelve 204."""
        create_response = client.post(
            "/api/v1/transactions",
            json=transaction_data,
            headers=auth_headers,
        )
        transaction_id = create_response.json()["id"]

        response = client.delete(
            f"/api/v1/transactions/{transaction_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # Verificamos que ya no existe
        get_response = client.get(
            f"/api/v1/transactions/{transaction_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    def test_cannot_delete_other_user_transaction(
        self, client, auth_headers, second_user_data, transaction_data
    ):
        """
        Un usuario no puede eliminar transacciones de otro.
        Test crítico de seguridad.
        """
        # Usuario 2 crea una transacción
        reg_response = client.post("/api/v1/auth/register", json=second_user_data)
        user2_headers = {"Authorization": f"Bearer {reg_response.json()['access_token']}"}

        create_response = client.post(
            "/api/v1/transactions",
            json=transaction_data,
            headers=user2_headers,
        )
        transaction_id = create_response.json()["id"]

        # Usuario 1 intenta borrarla → debe fallar con 404
        response = client.delete(
            f"/api/v1/transactions/{transaction_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestTransactionSummary:

    def test_summary_calculates_correctly(
        self, client, auth_headers, transaction_data, income_data
    ):
        """El resumen financiero debe calcular correctamente."""
        client.post("/api/v1/transactions", json=transaction_data, headers=auth_headers)
        client.post("/api/v1/transactions", json=income_data, headers=auth_headers)

        response = client.get("/api/v1/transactions/summary", headers=auth_headers)
        data = response.json()

        assert data["total_income"] == income_data["amount"]
        assert data["total_expenses"] == transaction_data["amount"]
        assert data["balance"] == income_data["amount"] - transaction_data["amount"]