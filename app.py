import requests
import shiny
import tempfile
import os

from pathlib import Path

# Function to fetch the image and description for a specific artwork ID
def fetch_art_data(artwork_id=27992):
    api_url = f"https://api.artic.edu/api/v1/artworks/{artwork_id}"
    params = {"fields": "title,image_id,artist_display,short_description"}
    response = requests.get(api_url, params=params)
    response.raise_for_status()  # Check for request errors
    data = response.json()["data"]  # Get the artwork data

    image_url = f"https://www.artic.edu/iiif/2/{data['image_id']}/full/843,/0/default.jpg"
    description = data.get("short_description", "No description available")
    artist_display = data.get("artist_display", "No artist information available")
    title = data.get("title", "No title available")

    # Formatting artist name and additional details
    formatted_artist_info = format_artist_info(artist_display)
    
    return image_url, description, formatted_artist_info, title

def format_artist_info(artist_display):
    # Replace \n with a delimiter that can be split easily
    artist_display = artist_display.replace('\n', '|')
    
    # Split artist display info using comma and the new delimiter
    parts = artist_display.split('|')
    
    # Handle the parts of the artist display information
    if len(parts) == 2:
        artist_name = parts[0].strip()
        rest = parts[1].strip()
        return f"{artist_name}<br>{rest}"
    elif len(parts) == 3:
        artist_name = parts[0].strip()
        country = parts[1].strip()
        years = parts[2].strip()
        return f"{artist_name}<br>{country}, {years}"
    else:
        return artist_display  # Return as is if format is unexpected





# UI
app_ui = shiny.ui.page_fluid(
    shiny.ui.head_content(
        shiny.ui.tags.meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        shiny.ui.tags.style((Path(__file__).parent / "style.css").read_text()),
    ),
    shiny.ui.h2("Art Picture of the Day"),
    
    # Row for the image
    shiny.ui.row(
        shiny.ui.column(12,  # Full-width column for the image
            shiny.ui.output_image("art_image"),
            class_="art-image",
            style="text-align: center;"
        )
    ),

    # Row for the text information
    shiny.ui.row(
        shiny.ui.column(12,  # Full-width column for the text
            shiny.ui.div(
                shiny.ui.output_text("title"),
                class_="title"  # Apply title class
            ),
            shiny.ui.div(
                shiny.ui.output_ui("artist_name"),
                class_="artist-name"  # Apply artist name class
            ),
            shiny.ui.div(
                shiny.ui.output_text("description"),
                class_="description"
            ),
            class_="art-details"
        ),
        style="text-align: center;"  # Ensure the text box itself is centered
    )
)

# Server
def server(input, output, session):
    @output
    @shiny.render.image
    def art_image():
        image_url, _, _, _ = fetch_art_data()
        
        # Download the image to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file_name = temp_file.name
        
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            temp_file.write(response.content)
            temp_file.close()
            
            # Return the local path to the downloaded image
            return {
                'src': temp_file_name,
                'alt': "Art Image"
            }
        except Exception as e:
            temp_file.close()
            os.remove(temp_file_name)
            raise e

    @output
    @shiny.render.text
    def description():
        _, description, _, _ = fetch_art_data()
        return description
    
    @output
    @shiny.render.ui()
    def artist_name():
        _, _, artist_info, _ = fetch_art_data()
        return shiny.ui.HTML(artist_info)
    
    @output
    @shiny.render.text
    def title():
        _, _, _, title = fetch_art_data()
        return title

# Shiny app
app = shiny.App(ui=app_ui, server=server)

if __name__ == "__main__":
    app.run()
