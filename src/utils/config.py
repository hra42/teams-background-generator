import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Replicate
    REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
    
    # Google Cloud / Vertex AI
    GOOGLE_PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID')
    GOOGLE_LOCATION = os.getenv('GOOGLE_LOCATION', 'us-central1')  # Default to us-central1
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set"""
        required_vars = [
            'REPLICATE_API_TOKEN',
            'GOOGLE_PROJECT_ID',
            'GOOGLE_APPLICATION_CREDENTIALS'
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
        
        # Validate that the credentials file exists
        if not os.path.exists(cls.GOOGLE_APPLICATION_CREDENTIALS):
            raise EnvironmentError(
                f"Google Cloud credentials file not found at: {cls.GOOGLE_APPLICATION_CREDENTIALS}"
            )
