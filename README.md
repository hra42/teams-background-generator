# Teams Background Generator

A Streamlit-based web application that generates professional backgrounds for Microsoft Teams using AI. The application leverages multiple AI image generation models through Replicate and Google Cloud Vertex AI platforms.

## Features

- Generate custom backgrounds using AI models from:
  - Replicate (Flux models, Photon, Ideogram-v2)
  - Google Cloud Vertex AI (Imagen 3)
- Multiple aspect ratio support (16:9, 3:2, 1:1, etc.)
- Advanced customization options
- Direct download for Teams compatibility
- Docker support for easy deployment

## Prerequisites

- Python 3.11 or higher
- Docker (optional)
- Google Cloud Project with Vertex AI API enabled
- Replicate API account

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=path_to_your_credentials.json
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_LOCATION=us-central1

# Replicate
REPLICATE_API_TOKEN=your_replicate_token
```

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/teams-background-generator.git
cd teams-background-generator
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run src/main.py
```

### Docker Deployment

1. Build and run using Docker Compose:
```bash
docker-compose up --build
```

The application will be available at `http://localhost:8501`

## Usage

1. Select an AI model from the dropdown menu
2. Enter a description of the background you want to generate
3. Adjust advanced settings if needed:
   - Aspect Ratio
   - Output Format
   - Safety Level
   - Style Strength
4. Click "Generate Background"
5. Download the generated image using the "Download for Teams" button

## Available Models

### Replicate Models
- Flux 1.1 Pro
- Flux Schnell LoRA
- Flux 1.1 Pro Ultra
- Flux Dev LoRA
- Photon
- Ideogram-v2

### Vertex AI Models
- Imagen 3
- Imagen 3 Fast

## Project Structure

```
├── src/
│   ├── api/
│   │   ├── replicate.py
│   │   └── vertex.py
│   ├── utils/
│   │   └── config.py
│   └── main.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is released into the public domain under The Unlicense. See `LICENSE.md` for more details.

## Acknowledgments

- Streamlit for the web framework
- Replicate for AI model access
- Google Cloud Vertex AI for Imagen models
