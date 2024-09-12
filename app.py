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
    
    # Make sure to call .get() on the 'data' dictionary, not a Shiny tag
    image_id = data.get("image_id", None)  # Assuming image_id is available
    if image_id:
        image_url_small = f"https://www.artic.edu/iiif/2/{image_id}/full/200,/0/default.jpg"
        image_url_medium = f"https://www.artic.edu/iiif/2/{image_id}/full/400,/0/default.jpg"
        image_url_large = f"https://www.artic.edu/iiif/2/{image_id}/full/800,/0/default.jpg"
        image_url_full = f"https://www.artic.edu/iiif/2/{image_id}/full/full/0/default.jpg"
    else:
        image_url_small = image_url_medium = image_url_large = image_url_full = "No image available"
    
    description = data.get("description", "No description available")
    artist_display = data.get("artist_info", "No artist information available")
    title = data.get("title", "No title available")
    alt_text = data.get("alt_text", "No alternative text available")
    
    # Return all 8 values
    return image_url_small, image_url_medium, image_url_large, image_url_full, description, artist_display, title, alt_text




# UI
app_ui = shiny.ui.page_fluid(
    shiny.ui.head_content(
        shiny.ui.tags.meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        shiny.ui.tags.style((Path(__file__).parent / "style.css").read_text())
    ),
    shiny.ui.div(
        shiny.ui.h2("Art Picture of the Day"),
        
        # Container for image and text
        shiny.ui.div(
            # Image container
            shiny.ui.div(
                shiny.ui.output_image("art_image"),
                class_="art-image-container"
            ),

            # Text information container
            shiny.ui.div(
                shiny.ui.div(
                    shiny.ui.output_text("title"),
                    class_="title"
                ),
                shiny.ui.div(
                    shiny.ui.output_ui("artist_name"),
                    class_="artist-name"
                ),
                shiny.ui.div(
                    shiny.ui.output_ui("description"),
                    class_="description"
                ),
                class_="art-details"
            ),
            class_="content-container"
        ),
        
        shiny.ui.div(
            shiny.ui.HTML(
                """
                <p>
                    Inspired by Astronomy Picture of the Day: <a href="https://apod.nasa.gov/apod/astropix.html" target="_blank">APOD</a><br>
                    Powered by <a href="https://shiny.posit.co/" target="_blank">Shiny</a><br>
                    Check out the source code on <a href="https://github.com/trevinflick/" target="_blank">GitHub</a><br>
                    Follow the bot on <a href="https://bsky.app/profile/artpod.bsky.social" target="_blank">Bluesky</a>
                </p>
                """
            ),
            class_="caption"
        ),
        class_="main-container"
    )
)

# Server
def server(input, output, session):
    @output
    @shiny.render.image
    def art_image():
        image_url_small, image_url_medium, image_url_large, image_url_full, description, artist_info, title, alt_text = fetch_art_data_from_github()

        # Use description as hover text if alt_text is not available
        hover_text = alt_text if alt_text != "No alternative text available" else description

        # Download the image
        response = requests.get(image_url_full)
        response.raise_for_status()
        
        # Save the image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        # Return the image details for rendering
        return {
            'src': temp_file_path,
            'alt': hover_text,
            'title': hover_text,
            'style': "max-width: 100%; max-height: 800px; width: auto; height: auto;"
        }


    @output
    @shiny.render.ui
    def description():
        _, _, _, _, description, _, _, _ = fetch_art_data_from_github()
        return shiny.ui.HTML(description)
    
    @output
    @shiny.render.ui()
    def artist_name():
        _, _, _, _, _, artist_info, _, _ = fetch_art_data_from_github()
        return shiny.ui.HTML(artist_info)
    
    @output
    @shiny.render.text
    def title():
        _, _, _, _, _, _, title, _ = fetch_art_data_from_github()
        return title

# Shiny app
app = shiny.App(ui=app_ui, server=server)

if __name__ == "__main__":
    app.run()
