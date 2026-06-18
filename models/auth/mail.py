import resend
import os
from resend.errors import ResendError

from models.security.ratelimiter import Limiter

from fastapi import APIRouter, HTTPException, Request

from models.databases.database import SessionLocal
from models.security.ratelimiter import limiter


router = APIRouter(prefix="/api/v1/nth/auth/mail/send")



params: resend.Emails.SendParams = {
    "from": "Acme <onboarding@resend.dev>",
    "to": ["delivered@resend.dev"],
    "subject": "Hello from Python",
    "html": "<strong>It works beautifully!</strong>",
}

try:
    email = resend.Emails.send(params)
    print(f"Email sent successfully! ID: {email['id']}")
except ResendError as e:
    print(f"Failed to send email: {e}")