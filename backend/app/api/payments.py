"""Premium job posts — Chapa / Telebirr placeholders (return checkout-shaped payloads)."""
import logging
import secrets

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.config import get_settings
from app.database import get_db
from app.deps import require_roles
from app.models import Job, Payment, PaymentStatus, User, UserRole
from app.schemas import PaymentInitRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/chapa/webhook")
def chapa_webhook(payload: dict = Body(default_factory=dict)):
    """Verify `x-chapa-signature` with CHAPA_WEBHOOK_SECRET in production; stub accepts any body."""
    logger.info("Chapa webhook stub: %s", list(payload.keys()) if isinstance(payload, dict) else "raw")
    return {"ok": True}


@router.post("/init")
def init_payment(
    body: PaymentInitRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.employer)),
):
    """Initialize premium placement — wire Chapa SDK in production (ETB)."""
    s = get_settings()
    job = db.query(Job).options(joinedload(Job.company)).filter(Job.id == body.job_id).first()
    if not job or job.company.owner_user_id != user.id:
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
    checkout_url = f"{s.frontend_url}/checkout?ref={ref}&provider={body.provider}"
    if not s.chapa_secret_key and body.provider == "chapa":
        logger.info("CHAPA_SECRET_KEY not set — returning stub checkout URL")
    return {
        "reference": ref,
        "amount_etb": body.amount_etb,
        "checkout_url": checkout_url,
        "message": "Complete payment in sandbox; webhook should mark job premium.",
    }
