from fastapi import FastAPI, HTTPException
import requests
from utils.graph_auth import acquire_token

app = FastAPI()

USER_EMAIL = "alfredo@cartarep.com"  # Replace with your email if needed

@app.get("/contacts")
def get_contacts():
    token = acquire_token()
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = f"https://graph.microsoft.com/v1.0/users/{USER_EMAIL}/contacts"
    params = {"$top": "100"}

    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        contacts = response.json().get('value', [])
        simplified = [
            {
                "id": c.get("id"),
                "name": c.get("displayName"),
                "email": c.get("emailAddresses", [{}])[0].get("address"),
                "company": c.get("companyName", "")
            }
            for c in contacts
        ]
        return simplified
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
