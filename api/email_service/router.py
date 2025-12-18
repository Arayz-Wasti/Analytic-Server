from fastapi import APIRouter, BackgroundTasks
from backend.api.email_service.email_notification import EmailService

router = APIRouter()

@router.post("/notification")
def send_notification(
    email: str,
    message: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(
        EmailService.send_email,
        to_email=email,
        subject="Notification",
        message=message
    )
    return {
        "status": "queued",
        "message": "Email notification queued successfully"
    }
