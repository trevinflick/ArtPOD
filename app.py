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
        shiny.ui.tags.style((Path(__file__).parent / "style.css").read_text()),
        shiny.ui.tags.script("""
            function updateImageSrc() {
            var img = document.querySelector('.responsive-image');
            if (img) {
                var screenWidth = window.innerWidth;
                console.log('Viewport width:', screenWidth);
                var src = img.getAttribute('data-small'); // Default to small size
                if (screenWidth >= 1024) {
                    src = img.getAttribute('data-large');
                } else if (screenWidth >= 600) {
                    src = img.getAttribute('data-medium');
                }
                console.log('Image source:', src);
                img.src = src;
            }
        }

            // Initial update on load
            window.addEventListener('load', updateImageSrc);

            // Update when the window is resized
            window.addEventListener('resize', updateImageSrc);
        """)
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
                shiny.ui.output_ui("description"),
                class_="description"
            ),
            class_="art-details"
        ),
        style="text-align: center;"  # Ensure the text box itself is centered
    ),
    
    # Row for the caption and links
    shiny.ui.row(
        shiny.ui.column(12,  # Full-width column for the caption
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
                class_="caption"  # Apply caption class
            ),
            style="text-align: center;"
        )
    )
)

# Server
def server(input, output, session):
    @output
    @shiny.render.image
    def art_image():
        # Make sure to unpack all 8 values
        image_url_small, image_url_medium, image_url_large, image_url_full, description, artist_info, title, alt_text = fetch_art_data_from_github()

        hover_text = alt_text if alt_text != "No alternative text available" else description

        # Create temporary files for each image size
        temp_file_small = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file_medium = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file_large = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file_full = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")

        try:
            # Download images for each size
            response_small = requests.get(image_url_small)
            response_small.raise_for_status()
            temp_file_small.write(response_small.content)

            response_medium = requests.get(image_url_medium)
            response_medium.raise_for_status()
            temp_file_medium.write(response_medium.content)

            response_large = requests.get(image_url_large)
            response_large.raise_for_status()
            temp_file_large.write(response_large.content)

            response_full = requests.get(image_url_full)
            response_full.raise_for_status()
            temp_file_full.write(response_full.content)

            # Return the image tag with multiple sizes
            return {
                'src': temp_file_small.name,  # Default to the small image
                'alt': "Art Image",
                'title': hover_text,  # Tooltip (hover text)
                'class': "responsive-image",
                'width': "100%",  # Ensure responsiveness
                # Pass image paths for different sizes as data attributes
                'data-small': temp_file_small.name,
                'data-medium': temp_file_medium.name,
                'data-large': temp_file_large.name,
                'data-full': temp_file_full.name
            }

        except Exception as e:
            temp_file_small.close()
            temp_file_medium.close()
            temp_file_large.close()
            temp_file_full.close()
            raise e

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
