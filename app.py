import requests
import shiny
import tempfile
import os

# Function to fetch the image and description for a specific artwork ID
def fetch_art_data(artwork_id=27992):
    api_url = f"https://api.artic.edu/api/v1/artworks/{artwork_id}"
    params = {"fields": "title,image_id,artist_display,date_start,date_end,short_description"}
    response = requests.get(api_url, params=params)
    response.raise_for_status()  # Check for request errors
    data = response.json()["data"]  # Get the artwork data

    image_url = f"https://www.artic.edu/iiif/2/{data['image_id']}/full/843,/0/default.jpg"
    description = data.get("short_description", "No description available")
    artist_name = data.get("artist_display", "No artist information available")
    start_year = data.get("date_start", "No start year available")
    end_year = data.get("date_end", "No end year available")

    return image_url, description, artist_name, start_year, end_year

# UI
app_ui = shiny.ui.page_fluid(
    shiny.ui.h2("Art Picture of the Day"),
    shiny.ui.div(
        shiny.ui.output_image("art_image"),
        shiny.ui.output_text("description"),
        shiny.ui.output_text("artist_name"),
        shiny.ui.output_text("start_year"),
        shiny.ui.output_text("end_year"),
        style="display: flex; flex-direction: column; align-items: center;"
    )
)

# Server
def server(input, output, session):
    @output
    @shiny.render.image
    def art_image():
        image_url, _, _, _, _ = fetch_art_data()
        
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
        _, description, _, _, _ = fetch_art_data()
        return description
    
    @output
    @shiny.render.text
    def artist_name():
        _, _, artist_name, _, _ = fetch_art_data()
        return artist_name
    
    @output
    @shiny.render.text
    def start_year():
        _, _, _, start_year, _ = fetch_art_data()
        return start_year
    
    @output
    @shiny.render.text
    def end_year():
        _, _, _, _, end_year = fetch_art_data()
        return end_year

# Shiny app
app = shiny.App(ui=app_ui, server=server)

if __name__ == "__main__":
    app.run()
