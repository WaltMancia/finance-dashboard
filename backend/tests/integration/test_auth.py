import pytest


class TestRegister:

    def test_register_success(self, client, user_data):
        """Registro exitoso devuelve 201 con tokens."""
        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()

        # Verificamos estructura de la respuesta
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["name"] == user_data["name"]

        # El password nunca debe aparecer en la respuesta
        assert "password" not in data["user"]
        assert "password_hash" not in data["user"]

    def test_register_duplicate_email(self, client, user_data):
        """Registrar el mismo email dos veces devuelve 409."""
        client.post("/api/v1/auth/register", json=user_data)
        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 409
        assert "registrado" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        """Email inválido devuelve 422."""
        response = client.post("/api/v1/auth/register", json={
            "name": "Test",
            "email": "not-an-email",
            "password": "password123",
        })
        assert response.status_code == 422

    def test_register_short_password(self, client):
        """Contraseña menor a 6 caracteres devuelve 422."""
        response = client.post("/api/v1/auth/register", json={
            "name": "Test",
            "email": "test@test.com",
            "password": "123",
        })
        assert response.status_code == 422

    def test_register_missing_fields(self, client):
        """Campos faltantes devuelven 422."""
        response = client.post("/api/v1/auth/register", json={
            "email": "test@test.com",
            # Falta name y password
        })
        assert response.status_code == 422


class TestLogin:

    def test_login_success(self, client, user_data, registered_user):
        """Login con credenciales correctas devuelve tokens."""
        response = client.post("/api/v1/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"],
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, client, user_data, registered_user):
        """Contraseña incorrecta devuelve 401."""
        response = client.post("/api/v1/auth/login", json={
            "email": user_data["email"],
            "password": "wrong_password",
        })
        assert response.status_code == 401

        # Mismo mensaje para usuario no encontrado y contraseña incorrecta
        assert "credenciales" in response.json()["detail"].lower()

    def test_login_nonexistent_email(self, client):
        """Email que no existe devuelve 401 con mismo mensaje."""
        response = client.post("/api/v1/auth/login", json={
            "email": "noexiste@test.com",
            "password": "password123",
        })
        assert response.status_code == 401
        assert "credenciales" in response.json()["detail"].lower()


class TestProtectedRoutes:

    def test_me_with_valid_token(self, client, auth_headers, user_data):
        """Token válido da acceso a rutas protegidas."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["email"] == user_data["email"]

    def test_me_without_token(self, client):
        """Sin token devuelve 403."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403

    def test_me_with_invalid_token(self, client):
        """Token inválido devuelve 401."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer token_invalido"},
        )
        assert response.status_code == 401

    def test_refresh_token(self, client, registered_user):
        """El refresh token genera un nuevo access token."""
        response = client.post("/api/v1/auth/refresh-token", json={
            "refresh_token": registered_user["refresh_token"],
        })

        assert response.status_code == 200
        assert "access_token" in response.json()