import requests
import shiny
import tempfile
import os
from pathlib import Path

def fetch_art_data_from_github():
    github_url = "https://raw.githubusercontent.com/trevinflick/fetch_art/main/art_data.json"
    response = requests.get(github_url)
    response.raise_for_status()  # Check for request errors
    data = response.json()  # Parse the JSON data

    # Extract data from JSON
    image_url = data.get("image_url", "No image available")
    description = data.get("description", "No description available")
    artist_display = data.get("artist_info", "No artist information available")
    title = data.get("title", "No title available")
    alt_text = data.get("alt_text", "No alternative text available")  # Fetch alt_text field
    
    return image_url, description, artist_display, title, alt_text


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
    ),
    
    # Add a footnote or caption acknowledging the Art Institute of Chicago API
    shiny.ui.div(
        shiny.ui.tags.p(
            "Data provided by ",
            shiny.ui.tags.a("The Art Institute of Chicago API", href="http://api.artic.edu/docs/#introduction", target="_blank"),
            class_="caption"
        ),
        style="text-align: center;"
    )
)

# Server
def server(input, output, session):
    @output
    @shiny.render.image
    def art_image():
        image_url, description, _, _, alt_text = fetch_art_data_from_github()
        
        # Determine the hover text
        hover_text = alt_text if alt_text != "No alternative text available" else description
        
        # Download the image to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file_name = temp_file.name
        
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            temp_file.write(response.content)
            temp_file.close()
            
            # Return the local path to the downloaded image with the hover text
            return {
                'src': temp_file_name,
                'alt': "Art Image",
                'title': hover_text  # Add the hover text here
            }
        except Exception as e:
            temp_file.close()
            os.remove(temp_file_name)
            raise e

    @output
    @shiny.render.text
    def description():
        _, description, _, _, _ = fetch_art_data_from_github()
        return description
    
    @output
    @shiny.render.ui()
    def artist_name():
        _, _, artist_info, _, _ = fetch_art_data_from_github()
        return shiny.ui.HTML(artist_info)
    
    @output
    @shiny.render.text
    def title():
        _, _, _, title, _ = fetch_art_data_from_github()
        return title

# Shiny app
app = shiny.App(ui=app_ui, server=server)

if __name__ == "__main__":
    app.run()
