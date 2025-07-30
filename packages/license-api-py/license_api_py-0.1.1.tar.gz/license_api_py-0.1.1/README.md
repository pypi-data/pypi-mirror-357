# license-api-py

## Installation

```
pip install license-api-py
```

## Code example

```py
import asyncio
from license_api_py import LicenseAPI

api = LicenseAPI("http://localhost:8080")

user = {
    "username": "bluniparker",
    "password": "your-password",
    "hwid": "your-hwid"
}

async def main():
    if (await api.login(user)):
        print("Logged in successfully!")
    else:
        print("Failed to login.")

if __name__ == "__main__":
    asyncio.run(main())
```
