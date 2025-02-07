import os
import random
import requests
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API key from environment variable
SEMAPHORE_API_KEY = os.getenv('SEMAPHORE_API_KEY')
sender_name = os.getenv('SEMAPHORE_SENDER_NAME')
if not SEMAPHORE_API_KEY:
    raise ValueError("Please set SEMAPHORE_API_KEY environment variable")

def generate_otp() -> str:
    """Generate a 6-digit OTP code"""
    return ''.join(random.choices('0123456789', k=6))

def send_otp(phone_number: str, message: str) -> Dict[str, Any]:
    """Send OTP via Semaphore SMS API"""
    url = "https://api.semaphore.co/api/v4/otp"
    params = {
        "apikey": SEMAPHORE_API_KEY,
        "number": phone_number,
        "message": message,
        "sendername": sender_name
    }
    response = requests.post(url, data=params)
    return response.json()

def main(req, res):
    """Appwrite Cloud Function handler"""
    try:
        # Get phone number from request
        phone_number = req.payload.get('phone_number')
        if not phone_number:
            return res.json({
                "success": False,
                "message": "Phone number is required"
            }, 400)

        # Generate OTP
        otp_code = generate_otp()
        message = f"Your OTP code is: {otp_code}. Please use it within 5 minutes."

        # Send OTP via SMS
        response = send_otp(phone_number, message)
        
        if response.get('status') == 'Pending':
            return res.json({
                "success": True,
                "message": "OTP sent successfully",
                "otp": otp_code
            })
        else:
            return res.json({
                "success": False,
                "message": "Failed to send OTP",
                "error": response
            }, 500)

    except Exception as e:
        return res.json({
            "success": False,
            "message": str(e)
        }, 500)
