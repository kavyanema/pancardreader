from PIL import Image
import re
import easyocr
import cv2
import numpy as np
import os
# Define characters more likely to be misread and their replacements
letter_corrections = {
    "O": ["0"],
    "I": ["1"],
    "S": ["5"],
    "Z": ["2"],
    "B": ["8"],
    "T": ["7"]
    # Add more corrections as needed
}

number_corrections = {
    "0": ["O"],
    "1": ["I"],
    "2": ["Z"],
    "5": ["S"],
    "7": ["T"]
    # Add more corrections as needed
}

def contains_numbers(text):
    return bool(re.search(r'\d', text))
def contains_letters(text):
    return any(char.isalpha() for char in text)
# Function to apply corrections to the OCR output

def correct_letter_misreads(text, corrections):
    corrected_text = text
    for misread, alternatives in corrections.items():
        for alt in alternatives:
            corrected_text = corrected_text.replace(alt, misread)
    return corrected_text

def correct_number_misreads(text, corrections):
    corrected_text = text
    for misread, alternatives in corrections.items():
        for alt in alternatives:
            corrected_text = corrected_text.replace(alt, misread)
    return corrected_text

def correct_misreads(text):
    corrected_text_chars = text[:5]
    corrected_text_nbrs = text[-5:][:4]
    final = text[-1:]
    if contains_numbers(corrected_text_chars) :
      corrected_text_chars = correct_letter_misreads(corrected_text_chars, letter_corrections)
    if contains_numbers(final) :
      final = correct_letter_misreads(final, letter_corrections)
    if contains_letters(corrected_text_nbrs) :
      corrected_text_nbrs = correct_letter_misreads(corrected_text_nbrs, number_corrections)
    return corrected_text_chars+''+corrected_text_nbrs+''+final


image_path = str(input("Enter path to PAN Card Image: "))


name_find = re.compile(r'INCOMETAX\s*DEPARTMENT[^\n]*\n(?:.*?\bName[^\n]*\n|\n\s*)\s*([A-Z\s.]+)\s*\n', re.DOTALL)
pan_find = re.compile(r'\b([A-Z]{5}\d{4}[A-Z]{1})\b')
DOB_find = re.compile(r'\b(\d{2}/\d{2}/\d{4})\b')
text_reader = easyocr.Reader(['en']) #Initialzing the ocr
def extract_text_from_image(image_path):
    # load image
    img = cv2.imread(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # convert to grayscale
    # threshold to get just the signature (INVERTED)
    retval, thresh_gray = cv2.threshold(gray, thresh=245, maxval=255, \
                                        type=cv2.THRESH_BINARY_INV)
    cv2.imwrite('Image_gray.jpg', thresh_gray)  # debugging

    contours, hierarchy = cv2.findContours(thresh_gray,cv2.RETR_LIST, \
                                        cv2.CHAIN_APPROX_SIMPLE)
    # Find object with the biggest bounding box
    mx = (0,0,0,0)      # biggest bounding box so far
    mx_area = 0
    for cont in contours:
        x,y,w,h = cv2.boundingRect(cont)
        area = w*h
        if area > mx_area:
            mx = x,y,w,h
            mx_area = area
    x,y,w,h = mx
    filename, _ = os.path.splitext(os.path.basename(image))
    # Crop and save
    roi=img[y:y+h,x:x+w]
    cv2.imwrite(f'Image_crop_{filename}.jpg', roi)
    results = text_reader.readtext(roi )
    names = []
    dates = []
    pans = []
    for (bbox, text, prob) in results:

        # Define the regions based on the bounding box coordinates
        x1, y1 = bbox[0]
        x2, y2 = bbox[2]
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2


        # Check if the text is within the region of name
        if 15 < center_x < 140 and 80 < center_y < 140:
            if text != 'GOVT, OF INDIA' and text !='INCOME TaX DEPARTMENT':
                names.append(text)
        
        #finding birth date using regex
        DOB_match = DOB_find.search(text)
        if DOB_match:
            DOB_found = DOB_match.group(0)
            dates.append(DOB_found)

        #finding pan_number using regex
        pan_match = pan_find.search(text)
        if pan_match:
            pan_number = pan_match.group(0)
            pans.append(pan_number)
        else:
            # If it doesn't match, attempt to correct the misreads
            corrected_output = correct_misreads(text)
            pan_match = pan_find.search(corrected_output)
            if pan_match:
                pan_number = pan_match.group(0)
                pans.append(pan_number)
    return names,dates,pans

names,dates,pans = extract_text_from_image(image_path)

if names:
    print("Name:", names)
else:
    print("No name found.")

if pans:
    print("PAN NUMBER IS:", pans)
else:
    print("Pan number not found")

if dates:
    print("Date of Birth is:", dates)
else:
    print("Date of Birth not found")

if pans and dates:
    print("It is a pancard")
else:
    print("It is not a pan card")
