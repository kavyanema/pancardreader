import pytesseract
from PIL import Image
import re

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

image_path = str(input("Enter path to PAN Card Image: "))
text = extract_text_from_image(image_path)

name_find = re.compile(r'INCOMETAX\s*DEPARTMENT[^\n]*\n(?:.*?\bName[^\n]*\n|\n\s*)\s*([A-Z\s.]+)\s*\n', re.DOTALL)
pan_find = re.compile(r'\b([A-Z]{5}\d{4}[A-Z]{1})\b')
DOB_find = re.compile(r'\b(\d{2}/\d{2}/\d{4})\b')


name_match = name_find.search(text)
pan_match = pan_find.search(text)
DOB_match = DOB_find.search(text)

if name_match:
    name = name_match.group(1).strip()
    print("Name:", name)
else:
    print("No name found.")

if pan_match:
    pan_number = pan_match.group(0)
    print("PAN NUMBER IS:", pan_number)
else:
    print("Pan number not found")

if DOB_match:
    DOB_found = DOB_match.group(0)
    print("Date of Birth is:", DOB_found)
else:
    print("Date of Birth not found")

if DOB_found and pan_number:
    print("It is a pancard")
else:
    print("It is not a pan card")
