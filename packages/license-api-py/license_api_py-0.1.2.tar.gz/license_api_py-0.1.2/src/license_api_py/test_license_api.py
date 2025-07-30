import pytest
import respx
from httpx import Response, HTTPStatusError

from license_api_py.main import LicenseAPI, LoginResponse

pytestmark = pytest.mark.anyio


@respx.mock
async def test_successful_login_and_link():
    api = LicenseAPI("https://example.com")
    creds = LoginResponse(username="testuser", password="testpass", hwid="ABC-123-XYZ")

    login_route = respx.post("https://example.com/auth/login").mock(
        return_value=Response(200, json={"access_token": "token123"})
    )

    hwid_route = respx.patch("https://example.com/users/hwid").mock(
        return_value=Response(200)
    )

    result = await api.login(creds)
    assert result is True
    assert login_route.called, "Login route was not called"
    assert hwid_route.called, "HWID link route was not called"


@respx.mock
async def test_login_http_error_raises():
    api = LicenseAPI("https://example.com")
    creds = LoginResponse(username="failuser", password="failpass", hwid="HWID-FAIL")

    respx.post("https://example.com/auth/login").mock(return_value=Response(401))

    with pytest.raises(HTTPStatusError):
        await api.login(creds)


@respx.mock
async def test_missing_access_token_raises_key_error():
    api = LicenseAPI("https://example.com")
    creds = LoginResponse(username="no_token", password="pass", hwid="HWID")

    respx.post("https://example.com/auth/login").mock(
        return_value=Response(200, json={})
    )

    with pytest.raises(KeyError):
        await api.login(creds)


@respx.mock
async def test_link_hwid_http_error_raises():
    api = LicenseAPI("https://example.com")

    respx.patch("https://example.com/users/hwid").mock(return_value=Response(500))

    with pytest.raises(HTTPStatusError):
        await api.link_hwid("ABC-123-XYZ", "token123")
