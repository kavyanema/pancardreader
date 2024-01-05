import pytesseract
from PIL import Image

def extract_text_from_image(image_path):
   image = Image.open(image_path)
   text = pytesseract.image_to_string(image)
   return text

def is_pan_card(text):
   keywords = ['GOVT', 'INDIA', 'INCOME']
   if all(keyword in text for keyword in keywords):
       return "It is a PAN card"
   else:
       return "It is not a PAN card"

image_path = str(input("Enter path to PAN Card Image: "))
text = extract_text_from_image(image_path)

pan_info_file = "pan_info.txt"
with open(pan_info_file, 'w') as file:
   file.write(text)

with open(pan_info_file, 'r') as file:
   file_content = file.readlines()
   print("Content of pan_info.txt:", file_content)

check = is_pan_card(text)
print(check)

name_extracted = file_content[8].strip()
print("Name is:", name_extracted)

DOB= file_content[17].strip()
print("DOB is:",DOB)

Pan_num=file_content[5].strip()
print("Pan number is:",Pan_num)





