import os
import pyautogui as py
import time
import logging
import requests
import pytesseract
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Set up Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\\Program Files\\Tesseract-OCR\\tessdata'

# API Configurations
OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL = "gemma2:27b"

# Search region for radio buttons
SEARCH_REGION = (100, 800, 600, 1200)  # Adjust as needed

def take_screenshot(region):
    """Take a screenshot of the specified region."""
    screenshot = py.screenshot(region=region)
    screenshot_path = "question_area.png"
    screenshot.save(screenshot_path)
    return screenshot_path

def extract_text_from_image(image_path):
    """Extract text from an image using Tesseract OCR."""
    try:
        logging.info("Extracting text from image...")
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        logging.info(f"Extracted Text: {text}")
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting text from image: {e}")
        return None

def send_question_to_ollama(question_text):
    """Send the extracted question text to Ollama and get the response."""
    try:
        # Ensure that the question_text is not empty or malformed
        if not question_text or len(question_text.strip()) == 0:
            logging.error("Received empty or invalid question text.")
            return None

        # Log the question text to ensure it was extracted correctly
        logging.info(f"Sending question to Ollama: {question_text}")

        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "Provide answers as a single letter (A, B, C, or D) with no additional text."
                },
                {
                    "role": "user",
                    "content": question_text
                }
            ],
            "stream": False
        }
        
        logging.info("Sending question to Ollama...")
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()  # Check if the request was successful
        
        # Extract the answer from the response
        answer = response.json().get("message", {}).get("content", "").strip()

        # Log the answer received
        logging.info(f"Received answer: {answer}")

        # Ensure the answer is uppercase and return
        return answer.upper() if answer else None
        
    except Exception as e:
        logging.error(f"Error sending question to Ollama: {e}")
        return None


def locate_radio_buttons(radio_button_image, region=None):
    """Locate all radio buttons within a specific region on the screen."""
    logging.info("Locating all radio buttons...")
    try:
        locations = list(py.locateAllOnScreen(radio_button_image, confidence=0.8, region=region))
        unique_locations = deduplicate_locations(locations)

        if len(unique_locations) == 4:
            logging.info(f"Found {len(unique_locations)} radio buttons.")
            for i, location in enumerate(unique_locations):
                logging.info(f"Radio Button {i + 1}: {location}")
            return unique_locations
        else:
            logging.error(f"Expected 4 radio buttons but found {len(unique_locations)}.")
            return []
    except Exception as e:
        logging.error(f"Error locating radio buttons: {e}")
        return []

def deduplicate_locations(locations, threshold=5):
    """Remove duplicate radio button detections based on proximity."""
    unique_locations = []
    for loc in locations:
        if all(abs(loc.left - u.left) > threshold or abs(loc.top - u.top) > threshold for u in unique_locations):
            unique_locations.append(loc)
    return unique_locations

def click_radio_button(button_location):
    """Click on a radio button."""
    x = button_location.left + button_location.width / 2
    y = button_location.top + button_location.height / 2
    py.moveTo(x, y, duration=0.5)
    time.sleep(0.5)
    py.click()
    logging.info(f"Clicked radio button at ({x}, {y}).")

def locate_next_button(next_button_image):
    """Locate the 'Next' button."""
    logging.info("Locating 'Next' button...")
    try:
        location = py.locateOnScreen(next_button_image, confidence=0.8)
        if location:
            x, y = py.center(location)
            py.moveTo(x, y, duration=0.5)
            py.click()
            logging.info("'Next' button clicked.")
            return True
        else:
            logging.error("'Next' button not found on screen.")
            return False
    except Exception as e:
        logging.error(f"Error locating 'Next' button: {e}")
        return False

def process_question():
    """Process a single question."""
    logging.info("Taking screenshot of the question area...")
    question_image_path = take_screenshot((100, 200, 1000, 500))  # Adjust to fit question area

    question_text = extract_text_from_image(question_image_path)
    if not question_text:
        logging.error("Failed to extract question text.")
        return

    answer = send_question_to_ollama(question_text)
    if not answer:
        logging.error("Failed to get an answer from Ollama.")
        return

    # Locate the radio buttons and click the correct one
    radio_button_image = "radio_button.png"
    button_locations = locate_radio_buttons(radio_button_image, region=SEARCH_REGION)
    if not button_locations:
        logging.error("Failed to locate radio buttons.")
        return

    # Assuming the correct option is A, B, C, or D, based on Ollama's answer
    answer_map = {"A": 0, "B": 1, "C": 2, "D": 3}
    correct_option_index = answer_map.get(answer)
    
    if correct_option_index is None:
        logging.error("Invalid answer received, skipping question.")
        return
    
    click_radio_button(button_locations[correct_option_index])

    # Now click the 'Next' button
    next_button_image = "next.png"  # Ensure this image file is correct
    locate_next_button(next_button_image)

# Main loop
if __name__ == "__main__":
    num_questions = int(input("Enter number of questions: "))
    for i in range(num_questions):
        logging.info(f"Processing question {i + 1}...")
        process_question()
        time.sleep(2)  # Optional delay between questions
    logging.info("Completed all questions.")
