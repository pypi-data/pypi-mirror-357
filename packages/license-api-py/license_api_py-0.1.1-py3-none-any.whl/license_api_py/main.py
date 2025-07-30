import httpx
from pydantic import BaseModel


class LoginResponse(BaseModel):
    username: str
    password: str
    hwid: str


class LicenseAPI:
    def __init__(self, url):
        """
        Initialize the LicenseAPI with the given URL.

        Args:
            url (str): The base URL of the license API.
        """
        self.url = url

    async def login(self, creds: LoginResponse) -> bool:
        """
        Login to the license API

        Args:
            creds (LoginResponse): The login credentials.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.url}/auth/login",
                json={
                    "username": creds.username,
                    "password": creds.password,
                },
            )

            response.raise_for_status()

            token = response.json()["access_token"]

            await self.link_hwid(creds.hwid, token)

        return True

    async def link_hwid(self, hwid: str, token: str):
        """
        Link the hardware ID to the user's account.

        Args:
            hwid (str): The hardware ID to link.
            token (str): The authentication token.
        """
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.url}/users/hwid",
                json={"hwid": hwid},
                headers={
                    "Authorization": f"Bearer {token}",
                },
            )

            response.raise_for_status()

        return response.status_code
