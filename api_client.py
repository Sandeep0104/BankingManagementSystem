import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def _headers(token=None):
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def _safe_json(response):
    """Safely parse JSON from a response, returning a fallback on failure."""
    try:
        return response.json()
    except Exception:
        return {"detail": f"Server error ({response.status_code}). Please try again in a moment."}

def _get_error(response, default="Something went wrong"):
    """Extract error detail from a response safely."""
    data = _safe_json(response)
    if isinstance(data, dict):
        return data.get("detail", default)
    return default

def register_user(username, password, email=None):
    try:
        response = requests.post(
            f"{API_BASE_URL}/register",
            json={"username": username, "password": password, "email": email},
            timeout=30
        )
        if response.status_code == 200:
            return True, _safe_json(response)
        return False, _get_error(response, "Error registering")
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. It may be starting up — please try again in 30 seconds."
    except requests.exceptions.Timeout:
        return False, "Server is taking too long to respond. Please try again."

def authenticate_user(username, password, totp_code=None):
    data = {"username": username, "password": password}
    if totp_code:
        data["totp_code"] = totp_code
    try:
        response = requests.post(f"{API_BASE_URL}/login", json=data, timeout=30)
        if response.status_code == 200:
            return True, _safe_json(response)
        return False, _get_error(response, "Error authenticating")
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. It may be starting up — please try again in 30 seconds."
    except requests.exceptions.Timeout:
        return False, "Server is taking too long to respond. Please try again."

def setup_2fa(token):
    try:
        response = requests.post(f"{API_BASE_URL}/users/2fa/setup", headers=_headers(token), timeout=15)
        if response.status_code == 200:
            return True, _safe_json(response)
        return False, _get_error(response, "Error generating 2FA secret")
    except Exception:
        return False, "Connection error. Please try again."

def verify_2fa(token, code):
    try:
        response = requests.post(f"{API_BASE_URL}/users/2fa/verify", json={"code": code}, headers=_headers(token), timeout=15)
        if response.status_code == 200:
            return True, "2FA Verified"
        return False, _get_error(response, "Error verifying 2FA")
    except Exception:
        return False, "Connection error. Please try again."

def load_accounts(token, role="customer"):
    endpoint = f"{API_BASE_URL}/accounts/" if role in ["teller", "manager"] else f"{API_BASE_URL}/accounts/my"
    try:
        response = requests.get(endpoint, headers=_headers(token), timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

def link_account(token, acno, name):
    try:
        response = requests.post(
            f"{API_BASE_URL}/accounts/link",
            json={"acno": acno, "name": name},
            headers=_headers(token), timeout=15
        )
        if response.status_code == 200:
            return True, "Successfully linked"
        return False, _get_error(response, "Error linking account")
    except Exception:
        return False, "Connection error. Please try again."

def create_account(token, name, acc_type, deposit, username=""):
    data = {"name": name, "acc_type": acc_type, "deposit": deposit}
    if username:
        data["username"] = username
    try:
        response = requests.post(f"{API_BASE_URL}/accounts/", json=data, headers=_headers(token), timeout=15)
        return _safe_json(response)
    except Exception:
        return {"detail": "Connection error. Please try again."}

def deposit_amount(token, acno, amount):
    try:
        response = requests.post(f"{API_BASE_URL}/accounts/{acno}/deposit", json={"amount": amount}, headers=_headers(token), timeout=15)
        return response.status_code == 200, _safe_json(response)
    except Exception:
        return False, {"detail": "Connection error. Please try again."}

def withdraw_amount(token, acno, amount):
    try:
        response = requests.post(f"{API_BASE_URL}/accounts/{acno}/withdraw", json={"amount": amount}, headers=_headers(token), timeout=15)
        if response.status_code == 200:
            return True, _safe_json(response)
        return False, _get_error(response, "Error")
    except Exception:
        return False, "Connection error. Please try again."

def transfer_funds(token, from_acno, to_acno, amount):
    try:
        response = requests.post(f"{API_BASE_URL}/accounts/{from_acno}/transfer", json={"to_acno": to_acno, "amount": amount}, headers=_headers(token), timeout=15)
        if response.status_code == 200:
            return True, "Transfer Successful"
        return False, _get_error(response, "Error")
    except Exception:
        return False, "Connection error. Please try again."

def get_account_transactions(token, acno):
    try:
        response = requests.get(f"{API_BASE_URL}/accounts/{acno}/transactions", headers=_headers(token), timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

def load_transactions(token):
    try:
        response = requests.get(f"{API_BASE_URL}/transactions", headers=_headers(token), timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

def update_account(token, acno, name, acc_type, deposit, username=""):
    data = {"name": name, "acc_type": acc_type, "deposit": deposit}
    if username:
        data["username"] = username
    try:
        response = requests.put(f"{API_BASE_URL}/accounts/{acno}", json=data, headers=_headers(token), timeout=15)
        return response.status_code == 200
    except Exception:
        return False

def delete_account(token, acno):
    try:
        response = requests.delete(f"{API_BASE_URL}/accounts/{acno}", headers=_headers(token), timeout=15)
        return response.status_code == 200
    except Exception:
        return False

