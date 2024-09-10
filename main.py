import os
import pyautogui as py
import time
from PIL import Image
import win32clipboard
from io import BytesIO
import keyboard
import pytesseract

# Set the path to your Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Ensure the TESSDATA_PREFIX environment variable is set
os.environ['TESSDATA_PREFIX'] = r'C:\\Program Files\\Tesseract-OCR\\tessdata'

questions = int(input('Enter number of questions... '))

def ScreenShot():
    print("Taking screenshot...")
    screenshot_path = 'image.png'
    cropped_image_path = 'image_cropped.png'
    py.screenshot(screenshot_path)
    im = Image.open(screenshot_path)
    left, top, right, bottom = 23, 350, 1790, 1115
    im_cropped = im.crop((left, top, right, bottom))
    im_cropped.save(cropped_image_path)
    print("Screenshot taken and cropped.")
    ExtractTextAndSubmit(cropped_image_path)

def image_to_clipboard(text):
    print("Copying text to clipboard...")
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text)
    win32clipboard.CloseClipboard()
    print("Text copied to clipboard.")

def ExtractTextAndSubmit(image_path):
    print("Extracting text from image...")
    image = Image.open(image_path)
    
    # Set the TESSDATA_PREFIX in the config
    tessdata_dir_config = '--tessdata-dir "C:\\Program Files\\Tesseract-OCR\\tessdata"'
    
    try:
        text = pytesseract.image_to_string(image, config=tessdata_dir_config)
        print("Extracted Text:")
        print(text)
        image_to_clipboard(text)
    
        print("Locating send image button...")
        send_image_path = 'send_a_message.png'
        location = py.locateOnScreen(send_image_path, confidence=0.70)
        if location:
            print("Send button found. Submitting answer...")
            py.moveTo(location.left + location.width / 2, location.top + location.height / 2)
            py.click()
            time.sleep(1)
            py.hotkey('ctrl', 'v')
            py.typewrite("Please only provide the answer a software developer would pick.")
            time.sleep(3)
            py.press('enter')
            py.moveTo(78, 830)
            py.click()
            print("Answer submitted.")
        else:
            print('Send button not found on the screen.')
    except pytesseract.pytesseract.TesseractError as e:
        print(f"Error: {e}")

def next():
    print("Locating next button...")
    next_image_path = 'next.png'
    button_location = py.locateOnScreen(next_image_path, confidence=0.70)
    if button_location:
        print("Next button found. Proceeding to next question...")
        py.moveTo(button_location)
        py.click()
        time.sleep(0.5)
    else:
        print('Next button not found on the screen.')

for i in range(questions):
    print(f"Processing question {i + 1}...")
    ScreenShot()
    print("Press 'a' to proceed to the next question...")
    keyboard.wait("a")
    next()
    print(f"Completed question {i + 1}.")
