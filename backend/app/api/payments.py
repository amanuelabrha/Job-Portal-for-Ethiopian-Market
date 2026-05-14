"""Premium job posts — Chapa / Telebirr placeholders (return checkout-shaped payloads)."""
import secrets
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import Job, Payment, PaymentStatus, User, UserRole
from app.schemas import PaymentInitRequest
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/init")
def init_payment(
    body: PaymentInitRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.employer)),
):
    """Initialize premium placement — wire Chapa SDK in production (ETB)."""
    s = get_settings()
    job = db.query(Job).filter(Job.id == body.job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    ref = f"JOB-{job.id}-{secrets.token_hex(6)}"
    pay = Payment(
        employer_user_id=user.id,
        job_id=job.id,
        provider=body.provider,
        external_id=ref,
        amount_etb=body.amount_etb,
        status=PaymentStatus.pending,
    )
    db.add(pay)
    db.commit()
    # Chapa live: POST https://api.chapa.co/v1/transaction/initialize with Bearer secret
    checkout_url = f"{s.frontend_url}/checkout?ref={ref}&provider={body.provider}"
    if not s.chapa_secret_key and body.provider == "chapa":
        logger.info("CHAPA_SECRET_KEY not set — returning stub checkout URL")
    return {
        "reference": ref,
        "amount_etb": body.amount_etb,
        "checkout_url": checkout_url,
        "message": "Complete payment in sandbox; webhook should mark job premium.",
    }
