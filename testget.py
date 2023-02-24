# READ FILE AND CLEAN DATA

# %% 

import PyPDF2
import pytesseract
from PIL import Image

def extract_regular_text(pdf_reader):
    num_pages = pdf_reader.getNumPages()
    regular_text = ''
    for page in range(num_pages):
        page_obj = pdf_reader.getPage(page)
        regular_text += page_obj.extractText()
    return regular_text

def extract_ocr_text(pdf_reader):
    num_pages = pdf_reader.getNumPages()
    ocr_text = ''
    for page in range(num_pages):
        page_obj = pdf_reader.getPage(page)
        page_image = page_obj.get_thumbnail(200)
        page_ocr_text = pytesseract.image_to_string(page_image)
        if len(page_ocr_text) > len(page_obj.extractText()):
            ocr_text += page_ocr_text
    return ocr_text

# Open the PDF file in read-binary mode
pdf_file = open('file.pdf', 'rb')

# Create a PDF reader object
pdf_reader = PyPDF2.PdfFileReader(pdf_file)

# Extract regular text and OCR text
regular_text = extract_regular_text(pdf_reader)
ocr_text = extract_ocr_text(pdf_reader)

# Close the PDF file
pdf_file.close()

# Combine regular text and OCR text
text = regular_text + ocr_text


# %%
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

def identify_acronyms(text):
    # Identify words in all caps using regular expressions
    all_caps_words = re.findall(r'\b[A-Z]{2,}\b', text)

    # Use part-of-speech tagging to identify likely acronyms
    pos_tags = nltk.pos_tag(all_caps_words)
    acronyms = [word for word, pos in pos_tags if pos == 'NNP']

    return acronyms


def clean_text(text):
    # Lowercase the text
    text = text.lower()

    # Remove non-alphanumeric characters
    text = re.sub(r'\W', ' ', text)

    # Tokenize the text
    tokens = nltk.word_tokenize(text)

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]

    # Stem the tokens
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]

    # Join the stemmed tokens back into a single string
    cleaned_text = ' '.join(stemmed_tokens)

    return cleaned_text


# PROCESS TEXT FOR QUESTION ANSWERING


