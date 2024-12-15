import os
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Replicate
    REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
    
    # Google Cloud / Vertex AI
    GOOGLE_PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID')
    GOOGLE_LOCATION = os.getenv('GOOGLE_LOCATION', 'us-central1')  # Default to us-central1
    GOOGLE_CREDENTIALS_BASE64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')  # New base64 credentials

    @classmethod
    def get_google_credentials(cls):
        """Decode base64 credentials if provided"""
        if cls.GOOGLE_CREDENTIALS_BASE64:
            return base64.b64decode(cls.GOOGLE_CREDENTIALS_BASE64).decode('utf-8')
        return None

    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set"""
        required_vars = [
            'REPLICATE_API_TOKEN',
            'GOOGLE_PROJECT_ID',
            'GOOGLE_CREDENTIALS_BASE64'  # Changed from GOOGLE_APPLICATION_CREDENTIALS
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
