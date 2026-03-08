from sqlalchemy.orm import Session
import models, schemas
import datetime

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.RegisterRequest, password_hash: str):
    db_user = models.User(username=user.username, email=user.email, password_hash=password_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_account(db: Session, acno: int):
    return db.query(models.Account).filter(models.Account.acno == acno).first()

def get_accounts(db: Session, skip: int = 0, limit: int = 100, user_id: int = None):
    query = db.query(models.Account)
    if user_id is not None:
        query = query.filter(models.Account.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_account(db: Session, account: schemas.AccountCreate):
    # Auto-generate next account number
    highest_acno = db.query(models.Account).order_by(models.Account.acno.desc()).first()
    next_acno = highest_acno.acno + 1 if highest_acno else 1000000001
    
    db_account = models.Account(
        acno=next_acno,
        name=account.name,
        acc_type=account.acc_type,
        deposit=account.deposit,
        user_id=account.user_id
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def update_account(db: Session, acno: int, account_update: schemas.AccountUpdate):
    db_account = get_account(db, acno)
    if not db_account:
        return None
    if account_update.name is not None:
        db_account.name = account_update.name
    if account_update.acc_type is not None:
        db_account.acc_type = account_update.acc_type
    if account_update.deposit is not None:
        db_account.deposit = account_update.deposit
    if account_update.user_id is not None:
        db_account.user_id = account_update.user_id
    db.commit()
    db.refresh(db_account)
    return db_account

def delete_account(db: Session, acno: int):
    db_account = get_account(db, acno)
    if not db_account:
        return False
    # Optional: Delete associated transactions or cascade
    db.query(models.Transaction).filter(models.Transaction.acno == acno).delete()
    db.delete(db_account)
    db.commit()
    return True

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(
        acno=transaction.acno,
        trans_type=transaction.trans_type,
        amount=transaction.amount,
        related_acno=transaction.related_acno,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions_by_account(db: Session, acno: int):
    return db.query(models.Transaction).filter(models.Transaction.acno == acno).order_by(models.Transaction.timestamp.desc()).all()

def get_all_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).order_by(models.Transaction.timestamp.desc()).offset(skip).limit(limit).all()
