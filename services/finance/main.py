"""
Finance Service - FastAPI + Mastercard Integration
Provides financial services and payment processing capabilities.
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import httpx
from typing import Optional, List, Dict
import logging
import uuid
from datetime import datetime, timedelta
import hashlib
import hmac
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Finance Service",
    description="Financial services and payment processing with Mastercard integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class PaymentRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field(..., min_length=3, max_length=3, description="Currency code (e.g., USD)")
    card_number: str = Field(..., description="Card number")
    expiry_month: int = Field(..., ge=1, le=12)
    expiry_year: int = Field(..., ge=2023)
    cvv: str = Field(..., min_length=3, max_length=4)
    merchant_id: str = Field(..., description="Merchant identifier")

class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    amount: float
    currency: str
    timestamp: datetime
    reference_number: Optional[str] = None

class TransactionStatus(BaseModel):
    transaction_id: str
    status: str
    amount: float
    currency: str
    created_at: datetime
    updated_at: datetime
    details: Optional[Dict] = None

class BalanceResponse(BaseModel):
    account_id: str
    balance: float
    currency: str
    last_updated: datetime

# Mastercard API configuration
MASTERCARD_API_URL = os.getenv("MASTERCARD_API_URL", "https://sandbox.api.mastercard.com")
MASTERCARD_CONSUMER_KEY = os.getenv("MASTERCARD_CONSUMER_KEY")
MASTERCARD_PRIVATE_KEY = os.getenv("MASTERCARD_PRIVATE_KEY")

class MastercardClient:
    def __init__(self):
        self.api_url = MASTERCARD_API_URL
        self.consumer_key = MASTERCARD_CONSUMER_KEY
        self.private_key = MASTERCARD_PRIVATE_KEY
        
    def _generate_signature(self, method: str, url: str, body: str = "") -> str:
        """Generate OAuth signature for Mastercard API"""
        # This is a simplified signature generation
        # In production, use proper OAuth 1.0a signature generation
        timestamp = str(int(datetime.now().timestamp()))
        nonce = str(uuid.uuid4())
        
        # Create signature base string
        signature_base = f"{method}&{url}&{timestamp}&{nonce}&{body}"
        
        # Generate signature (simplified for demo)
        signature = hmac.new(
            self.private_key.encode() if self.private_key else b"demo_key",
            signature_base.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
        
    async def process_payment(self, payment_data: dict) -> dict:
        """Process payment through Mastercard API"""
        if not self.consumer_key:
            # Mock response for demo purposes
            return {
                "transaction_id": str(uuid.uuid4()),
                "status": "approved",
                "reference_number": f"MC{uuid.uuid4().hex[:8].upper()}",
                "timestamp": datetime.now().isoformat()
            }
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"OAuth oauth_consumer_key=\"{self.consumer_key}\""
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_url}/send/v1/partners/payments",
                    headers=headers,
                    json=payment_data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                logger.error(f"Mastercard API request failed: {e}")
                raise HTTPException(status_code=503, detail="Payment service unavailable")
            except httpx.HTTPStatusError as e:
                logger.error(f"Mastercard API returned error: {e.response.status_code}")
                raise HTTPException(status_code=e.response.status_code, detail="Payment processing failed")

# Dependencies
def get_mastercard_client():
    return MastercardClient()

# In-memory transaction store (in production, this would be a database)
transactions_store = {}
account_balances = {
    "default": {"balance": 10000.0, "currency": "USD", "last_updated": datetime.now()}
}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"service": "Finance Service", "status": "healthy", "version": "1.0.0"}

@app.post("/payments", response_model=PaymentResponse)
async def process_payment(
    payment: PaymentRequest,
    client: MastercardClient = Depends(get_mastercard_client)
):
    """Process a payment transaction"""
    try:
        # Mask sensitive card data for logging
        masked_card = payment.card_number[:4] + "*" * 8 + payment.card_number[-4:]
        logger.info(f"Processing payment for card {masked_card}, amount: {payment.amount} {payment.currency}")
        
        # Prepare payment data for Mastercard API
        payment_data = {
            "amount": payment.amount,
            "currency": payment.currency,
            "payment_method": {
                "card": {
                    "number": payment.card_number,
                    "expiry_month": payment.expiry_month,
                    "expiry_year": payment.expiry_year,
                    "cvv": payment.cvv
                }
            },
            "merchant_id": payment.merchant_id
        }
        
        # Process payment through Mastercard
        mc_response = await client.process_payment(payment_data)
        
        # Create transaction record
        transaction = PaymentResponse(
            transaction_id=mc_response["transaction_id"],
            status=mc_response["status"],
            amount=payment.amount,
            currency=payment.currency,
            timestamp=datetime.now(),
            reference_number=mc_response.get("reference_number")
        )
        
        # Store transaction
        transactions_store[transaction.transaction_id] = {
            **transaction.dict(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        return transaction
        
    except Exception as e:
        logger.error(f"Payment processing failed: {e}")
        raise HTTPException(status_code=500, detail="Payment processing failed")

@app.get("/transactions/{transaction_id}", response_model=TransactionStatus)
async def get_transaction(transaction_id: str):
    """Get transaction status"""
    if transaction_id not in transactions_store:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction_data = transactions_store[transaction_id]
    return TransactionStatus(**transaction_data)

@app.get("/transactions", response_model=List[TransactionStatus])
async def list_transactions(
    limit: int = 10,
    offset: int = 0,
    status: Optional[str] = None
):
    """List transactions with optional filtering"""
    transactions = list(transactions_store.values())
    
    # Filter by status if provided
    if status:
        transactions = [t for t in transactions if t["status"] == status]
    
    # Apply pagination
    transactions = transactions[offset:offset + limit]
    
    return [TransactionStatus(**t) for t in transactions]

@app.get("/accounts/{account_id}/balance", response_model=BalanceResponse)
async def get_account_balance(account_id: str):
    """Get account balance"""
    if account_id not in account_balances:
        raise HTTPException(status_code=404, detail="Account not found")
    
    balance_info = account_balances[account_id]
    return BalanceResponse(
        account_id=account_id,
        **balance_info
    )

@app.post("/accounts/{account_id}/balance")
async def update_account_balance(
    account_id: str,
    amount: float,
    currency: str = "USD"
):
    """Update account balance (for demo purposes)"""
    if account_id not in account_balances:
        account_balances[account_id] = {
            "balance": amount,
            "currency": currency,
            "last_updated": datetime.now()
        }
    else:
        account_balances[account_id]["balance"] = amount
        account_balances[account_id]["last_updated"] = datetime.now()
    
    return {"message": "Balance updated successfully", "account_id": account_id}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "service": "Finance Service",
        "status": "healthy",
        "mastercard_configured": bool(MASTERCARD_CONSUMER_KEY),
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)