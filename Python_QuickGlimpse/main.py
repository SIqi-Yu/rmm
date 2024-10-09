import asyncio
from PIL import Image, ImageTk

import scrappers.scrapper_example as scrapper_example
import customtkinter as ctk
from customtkinter import CTkImage

import scrappers.WeatherScrape_TaiyuanZhang as weather_scrapper
import scrappers.attraction_siqi as attraction_scrapper
import scrappers.airbnb_santiago as airbnb_scrapper

def main():
    gui()

async def get_results(location:str, use_offline:bool = False):
    """
    Calls the main functions of the various scrapping Python files.
    Async because web scraping.
    """
    weather_data = weather_scrapper.main(location, use_offline)
    attraction_data = attraction_scrapper.main("Museums", location, use_offline)
    airbnb_data = airbnb_scrapper.main(location, use_offline)
    return weather_data, attraction_data, airbnb_data

def gui():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.geometry("1280x1080")

    display_company_and_group(app)

    # Frame for top row element
    input_frame = ctk.CTkFrame(app)
    input_frame.pack(fill="x", padx=10, pady=10)

    # Top row: input
    text_input = gui_text_input(input_frame)
    text_input.pack(side="left", padx=(0, 10))

    # Top row:dropdown
    dropdown, select_option = gui_dropdown(input_frame)
    dropdown.pack(side="left", padx=(0, 10))

    # Top row:submit button
    submit_button = ctk.CTkButton(input_frame, text="Submit")
    submit_button.pack(side="left")

    # Top row:quit button
    quit_button = ctk.CTkButton(input_frame, text="Quit", command=app.quit, fg_color="red", hover_color="dark red")
    quit_button.pack(side="right")

    # Airbnb row with image and text
    image_label1, image_label2, airbnb_textbox = gui_create_image_and_text_row(app)
    airbnb_textbox.insert("1.0", "Key in a city to try! Quick hint: Try Dallas, San Diego, San Antonio, or some other famous US cities! Dallas will be pre downloaded.")

    # Attraction and weather row
    attractions_textbox, weather_textbox = gui_create_side_by_side_columns(app)

    async def get_and_display_results(input, use_offline=False):
        """
        This function gets the results using the scrappers and refreshes the GUI.
        """
        weather_info, attraction_info, airbnb_info = await get_results(input, use_offline)
        app.after(0, lambda: gui_display_weather(weather_textbox, weather_info))
        app.after(0, lambda: gui_display_attractions(attractions_textbox, attraction_info))
        app.after(0, lambda: gui_display_image(image_label1, "offline/City_average_prices.png"))
        app.after(0, lambda: gui_display_image(image_label2, "offline/City_price_ranges.png"))
        app.after(0, lambda: gui_display_airbnb(airbnb_textbox, airbnb_info))

        print(f"Airbnb info: {airbnb_info}")

    def submit_function():
        """
        Gets user input for city and type
        """
        input = text_input.get()
        use_offline = select_option.get() == "Use offline"
        asyncio.run(get_and_display_results(input, use_offline))

    submit_button.configure(command=submit_function)

    app.mainloop()
def gui_create_side_by_side_columns(app):
    # Create a container frame for the bottom two frames
    bottom_container = ctk.CTkFrame(app)
    bottom_container.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)

    # Create left frame for attractions (long rectangle)
    left_frame = ctk.CTkFrame(bottom_container)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=0)

    # Create right frame for weather (long rectangle)
    right_frame = ctk.CTkFrame(bottom_container)
    right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0), pady=0)

    # Create scrollable frame for attractions
    attractions_scroll = ctk.CTkScrollableFrame(left_frame, width=580, height=680)
    attractions_scroll.pack(fill="both", expand=True)

    # Create scrollable frame for weather
    weather_scroll = ctk.CTkScrollableFrame(right_frame, width=580, height=680)
    weather_scroll.pack(fill="both", expand=True)

    # Create text boxes for attractions and weather
    attractions_textbox = ctk.CTkTextbox(attractions_scroll, width=560, height=660, font=("Arial", 12))
    attractions_textbox.pack(padx=10, pady=10, fill="both", expand=True)

    weather_textbox = ctk.CTkTextbox(weather_scroll, width=560, height=660, font=("Arial", 12))
    weather_textbox.pack(padx=10, pady=10, fill="both", expand=True)

    return attractions_textbox, weather_textbox

def gui_text_input(parent):
    text_input = ctk.CTkEntry(parent, width=200)
    return text_input

def gui_dropdown(parent):
    selected_option = ctk.StringVar()
    selected_option.set("Scrape from online")
    options = ["Scrape from online", "Use offline"]
    dropdown = ctk.CTkOptionMenu(parent, variable=selected_option, values=options)
    return dropdown, selected_option

# =========================== Display and Formatting Functions for Data ===========================
def gui_display_attractions(text_box, attraction_info):
    if attraction_info is None:
        text_box.configure(state="normal")
        text_box.delete("1.0", "end")
        text_box.insert("end", "Attractions not available.\n\n", "title")
        text_box.configure(state="disabled")
    else:
        text_box.configure(state="normal")
        text_box.delete("1.0", "end")
        text_box.insert("end", "Attractions\n\n", "title")

        for attraction in attraction_info:
            text_box.insert("end", f"{attraction['title']}\n", "attraction_title")
            text_box.insert("end", "Time to Spend: ", "label")
            text_box.insert("end", f"{attraction['time_to_spend']}\n", "value")
            text_box.insert("end", "Type: ", "label")
            text_box.insert("end", f"{attraction['type']}\n\n", "value")

        text_box.configure(state="disabled")

def gui_display_weather(text_box, weather_info):
    if weather_info is None:
        text_box.configure(state="normal")
        text_box.delete("1.0", "end")
        text_box.insert("end", "Weather information not available.\n\n", "title")
        text_box.configure(state="disabled")
        return
    else:
        text_box.configure(state="normal")
        text_box.delete("1.0", "end")
        text_box.insert("end", f"🌦️ Weather Forecast for {weather_info['location']} 🌡️\n\n", "title")

        weather_emojis = {
            "sunny": "☀️",
            "clear": "🌞",
            "partly cloudy": "⛅",
            "cloudy": "☁️",
            "rain": "🌧️",
            "showers": "🌦️",
            "thunderstorm": "⛈️",
            "snow": "❄️",
            "fog": "🌫️",
            "windy": "💨",
            "hot": "🔥",
            "cold": "🥶"
        }

        for day, info in weather_info.items():
            if day != 'location':
                text_box.insert("end", f"📅 {day}:\n", "day")
                for key, value in info.items():
                    if key.lower() == 'description':
                        emoji = next((weather_emojis[k] for k in weather_emojis if k in value.lower()), "🌈")
                        text_box.insert("end", f"{emoji} {key.capitalize()}: ", "label")
                        text_box.insert("end", f"{value}\n", "value")
                    elif key.lower() == 'high':
                        text_box.insert("end", f"🔺 {key.capitalize()}: ", "label")
                        text_box.insert("end", f"{value}\n", "value")
                    elif key.lower() == 'low':
                        text_box.insert("end", f"🔻 {key.capitalize()}: ", "label")
                        text_box.insert("end", f"{value}\n", "value")
                    elif key != 'detailed':
                        text_box.insert("end", f"{key.capitalize()}: ", "label")
                        text_box.insert("end", f"{value}\n", "value")
                if 'detailed' in info:
                    text_box.insert("end", "ℹ️ Details: ", "label")
                    text_box.insert("end", f"{info['detailed']}\n", "value")
                text_box.insert("end", "\n")

        text_box.configure(state="disabled")

def gui_display_airbnb(text_box, airbnb_info):
    if airbnb_info is None:
        text_box.configure(state="normal")
        text_box.delete("1.0", "end")
        text_box.insert("end", "Airbnb information not available.\n\n", "title")
        text_box.configure(state="disabled")
        return
    else:
        text_box.configure(state="normal")
        text_box.delete("1.0", "end")

        # Helper function to create star ratings
        def star_rating(num):
            return "⭐" * int(num) + "☆" * (5 - int(num))

        text_box.insert("end", "Airbnb Listings Information\n\n", "title")

        # Display information for listings above 3 stars
        text_box.insert("end", f"Listings Above 3 Stars {star_rating(3)}\n", "subtitle")
        for bedrooms, data in airbnb_info['above_3_stars'].items():
            text_box.insert("end", f"🛏️ {bedrooms} Bedroom(s):\n", "bedroom_rating")
            text_box.insert("end", f"  Average Price: ${data['average_price']:.2f}\n", "info")
            text_box.insert("end", f"  Price Range: ${data['min']} - ${data['max']}\n", "info")
            text_box.insert("end", f"  Number of Listings: {data['count']}\n\n", "info")

        # Display information for all listings
        text_box.insert("end", f"All Listings {star_rating(5)}\n", "subtitle")
        for bedrooms, data in airbnb_info['all_listings'].items():
            text_box.insert("end", f"🛏️ {bedrooms} Bedroom(s):\n", "bedroom_rating")
            text_box.insert("end", f"  Average Price: ${data['average_price']:.2f}\n", "info")
            text_box.insert("end", f"  Price Range: ${data['min']} - ${data['max']}\n", "info")
            text_box.insert("end", f"  Number of Listings: {data['count']}\n\n", "info")

        text_box.configure(state="disabled")

def gui_display_image(container, file_path):
    try:
        pil_image = Image.open(file_path)
        pil_image = pil_image.resize((500, 400), Image.LANCZOS)
        ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(500, 400))
        
        container.configure(image=ctk_image)
        return True
    except Exception as e:
        print(f"Error loading image: {e}")
        return False

def gui_create_image_and_text_row(app):
    # Create a frame to hold the images and text
    row_frame = ctk.CTkFrame(app)
    row_frame.pack(fill="x", padx=10, pady=10)

    # Create two image labels
    image_label1 = ctk.CTkLabel(row_frame, text="")
    image_label1.pack(side="left", padx=(0, 5))

    image_label2 = ctk.CTkLabel(row_frame, text="")
    image_label2.pack(side="left", padx=(0, 5))

    # Create a text box
    text_box = ctk.CTkTextbox(row_frame, height=100, width=400)
    text_box.pack(side="left", padx=(5, 0), fill="both", expand=True)

    return image_label1, image_label2, text_box
def display_company_and_group(app):
    info_frame = ctk.CTkFrame(app)
    info_frame.pack(fill="x", padx=10, pady=(0, 10))

    company_name = "Quick Glimpse."
    group_members = ["Xun Yi", "Tai Yuan", "Siqi", "Santiago"]

    company_label = ctk.CTkLabel(info_frame, text=f"Company: {company_name}", font=("Arial", 14, "bold"))
    company_label.pack(side="left", padx=(10, 20))

    members_label = ctk.CTkLabel(info_frame, text="Group Members:", font=("Arial", 14, "bold"))
    members_label.pack(side="left")

    for member in group_members:
        member_label = ctk.CTkLabel(info_frame, text=member, font=("Arial", 12))
        member_label.pack(side="left", padx=(5, 0))

if __name__ == "__main__":
    # If you read this file, please forgive the amount of functions I declared within functions.
    # It is ugly work but it is honest work.
    main()