import asyncio
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.sms import SmsQueue
from app.models.notification import NotificationLog
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def sms_simulator_worker():
    """
    Simulates the Android SMS Gateway for testing end-to-end functionality without a real device.
    Polls the SmsQueue for PENDING messages, marks them as SENT, and logs the result.
    """
    logger.info("SMS Simulator Worker Started. Polling for messages...")
    while True:
        db = SessionLocal()
        try:
            # Find up to 10 pending SMS
            pending_sms = db.query(SmsQueue).filter(SmsQueue.status == "PENDING").limit(10).all()
            
            for sms in pending_sms:
                logger.info(f"[SIMULATOR] Sending SMS to {sms.recipient_phone}: {sms.message}")
                
                # Simulate network delay (Android sending SMS)
                await asyncio.sleep(2) 
                
                # Update SMS Queue
                sms.status = "SENT"
                
                # Find the corresponding NotificationLog to update its status
                # (Match by recipient and message since we don't have a direct FK right now)
                log = db.query(NotificationLog).filter(
                    NotificationLog.tenant_id == sms.tenant_id,
                    NotificationLog.channel == "SMS",
                    NotificationLog.recipient == sms.recipient_phone,
                    NotificationLog.status == "PENDING"
                ).first()
                
                if log:
                    log.status = "SENT"
                    log.provider_response = "Simulated Success via Mock Android Gateway"
                    
                db.commit()
                logger.info(f"[SIMULATOR] SMS marked as SENT for {sms.recipient_phone}")
                
        except Exception as e:
            logger.error(f"[SIMULATOR] Error: {e}")
        finally:
            db.close()
            
        # Poll every 10 seconds
        await asyncio.sleep(10)

def start_simulator():
    """
    Starts the simulator loop as an asyncio task.
    Call this on FastAPI startup.
    """
    # Only run simulator if explicitly enabled or in development
    # For now, we run it to allow testing the dashboard
    asyncio.create_task(sms_simulator_worker())
