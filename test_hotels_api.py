import requests
from modules.amadeus_api import get_access_token

token = get_access_token()
print("Access token:", bool(token))

headers = {"Authorization": f"Bearer {token}"}
params = {
    "cityCode": "PAR",
    "adults": 1,
    "checkInDate": "2025-12-10",
    "checkOutDate": "2025-12-12",
    "currency": "USD",
}

url = "https://test.api.amadeus.com/v1/shopping/hotel-offers"
res = requests.get(url, headers=headers, params=params)
print("Status:", res.status_code)
print("Response preview:")
print(res.text[:500])  # عرض أول 500 حرف فقط