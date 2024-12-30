#Prompt for image comparison model.
from typing import Dict, List
import openai
import os, base64
from dotenv import load_dotenv


load_dotenv(dotenv_path='pizza_image_comparison_module\.env')

# Setup Prompt for the image comparison model.
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

#load and encode images and analyze both of the images.
def encode_image(image_path):
    """Encode image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_pizza_images(prompt, image1_path, image2_path, api_key):
    # Set OpenAI API key
    openai.api_key = api_key
    
    # Encode both images
    base64_image1 = encode_image(image1_path)
    base64_image2 = encode_image(image2_path)
    
    # Create message with both images
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
                        "url": f"data:image/jpeg;base64,{base64_image1}"
                    }
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image2}"
                    }
                }
            ]
        }
    ]
    
    # Send request to GPT-4 Vision
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Note the correct model name
        messages=messages,
        max_tokens=400,
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Example usage
criteria = {
    "Base/Crust": [
        "Presence of bread-based foundation",
        "Visual texture (crispy/soft/burnt)",
        "Thickness type"
    ],
    "Sauce Layer": [
        "Presence and coverage",
        "Type identification"
    ],
    "Cheese": [
        "Presence and distribution",
        "Melting characteristics"
    ]
}



# Replace with your OpenAI API key
api_key = os.getenv(key='openai_api_key')

image1_path = "pizza_image_comparison_module\pizza_imgs\standard Pizza Image 2.jpg"
image2_path = "pizza_image_comparison_module\pizza_imgs\otgood_pizza_img.png"

# Generate prompt
prompt = create_pizza_comparison_prompt(image1_path, image2_path, criteria)

result = analyze_pizza_images(prompt, image1_path, image2_path, api_key)

print(result)

