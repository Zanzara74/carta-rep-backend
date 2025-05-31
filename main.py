from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from utils.graph_auth import acquire_token

app = FastAPI()

# Configura CORS (modifica gli origins secondo il tuo frontend)
origins = [
    "https://carta-rep-frontend.sandbox.codesandbox.io",
    "http://localhost:3000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USER_EMAIL = "alfredo@cartarep.com"
LOGODEV_SECRET_KEY = "sk_ZThBXdGFSrWLWjYzd4L_SQ"  # Metti qui la tua Logo.dev Secret Key

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

@app.get("/logo")
def get_logo(domain: str = Query(...)):
    url = f"https://api.logo.dev/api/v1/logo?domain={domain}"
    headers = {
        "Authorization": f"Bearer {LOGODEV_SECRET_KEY}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # Adatta se cambia la struttura JSON
        return {
            "url": data.get("logo", {}).get("url", ""),
            "domain": domain
        }
    else:
        return {"error": response.text}
