import streamlit as st
import asyncio
from utils.config import Config
from api.replicate import ReplicateClient
from api.vertex import VertexClient
import requests
import base64

# Initialize session state
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'selected_service' not in st.session_state:
    st.session_state.selected_service = None
if 'model_info' not in st.session_state:
    st.session_state.model_info = {}

def initialize_clients():
    """Initialize both Replicate and Vertex AI clients using Config."""
    clients = {}
    
    try:
        Config.validate()
        clients['replicate'] = ReplicateClient(api_token=Config.REPLICATE_API_TOKEN)
        clients['vertex'] = VertexClient(
            project_id=Config.GOOGLE_PROJECT_ID,
            location=Config.GOOGLE_LOCATION
        )
        return clients
    except EnvironmentError as e:
        st.error(f"Configuration Error: {str(e)}")
        return None

def initialize_models(clients):
    """Initialize model information from all services."""
    replicate_models = clients['replicate'].get_available_models()
    vertex_models = clients['vertex'].get_available_models()

    # Combine models with service identifier
    all_models = (
        [{"service": "replicate", **model} for model in replicate_models] +
        [{"service": "vertex", **model} for model in vertex_models]
    )

    # Create a mapping for easy lookup
    return {
        f"{model['name']}": {
            "service": model['service'],
            "path": model['path'],
            "description": model['description']
        }
        for model in all_models
    }

def download_image(url: str) -> bytes:
    """Download image from URL"""
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def on_model_change():
    """Handle model selection change"""
    selected_model = st.session_state.model_info[st.session_state.model_select]
    st.session_state.selected_service = selected_model["service"]

async def main():
    st.set_page_config(
        page_title="Teams Background Generator",
        page_icon=":camera:",
    )
    st.title("Teams Background Generator")
    st.markdown("Generate professional backgrounds for Microsoft Teams using AI")

    st.success("NEW: Support for Imagen3 models on Vertex AI 🚀")

    # Initialize clients
    clients = initialize_clients()
    if not clients:
        return

    # Initialize models
    st.session_state.model_info = initialize_models(clients)

    # Model selection outside the form
    selected_model_name = st.selectbox(
        "Select model:",
        options=list(st.session_state.model_info.keys()),
        help="Choose between different AI models for image generation",
        key="model_select",
        on_change=on_model_change
    )

    # Get the selected model info
    selected_model = st.session_state.model_info[selected_model_name]
    service = selected_model["service"]
    st.session_state.selected_service = service

    # UI Elements
    with st.form("image_generation_form"):
        # Text prompt
        prompt = st.text_area(
            "Describe your background:",
            placeholder="a minimal, professional office space with modern architecture and natural lighting",
            help="Describe the background you want to generate"
        )

        # Advanced options in an expander
        with st.expander("Advanced Settings"):
            col1, col2 = st.columns(2)
            
            with col1:
                if service == "vertex":
                    aspect_ratio = st.selectbox(
                        "Aspect Ratio:",
                        options=["16:9", "1:1", "9:16", "4:3", "3:4"],
                        index=0,
                        help="Supported aspect ratios for Imagen"
                    )
                else:
                    aspect_ratio = st.selectbox(
                        "Aspect Ratio:",
                        options=["16:9", "3:2", "1:1", "2:3"],
                        index=0,
                        help="16:9 is recommended for Teams backgrounds"
                    )
                    output_format = st.selectbox(
                        "Output Format:",
                        options=["png", "jpg"],
                        index=0,
                        help="PNG recommended for better quality"
                    )

            with col2:
                if service == "vertex":
                    # Hidden settings with fixed values
                    safety_tolerance = 1  # corresponds to block_only_high
                    image_prompt_strength = 0.1
                    raw = False
                else:
                    safety_tolerance = st.slider(
                        "Safety Level:",
                        min_value=0, max_value=3, value=2,
                        help="Higher values apply stricter content filtering"
                    )
                    image_prompt_strength = st.slider(
                        "Style Strength:",
                        min_value=0.0, max_value=1.0, value=0.1, step=0.1,
                        help="Higher values create more artistic images"
                    )
                    raw = st.checkbox("Raw Output", value=False, help="RAW Images are less processed and can produce more varied results")

        # Submit button
        submit = st.form_submit_button("Generate Background")

    # Handle form submission
    if submit and prompt:
        try:
            with st.spinner("Generating your Teams background..."):
                # Get the model path from the selected model
                model_path = selected_model["path"]

                # Generate image using the appropriate service
                if service == "replicate":
                    result = await clients['replicate'].generate_image(
                        prompt=prompt,
                        model_path=model_path,
                        raw=raw,
                        aspect_ratio=aspect_ratio,
                        output_format=output_format,
                        safety_tolerance=safety_tolerance,
                        image_prompt_strength=image_prompt_strength
                    )
                else:  # vertex
                    result = await clients['vertex'].generate_image(
                        prompt=prompt,
                        model_path=model_path,
                        raw=raw,
                        aspect_ratio=aspect_ratio,
                        safety_tolerance=safety_tolerance,
                        image_prompt_strength=image_prompt_strength
                    )

                if result.get('status') == 'success':
                    # Store the result in session state with appropriate format
                    if service == "vertex":
                        format = "png"  # Vertex AI always returns PNG
                    else:
                        format = output_format

                    st.session_state.generated_images = [{
                        'url': url,
                        'format': format,
                        'metadata': result.get('metadata', {}),
                        'service': service
                    } for url in result.get('urls', [])]

        except Exception as e:
            st.error(f"Error: {str(e)}")
            return

    # Display generated images (outside the form)
    if st.session_state.generated_images:
        st.subheader("Your Generated Background")

        for idx, image_data in enumerate(st.session_state.generated_images):
            # Create columns for image and buttons
            col1, col2 = st.columns([4, 1])

            # Display image
            with col1:
                st.image(image_data['url'], use_container_width=True)
                st.caption(f"Generated using {image_data['service'].title()} AI")

            # Display buttons
            with col2:
                try:
                    # Handle download differently based on service
                    if image_data['service'] == 'vertex':
                        # Extract base64 data from data URL
                        base64_data = image_data['url'].split(',')[1]
                        image_bytes = base64.b64decode(base64_data)
                    else:
                        # Regular URL download for Replicate
                        image_bytes = download_image(image_data['url'])

                    st.download_button(
                        label="Download for Teams",
                        data=image_bytes,
                        file_name=f"teams_background_{idx+1}.{image_data['format']}",
                        mime=f"image/{image_data['format']}",
                        help="Click to download the image for use in Teams"
                    )

                    # Only show direct link for non-data URLs (Replicate)
                    if image_data['service'] != 'vertex':
                        st.markdown(f"[Direct link]({image_data['url']})")

                except Exception as e:
                    st.error(f"Error preparing download: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
