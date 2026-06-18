from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, Profile, Subscription, Payment, ActivityLog
from ..schemas import ProfileOut, ProfileUpdate, SubscriptionOut, PaymentOut, ActivityLogOut
from ..auth import get_current_user

router = APIRouter(prefix="/user", tags=["Users & Billing"])

@router.get("/profile", response_model=ProfileOut)
def get_user_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("/profile", response_model=ProfileOut)
def update_user_profile(profile_in: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        
    for field, value in profile_in.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
        
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/subscription", response_model=SubscriptionOut)
def get_subscription(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sub = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not sub:
        sub = Subscription(user_id=current_user.id, plan_type="free", status="active")
        db.add(sub)
        db.commit()
        db.refresh(sub)
    return sub

@router.post("/subscription/upgrade", response_model=SubscriptionOut)
def upgrade_subscription(plan_type: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if plan_type not in ["free", "pro", "enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid plan type")
        
    sub = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not sub:
        sub = Subscription(user_id=current_user.id)
        db.add(sub)
        
    sub.plan_type = plan_type
    sub.status = "active"
    
    # Record payment log for visual billing demonstration
    amount = 29.0 if plan_type == "pro" else 99.0 if plan_type == "enterprise" else 0.0
    if amount > 0:
        payment = Payment(
            user_id=current_user.id,
            subscription_id=sub.id,
            amount=amount,
            currency="USD",
            status="completed"
        )
        db.add(payment)
        
    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        activity_type="upgrade_plan",
        description=f"Upgraded subscription plan to {plan_type.upper()}"
    )
    db.add(log)
    
    db.commit()
    db.refresh(sub)
    return sub

@router.get("/billing/history", response_model=List[PaymentOut])
def get_billing_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Payment).filter(Payment.user_id == current_user.id).order_by(Payment.payment_date.desc()).all()

@router.get("/activity", response_model=List[ActivityLogOut])
def get_activity_log(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's recent activity log entries."""
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(50)
        .all()
    )
