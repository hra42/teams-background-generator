from vertexai.preview.vision_models import ImageGenerationModel
from typing import Dict, Any, List
import base64
import json
from google.oauth2 import service_account  # Add this import
import vertexai

class VertexClient:
    # Available Imagen models
    AVAILABLE_MODELS = [
        {
            "name": "Imagen 3",
            "path": "imagen-3.0-generate-001",
            "description": "High quality image generation"
        },
        {
            "name": "Imagen 3 Fast",
            "path": "imagen-3.0-fast-generate-001",
            "description": "Fast image generation"
        }
    ]

    def __init__(self, project_id: str, credentials_json: str, location: str = "us-central1"):
        """
        Initialize the Vertex AI client.
        
        Args:
            project_id: Google Cloud project ID
            credentials_json: JSON credentials as string
            location: Google Cloud location
        """
        
        # Create temporary credentials file
        credentials_dict = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        
        vertexai.init(project=project_id, location=location, credentials=credentials)
        self.project_id = project_id
        self.location = location
        self.model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")

    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get list of available Imagen models.
        """
        return [
            {
                "name": model["name"],
                "path": model["path"],
                "description": model["description"]
            }
            for model in self.AVAILABLE_MODELS
        ]

    async def generate_image(
        self,
        prompt: str,
        model_path: str,
        raw: bool = False,
        aspect_ratio: str = "1:1",
        safety_tolerance: int = 1,
        image_prompt_strength: float = 0.1,
        number_of_images: int = 1
    ) -> Dict[str, Any]:
        """
        Generate images using Vertex AI's Imagen model.
        
        Args:
            prompt (str): The text prompt for image generation
            model_path (str): Model identifier (imagen-3.0-generate-001 or imagen-3.0-fast-generate-001)
            raw (bool): Not used in Vertex AI
            aspect_ratio (str): One of "1:1", "16:9", "9:16", "4:3", "3:4"
            safety_tolerance (int): Not used - fixed to block_only_high
            image_prompt_strength (float): Not used in Vertex AI
            number_of_images (int): Number of images to generate (1-8 for imagen-3.0, 1-4 for others)
        """
        try:
            # Update model if different from current
            if model_path != self.model._model_id:
                self.model = ImageGenerationModel.from_pretrained(model_path)

            # Generate the images
            images = self.model.generate_images(
                prompt=prompt,
                number_of_images=number_of_images,
                language="en",
                aspect_ratio=aspect_ratio,
                safety_filter_level="block_only_high"
            )

            # Process and store the images
            urls = []
            
            # Convert and process each generated image
            for generated_image in images:
                # Access the image bytes directly
                image_bytes = generated_image._image_bytes
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                urls.append(f"data:image/png;base64,{base64_image}")

            return {
                'status': 'success',
                'urls': urls,
                'model_path': model_path,
                'metadata': {
                    'prompt': prompt,
                    'aspect_ratio': aspect_ratio,
                    'number_of_images': number_of_images,
                    'model': model_path,
                    'safety_filter': "block_only_high",
                    'language': "en"
                }
            }

        except Exception as e:
            raise Exception(f"Vertex AI API error: {str(e)}")

    def validate_connection(self) -> bool:
        """
        Validate the connection to Vertex AI.
        """
        try:
            return self.model is not None
        except Exception:
            return False
