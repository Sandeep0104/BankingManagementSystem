from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)
    password_hash = Column(String)
    role = Column(String, default="customer")  # customer, teller, manager
    totp_secret = Column(String, nullable=True)
    is_2fa_enabled = Column(Integer, default=0) # SQLite doesn't have boolean by default

    accounts = relationship("Account", back_populates="owner")

class Account(Base):
    __tablename__ = "accounts"

    acno = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    acc_type = Column(String)  # 'S' or 'C'
    deposit = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Link to user

    owner = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    acno = Column(Integer, ForeignKey("accounts.acno"))
    trans_type = Column(String) # DEPOSIT, WITHDRAW, TRANSFER_SENT, TRANSFER_RECEIVED
    amount = Column(Float)
    related_acno = Column(Integer, nullable=True)

    account = relationship("Account", back_populates="transactions")
