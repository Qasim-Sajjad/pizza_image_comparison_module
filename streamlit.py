import streamlit as st
import openai
import base64
from typing import Dict, List
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='pizza_image_comparison_module\.env')

def encode_image_from_upload(uploaded_file):
    """Encode uploaded image to base64 string"""
    bytes_data = uploaded_file.getvalue()
    return base64.b64encode(bytes_data).decode('utf-8')

def create_pizza_comparison_prompt(
    image1_name: str, 
    image2_name: str,
    criteria: Dict[str, List[str]]
) -> str:
    criteria_section = ""
    for idx, (element, descriptions) in enumerate(criteria.items(), 1):
        criteria_section += f"{idx}. {element}\n"
        for desc in descriptions:
            criteria_section += f"   - {desc}\n"

    prompt = f"""You are a pizza expert analyzing two pizza images ({image1_name} and {image2_name}). Provide a concise analysis (maximum 250 words) based on the following criteria:

Essential Elements to Compare:
{criteria_section}

Required Output Format:
[ANALYSIS]
Reference Image: List visible elements and their characteristics
Comparison Image: Note presence/absence of elements compared to reference
Conclusion: State if image meets criteria (Valid/Not Valid Pizza)

Important: Focus only on provided criteria. Be objective and concise.
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
            temperature=0.7
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
            st.image(image1, use_column_width=True)
    
    with col2:
        st.subheader("Comparison Pizza Image")
        image2 = st.file_uploader("Upload comparison pizza image", type=["jpg", "jpeg", "png"])
        if image2:
            st.image(image2, use_column_width=True)
    
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