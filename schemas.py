from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# --- Token / Auth ---
class LoginRequest(BaseModel):
    username: str
    password: str
    totp_code: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    # Include role info
    role: str
    is_2fa_enabled: bool

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserResponse(BaseModel):
    username: str
    email: Optional[str]
    role: str
    is_2fa_enabled: bool

    class Config:
        from_attributes = True

class TOTPSetupResponse(BaseModel):
    secret: str
    uri: str

class TOTPVerifyRequest(BaseModel):
    code: str

# --- Account ---
class AccountBase(BaseModel):
    name: str
    acc_type: str
    deposit: float
    user_id: Optional[int] = None
    username: Optional[str] = None

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    acc_type: Optional[str] = None
    deposit: Optional[float] = None
    username: Optional[str] = None
    user_id: Optional[int] = None

class AccountResponse(AccountBase):
    acno: int

    class Config:
        from_attributes = True

# --- Transaction ---
class AccountLinkRequest(BaseModel):
    acno: int
    name: str

class TransactionBase(BaseModel):
    acno: int
    trans_type: str
    amount: float
    related_acno: Optional[int] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# --- Operation Models ---
class DepositWithdrawRequest(BaseModel):
    amount: float

class TransferRequest(BaseModel):
    to_acno: int
    amount: float
