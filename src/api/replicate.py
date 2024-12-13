import replicate
from typing import Optional, Dict, Any, List

class ReplicateClient:
    # Available Flux models with their full paths
    AVAILABLE_MODELS = [
        {
            "name": "Flux 1.1 Pro",
            "path": "black-forest-labs/flux-1.1-pro",
            "description": "High quality image generation"
        },
        {
            "name": "Flux Schnell LoRA",
            "path": "black-forest-labs/flux-schnell-lora",
            "description": "Fast image generation with LoRA"
        },
        {
            "name": "Flux 1.1 Pro Ultra",
            "path": "black-forest-labs/flux-1.1-pro-ultra",
            "description": "Ultra high quality image generation"
        },
        {
            "name": "Flux Dev LoRA",
            "path": "black-forest-labs/flux-dev-lora",
            "description": "Development version with LoRA"
        },
        {
            "name": "Photon",
            "path": "luma/photon",
            "description": "High-quality image generation model optimized for creative professional workflows and ultra-high fidelity outputs"
        },
        {
            "name": "Ideogram-v2",
            "path": "ideogram-ai/ideogram-v2",
            "description": "An excellent image model with state of the art inpainting, prompt comprehension and text rendering"
        }  
    ]

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the Replicate client.
        """
        self.client = replicate.Client(api_token=api_token)
        
    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get list of available Flux models.
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
        aspect_ratio: str = "3:2",
        output_format: str = "jpg",
        safety_tolerance: int = 2,
        image_prompt_strength: float = 0.1
    ) -> Dict[str, Any]:
        """
        Generate images using Replicate's Flux models.
        
        Args:
            prompt (str): The text prompt for image generation
            model_path (str): Full path to the model
            raw (bool): Whether to return raw output
            aspect_ratio (str): Aspect ratio of the output image
            output_format (str): Output format
            safety_tolerance (int): Safety filter level
            image_prompt_strength (float): Strength of the image prompt
        """
        try:
            output = self.client.run(
                model_path,
                input={
                    "prompt": prompt,
                    "raw": raw,
                    "aspect_ratio": aspect_ratio,
                    "output_format": output_format,
                    "safety_tolerance": safety_tolerance,
                    "image_prompt_strength": image_prompt_strength
                }
            )
            
            # Convert FileOutput to URL string
            if hasattr(output, 'url'):
                urls = [output.url]
            elif isinstance(output, list) and all(hasattr(item, 'url') for item in output):
                urls = [item.url for item in output]
            else:
                raise Exception(f"Unexpected output format")
            
            return {
                'status': 'success',
                'urls': urls,
                'model_path': model_path,
                'metadata': {
                    'prompt': prompt,
                    'aspect_ratio': aspect_ratio,
                    'output_format': output_format,
                    'safety_tolerance': safety_tolerance,
                    'image_prompt_strength': image_prompt_strength
                }
            }
            
        except Exception as e:
            raise Exception(f"Replicate API error: {str(e)}")

    def validate_connection(self) -> bool:
        """
        Validate the connection to Replicate.
        """
        try:
            self.client.models.list()
            return True
        except Exception:
            return False
