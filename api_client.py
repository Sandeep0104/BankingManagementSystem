import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def _headers(token=None):
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def register_user(username, password, email=None):
    response = requests.post(
        f"{API_BASE_URL}/register",
        json={"username": username, "password": password, "email": email}
    )
    if response.status_code == 200:
        return True, response.json()
    return False, response.json().get("detail", "Error registering")

def authenticate_user(username, password, totp_code=None):
    data = {"username": username, "password": password}
    if totp_code:
        data["totp_code"] = totp_code
    response = requests.post(f"{API_BASE_URL}/login", json=data)
    if response.status_code == 200:
        return True, response.json()
    return False, response.json().get("detail", "Error authenticating")

def setup_2fa(token):
    response = requests.post(f"{API_BASE_URL}/users/2fa/setup", headers=_headers(token))
    if response.status_code == 200:
        return True, response.json()
    return False, response.json().get("detail", "Error generating 2FA secret")

def verify_2fa(token, code):
    response = requests.post(f"{API_BASE_URL}/users/2fa/verify", json={"code": code}, headers=_headers(token))
    if response.status_code == 200:
        return True, "2FA Verified"
    return False, response.json().get("detail", "Error verifying 2FA")

def load_accounts(token, role="customer"):
    endpoint = f"{API_BASE_URL}/accounts/" if role in ["teller", "manager"] else f"{API_BASE_URL}/accounts/my"
    response = requests.get(endpoint, headers=_headers(token))
    if response.status_code == 200:
        return response.json()
    return []

def link_account(token, acno, name):
    response = requests.post(
        f"{API_BASE_URL}/accounts/link",
        json={"acno": acno, "name": name},
        headers=_headers(token)
    )
    if response.status_code == 200:
        return True, "Successfully linked"
    return False, response.json().get("detail", "Error linking account")

def create_account(token, name, acc_type, deposit, username=""):
    data = {"name": name, "acc_type": acc_type, "deposit": deposit}
    if username:
        data["username"] = username
    response = requests.post(f"{API_BASE_URL}/accounts/", json=data, headers=_headers(token))
    return response.json()

def deposit_amount(token, acno, amount):
    response = requests.post(f"{API_BASE_URL}/accounts/{acno}/deposit", json={"amount": amount}, headers=_headers(token))
    return response.status_code == 200, response.json()

def withdraw_amount(token, acno, amount):
    response = requests.post(f"{API_BASE_URL}/accounts/{acno}/withdraw", json={"amount": amount}, headers=_headers(token))
    if response.status_code == 200:
        return True, response.json()
    return False, response.json().get("detail", "Error")

def transfer_funds(token, from_acno, to_acno, amount):
    response = requests.post(f"{API_BASE_URL}/accounts/{from_acno}/transfer", json={"to_acno": to_acno, "amount": amount}, headers=_headers(token))
    if response.status_code == 200:
        return True, "Transfer Successful"
    return False, response.json().get("detail", "Error")

def get_account_transactions(token, acno):
    response = requests.get(f"{API_BASE_URL}/accounts/{acno}/transactions", headers=_headers(token))
    if response.status_code == 200:
        return response.json()
    return []

def load_transactions(token):
    response = requests.get(f"{API_BASE_URL}/transactions", headers=_headers(token))
    if response.status_code == 200:
        return response.json()
    return []

def update_account(token, acno, name, acc_type, deposit, username=""):
    data = {"name": name, "acc_type": acc_type, "deposit": deposit}
    if username:
        data["username"] = username
    response = requests.put(f"{API_BASE_URL}/accounts/{acno}", json=data, headers=_headers(token))
    return response.status_code == 200

def delete_account(token, acno):
    response = requests.delete(f"{API_BASE_URL}/accounts/{acno}", headers=_headers(token))
    return response.status_code == 200
