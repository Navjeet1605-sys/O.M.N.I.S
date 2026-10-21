import requests
import base64
from typing import Tuple, Optional
import os
from dotenv import load_dotenv; load_dotenv() # Load environment variables from .env file

def generate(prompt: str, seed: int=1800647681, width: int=1024, height: int=576, steps: int=4, enhance: bool=True, safety_filter: bool=True, image_path: str="Data/image.jpg") -> Tuple[bool, Optional[str]]:
    """
    Generates an image based on the given parameters and saves it to a file.

    Parameters:
    - prompt (str): Description of the image to generate.
    - seed (int): Seed for the image generation process.
    - width (int): Width of the generated image.
    - height (int): Height of the generated image.
    - steps (int): Number of steps for the image generation process. More the Steps More Clear and Realistic Image 
    - enhance (bool): Whether to enhance the image quality.
    - safety_filter (bool): Whether to apply a safety filter to the image.

    - For Square Image Size: 768x768
    - For Portrait Image Size: 1024x576
    - For Landscape Image Size: 576x1024

    Returns:
    - Tuple[bool, Optional[str]]: A tuple containing a boolean indicating the success of the API call,
      and an optional string with the file path where the image is saved if successful.
    """

    # Define the URL and headers for the API call
    url = "https://turbo.decohere.ai/generate/turbo"
    headers = {
        "Authorization": f"Bearer {os.environ.get('DECOHERE_AI')}",
    }

    # Define the payload for the POST request
    payload = {
        "prompt": prompt,
        "seed": seed,
        "width": width,
        "height": height, 
        "steps": steps,
        "enhance": enhance,
        "safety_filter": safety_filter,
    }

    # Make the POST request to the API
    response = requests.post(url, headers=headers, json=payload)

    # Check the response status code
    if response.status_code == 200:
        # Extract base64 encoded image data
        base64_image_data = response.json().get('image', '')
        # Decode base64 encoded image data to bytes
        image_bytes = base64.b64decode(base64_image_data)
        # Write the bytes to a file as an image
        with open(image_path, "wb") as image_file:
            image_file.write(image_bytes)
        return True, image_path
    else:
        print(f"API call failed with status code {response.status_code}")
        return False, response.text
    
# Example usage:
if __name__ == "__main__":
    prompt = "The neon-lit streets of Neo-Tokyo stretch out before you. Hovercars whiz past, leaving trails of light. Holographic billboards advertise cybernetic enhancements and virtual reality experiences. On a rooftop, a lone hacker in a trench coat plugs into the city’s mainframe, seeking hidden truths. Capture the gritty atmosphere—the rain-slicked pavement, the distant hum of machinery, and the flickering holograms."

    prompt = "Tucked away on a cobblestone street, the “ChronoTea” shop defies time itself. The bell jingles as you enter, and the aroma of exotic teas envelops you. The walls are adorned with antique clocks, each showing a different era. The barista, a mysterious figure with mismatched eyes, offers you a cup of “Eternal Jasmine.” As you sip, memories from your past and glimpses of your future swirl together. Describe the cozy nooks, the ticking clocks, and the taste of eternity."

    prompt = "Deep within the Whispering Woods lies a sacred glade. Ancient oaks form a protective circle, their leaves shimmering with magic. At midnight, druids gather—their robes embroidered with moon phases. They chant in an ancient language, invoking the spirits of earth, air, fire, and water. In the center, a silver cauldron steams, filled with herbs and moonlit dew. Describe the energy—the crackling ley lines, the rustling leaves, and the sense of balance restored."

    prompt = "In the heart of a cosmic nebula, an art gallery floats—a celestial masterpiece. Each exhibit is a swirling galaxy, its colors shifting with emotion. Visitors wear shimmering spacesuits, their helmets reflecting constellations. The curator, an android with silver tendrils, explains the meaning behind a star-cluster sculpture. Describe the ethereal beauty—the sound of solar winds, the taste of stardust, and the way the art seems to sing across light-years."

    prompt = "Ravenswood Manor stands atop a fog-shrouded hill. Its turrets and gables loom like silent sentinels. Inside, candelabras flicker, casting elongated shadows on velvet wallpaper. A ghostly pianist plays a mournful melody in the ballroom, while a spectral lady in white drifts down the grand staircase. Describe the chill in the air, the scent of old roses, and the secrets hidden in the dusty library."



    success, file_path = generate(prompt)
    if success: print(f"Image saved at {file_path}")
    else: print("Failed to generate the image.")