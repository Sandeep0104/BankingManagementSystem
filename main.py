from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List

import models, schemas, crud, auth
from database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="NexaBank API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except auth.jwt.PyJWTError:
        raise credentials_exception
    user = crud.get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user

def require_staff(current_user: models.User = Depends(get_current_user)):
    if current_user.role not in ["teller", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized (Staff only)")
    return current_user

def require_manager(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Not authorized (Manager only)")
    return current_user

# --- Authentication & Users ---

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.RegisterRequest, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = crud.create_user(db=db, user=user, password_hash=hashed_password)
    return new_user

@app.post("/login", response_model=schemas.TokenResponse)
def login(user: schemas.LoginRequest, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, username=user.username)
    if not db_user or not auth.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if db_user.is_2fa_enabled:
        if not user.totp_code or not auth.verify_totp(db_user.totp_secret, user.totp_code):
            raise HTTPException(status_code=401, detail="Invalid 2FA code")

    access_token = auth.create_access_token(data={"sub": db_user.username, "role": db_user.role})
    return {"access_token": access_token, "token_type": "bearer", "role": db_user.role, "is_2fa_enabled": bool(db_user.is_2fa_enabled)}

@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.post("/users/2fa/setup", response_model=schemas.TOTPSetupResponse)
def setup_2fa(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    secret = auth.generate_totp_secret()
    
    # Temporarily store secret (in a real app, maybe a separate "pending" state or cache)
    current_user.totp_secret = secret
    db.commit()
    
    uri = auth.get_totp_uri(secret, current_user.username)
    return {"secret": secret, "uri": uri}

@app.post("/users/2fa/verify")
def verify_2fa(req: schemas.TOTPVerifyRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.totp_secret:
        raise HTTPException(status_code=400, detail="2FA setup not initiated")
    
    if auth.verify_totp(current_user.totp_secret, req.code):
        current_user.is_2fa_enabled = 1
        db.commit()
        return {"message": "2FA successfully verified and enabled"}
    raise HTTPException(status_code=400, detail="Invalid code")


# --- Accounts ---

@app.post("/accounts/", response_model=schemas.AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_staff)):
    if account.username:
        user = crud.get_user(db, username=account.username)
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{account.username}' not found")
        account.user_id = user.id
    return crud.create_account(db=db, account=account)

@app.get("/accounts/", response_model=List[schemas.AccountResponse])
def read_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(require_staff)):
    accounts = crud.get_accounts(db, skip=skip, limit=limit)
    return accounts

@app.get("/accounts/my", response_model=List[schemas.AccountResponse])
def read_my_accounts(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    accounts = crud.get_accounts(db, user_id=current_user.id)
    return accounts

@app.post("/accounts/link", response_model=schemas.AccountResponse)
def link_account(req: schemas.AccountLinkRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_account = crud.get_account(db, acno=req.acno)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    if db_account.user_id:
        raise HTTPException(status_code=400, detail="Account is already linked to a user profile")
    if db_account.name.lower() != req.name.lower():
        raise HTTPException(status_code=400, detail="Account Name does not match bank records")
    
    db_account.user_id = current_user.id
    db.commit()
    db.refresh(db_account)
    return db_account

def get_auth_account(acno: int, db: Session, user: models.User):
    # Helper to check if a user is allowed to access an account
    db_account = crud.get_account(db, acno=acno)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    if user.role == "customer" and db_account.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this account")
    return db_account

@app.get("/accounts/{acno}", response_model=schemas.AccountResponse)
def read_account(acno: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return get_auth_account(acno, db, current_user)

@app.put("/accounts/{acno}", response_model=schemas.AccountResponse)
def update_account(acno: int, account: schemas.AccountUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(require_manager)):
    if account.username:
        user = crud.get_user(db, username=account.username)
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{account.username}' not found")
        account.user_id = user.id

    db_account = crud.update_account(db, acno=acno, account_update=account)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@app.delete("/accounts/{acno}")
def delete_account(acno: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_manager)):
    success = crud.delete_account(db, acno=acno)
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted successfully"}

# --- Transactions ---

@app.post("/accounts/{acno}/deposit", response_model=schemas.AccountResponse)
def deposit(acno: int, req: schemas.DepositWithdrawRequest, db: Session = Depends(get_db), current_user: models.User = Depends(require_staff)):
    db_account = crud.get_account(db, acno=acno)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Update balance
    db_account.deposit += req.amount
    db.commit()
    db.refresh(db_account)

    # Log transaction
    txn = schemas.TransactionCreate(acno=acno, trans_type="DEPOSIT", amount=req.amount)
    crud.create_transaction(db, txn)

    return db_account

@app.post("/accounts/{acno}/withdraw", response_model=schemas.AccountResponse)
def withdraw(acno: int, req: schemas.DepositWithdrawRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_account = get_auth_account(acno, db, current_user)
    
    # Check minimum balance
    if db_account.acc_type == 'S' and db_account.deposit - req.amount < 500:
        raise HTTPException(status_code=400, detail="Insufficient balance (Min 500)")
    if db_account.acc_type == 'C' and db_account.deposit - req.amount < 1000:
        raise HTTPException(status_code=400, detail="Insufficient balance (Min 1000)")

    # Update balance
    db_account.deposit -= req.amount
    db.commit()
    db.refresh(db_account)

    # Log transaction
    txn = schemas.TransactionCreate(acno=acno, trans_type="WITHDRAW", amount=req.amount)
    crud.create_transaction(db, txn)

    return db_account

@app.post("/accounts/{from_acno}/transfer", response_model=dict)
def transfer(from_acno: int, req: schemas.TransferRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    from_acc = get_auth_account(from_acno, db, current_user)
    to_acc = crud.get_account(db, acno=req.to_acno)

    if not from_acc or not to_acc:
        raise HTTPException(status_code=404, detail="One or both accounts not found")

    # Check minimum balance on sender
    if from_acc.acc_type == 'S' and from_acc.deposit - req.amount < 500:
        raise HTTPException(status_code=400, detail="Insufficient balance (Min 500)")
    if from_acc.acc_type == 'C' and from_acc.deposit - req.amount < 1000:
        raise HTTPException(status_code=400, detail="Insufficient balance (Min 1000)")

    # Perform transfer
    from_acc.deposit -= req.amount
    to_acc.deposit += req.amount
    db.commit()

    # Log transactions
    txn_out = schemas.TransactionCreate(acno=from_acno, trans_type="TRANSFER_SENT", amount=req.amount, related_acno=req.to_acno)
    crud.create_transaction(db, txn_out)
    
    txn_in = schemas.TransactionCreate(acno=req.to_acno, trans_type="TRANSFER_RECEIVED", amount=req.amount, related_acno=from_acno)
    crud.create_transaction(db, txn_in)

    return {"message": "Transfer Successful"}

@app.get("/accounts/{acno}/transactions", response_model=List[schemas.TransactionResponse])
def get_transactions(acno: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_account = get_auth_account(acno, db, current_user)
    return crud.get_transactions_by_account(db, acno=acno)

@app.get("/transactions", response_model=List[schemas.TransactionResponse])
def get_all_txns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(require_staff)):
    return crud.get_all_transactions(db, skip=skip, limit=limit)
