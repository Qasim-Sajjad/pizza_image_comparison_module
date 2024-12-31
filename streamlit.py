import streamlit as st
import openai
import base64,io
from typing import Dict, List
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv(dotenv_path='pizza_image_comparison_module\.env')

def resize_image(uploaded_image, width=1024):
    """Resize the uploaded image to a specific width while maintaining the aspect ratio."""
    # Open the uploaded image using PIL
    img = Image.open(uploaded_image)
    format = img.format
    # Calculate the new height maintaining the aspect ratio
    aspect_ratio = img.height / img.width
    new_height = int(width * aspect_ratio)
    # Resize the image
    img_resized = img.resize((width, new_height))

    # Save the resized image to a BytesIO object to keep it in memory
    img_byte_arr = io.BytesIO()
    img_resized.save(img_byte_arr, format=format)  # or 'JPEG' depending on your image format
    img_byte_arr.seek(0)  # Rewind the BytesIO object so it can be used again

    return img_byte_arr

def encode_image_from_upload(uploaded_file):
    """Encode uploaded image to base64 string"""
    bytes_data = uploaded_file.getvalue()
    return base64.b64encode(bytes_data).decode('utf-8')

def create_pizza_comparison_prompt(
    image1_name: str, 
    image2_name: str,
    criteria: Dict[str, List[str]]
) -> str:
    
    # Build criteria section
    criteria_section = ""
    for idx, (element, descriptions) in enumerate(criteria.items(), 1):
        criteria_section += f"{idx}. {element}\n"
        for desc in descriptions:
            criteria_section += f"   - {desc}\n"

    prompt = f"""As an expert pizza analyst, conduct a detailed comparative analysis between the reference pizza image ({image1_name}) and the evaluation pizza image ({image2_name}). Provide a thorough assessment based on the specified criteria, maintaining objectivity and precision.

Essential Evaluation Criteria:
{criteria_section}

Required Analysis Structure:
1. Reference Standard Analysis:
   - Establish baseline characteristics for each criterion
   - Document key visual elements as benchmarks
   - Note quality indicators that set the standard

2. Comparative Evaluation:
   - Systematically assess each criterion against the reference
   - Identify deviations or alignments with specific examples
   - Quantify differences where possible (e.g., coverage percentage, distribution patterns)

3. Critical Analysis:
   - Evaluate the impact of observed differences
   - Assess whether deviations affect pizza authenticity
   - Consider whether variations are acceptable within standard ranges

4. Final Assessment:
   - Clear determination: Valid Pizza / Not Valid Pizza
   - List key factors supporting the decision
   - Note any critical deficiencies or exceptional qualities

Important Guidelines:
- Maintain strict focus on provided criteria
- Use specific examples from both images
- Be precise and objective in comparisons
- Limit total analysis to 250 words
- Avoid subjective quality judgments
- Reference specific visual evidence for each point

[ANALYSIS]
"""
    return prompt

def analyze_pizza_images(prompt, image1_data, image2_data, api_key):
    openai.api_key = api_key
    
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image1_data}"
                    }
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image2_data}"
                    }
                }
            ]
        }
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=400,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    st.title("Pizza Comparison Analysis Tool")
    # Get API key from secrets
    api_key = st.secrets["openai_api_key"]
    
    # Image upload
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Reference Pizza Image")
        image1 = st.file_uploader("Upload reference pizza image", type=["jpg", "jpeg", "png"])
        if image1:
            st.image(image1, use_container_width=True)
    
    with col2:
        st.subheader("Comparison Pizza Image")
        image2 = st.file_uploader("Upload comparison pizza image", type=["jpg", "jpeg", "png"])
        if image2:
            st.image(image2, use_container_width=True)
    
    # Criteria input section
    st.subheader("Evaluation Criteria")
    
    criteria = {}
    num_criteria = st.number_input("Number of criteria", min_value=1, max_value=5, value=3)
    
    for i in range(num_criteria):
        col1, col2 = st.columns([1, 2])
        with col1:
            criterion_name = st.text_input(f"Criterion {i+1} Name", key=f"name_{i}")
        with col2:
            descriptions = st.text_area(
                f"Descriptions (one per line)", 
                key=f"desc_{i}",
                height=100
            )
        if criterion_name and descriptions:
            criteria[criterion_name] = [desc.strip() for desc in descriptions.split("\n") if desc.strip()]
    
    # Analysis button
    if st.button("Analyze Images"):
        if not api_key:
            st.error("Please enter your OpenAI API key")
        elif not image1 or not image2:
            st.error("Please upload both images")
        elif not criteria:
            st.error("Please add at least one criterion with descriptions")
        else:
            with st.spinner("Analyzing images..."):
                # Encode images
                # image1 = resize_image(uploaded_image=image1,width=1024)
                # image2 = resize_image(uploaded_image=image2,width=1024)
                image1_data = encode_image_from_upload(image1)
                image2_data = encode_image_from_upload(image2)
                
                # Create prompt and analyze
                prompt = create_pizza_comparison_prompt(
                    image1.name,
                    image2.name,
                    criteria
                )
                
                result = analyze_pizza_images(prompt, image1_data, image2_data, api_key)
                
                # Display results
                st.subheader("Analysis Results")
                st.write(result)

if __name__ == "__main__":
    main()