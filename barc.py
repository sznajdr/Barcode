import streamlit as st
import requests
import os
from PIL import Image, ImageFont, ImageDraw
import textwrap

st.set_page_config(page_title="Barcode Generator")

# Download Arial.ttf if it doesn't exist
if not os.path.exists("Arial.ttf"):
    url = "https://github.com/matomo-org/travis-scripts/raw/71555936095b4d4252ec0a2eeacd710a17793db4/fonts/Arial.ttf"
    response = requests.get(url)
    with open("Arial.ttf", "wb") as f:
        f.write(response.content)

# Define widgets
barcode_textbox = st.text_input("Barcode:")
title_textbox = st.text_input("Title:")
generate_button = st.button("Generate Barcode")

# Define functions
def generate_barcode():
    barcode = barcode_textbox

    # Generate barcode image for the entered barcode
    # Set the barcode type to EAN13
    bcid = "ean13"

    # Set the font for the product title
    font = ImageFont.truetype("Arial.ttf", size=14)

    # Set the EAN13 number as the text to encode
    ean = barcode

    # Set the product title as the filename
    filename = "{}.png".format(barcode)

    # Set the API endpoint URL with includetext parameter
    url = "https://bwipjs-api.metafloor.com/?bcid={}&text={}&includetext=1&bg=ffffff".format(bcid, ean)
    st.write("Barcode URL:", url)

    # Send an HTTP GET request to the API endpoint
    response = requests.get(url)

    # Save the returned PNG image file with the product title as the filename
    with open(filename, "wb") as f:
        f.write(response.content)
    st.write("Saved barcode image as:", filename)

    # Open the saved barcode image
    filename = filename.strip()

    # Create a new image with extra margin to fit the wrapped product title text
    with Image.open(filename) as img:
        # Get the size of the barcode image
        width, height = img.size

        max_title_width = 40 # Set the maximum width for the product title text
        wrapped_title = textwrap.wrap(title_textbox, width=max_title_width, break_long_words=True) # Wrap the product title text into multiple lines if it is too long to fit
        wrapped_title_height = 0 # Calculate the total height required for the wrapped product title text
        for line in wrapped_title:
            wrapped_title_height += font.getsize(line)[1]
            
        # Calculate the total width required for the title and barcode
        total_width = max(width, font.getsize(title_textbox)[0])

        new_width = total_width + 2 # Add extra margin on both sides
        new_height = height + wrapped_title_height + 32 # Add extra margin at bottom
        new_img = Image.new("RGB", (new_width, new_height), color=(255, 255, 255, 255))

        # Paste the barcode image onto the new image
        barcode_img = img.convert("RGB") # Convert the mode of the barcode image to RGB
        new_img.paste(barcode_img, (int((new_width - width) / 2), 0))
        new_img = img.convert("RGBA") # Convert the mode of the barcode image to RGB

         # Get the actual width of the wrapped product title text
        actual_title_width = max([font.getsize(line)[0] for line in wrapped_title])

        # Calculate the x-coordinate of the title text to center it horizontally
        x = int((new_width - actual_title_width) / 2)

        # Set up the drawing context
        draw = ImageDraw.Draw(new_img)

               # Draw the product title onto the new image
        draw = ImageDraw.Draw(new_img)
        y_offset = height + 12 # Add extra margin
        for line in wrapped_title:
            # Get the width of the current line of text
            line_width, line_height = font.getsize(line)

            # Calculate the X coordinate for centering the text
            x_offset = int((new_width - line_width) / 2)

            # Draw the text on the new image
            draw.text((x_offset, y_offset), line, font=font, fill=(0, 0, 0, 255))

            # Move the Y offset down to the next line of text
            y_offset += line_height

        # Save the new image with the wrapped product title text
        new_filename = "{}_title.png".format(barcode)
        new_img.save(new_filename)
        st.write("Saved barcode image with title as:", new_filename)

if generate_button:
    generate_barcode()
