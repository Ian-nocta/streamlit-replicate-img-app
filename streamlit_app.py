import replicate
import streamlit as st
import requests
import zipfile
import io
from utils import icon
from streamlit_image_select import image_select

# UI configurations
st.set_page_config(page_title="Your Aura Reading",
                   page_icon=":crystal_ball:",
                   layout="wide")
icon.show_icon(":crystal_ball:")
st.markdown("# :rainbow[Your Aura Reading]")
st.markdown(":orange[<strong>Hmm you're hard to read 🤔</strong>]", unsafe_allow_html=True)


#removing the github fork

st.markdown(
    """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# API Tokens and endpoints from `.streamlit/secrets.toml` file
REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
REPLICATE_MODEL_ENDPOINTSTABILITY = st.secrets["REPLICATE_MODEL_ENDPOINTSTABILITY"]

# Resources text, link, and logo
replicate_text = "Stability AI SDXL Model on Replicate"
replicate_link = "https://replicate.com/stability-ai/sdxl"
replicate_logo = "https://storage.googleapis.com/llama2_release/Screen%20Shot%202023-07-21%20at%2012.34.05%20PM.png"

# Placeholders for images and gallery
generated_images_placeholder = st.empty()
gallery_placeholder = st.empty()

def generate_prompt(color_choice, emotion):
    return f"Create a high-fidelity, circular aura image that exudes a sense of energy and {emotion}. The aura should be a gradient, using only various shades of {color_choice} that seamlessly blend into one another. Start with a light, pastel shade of {color_choice} at the outermost edge, gradually transitioning to a vibrant, mid-tone shade in the middle, and finally, a deep, rich shade of {color_choice} at the innermost part of the circle. The transition between the shades should be smooth and refined, creating a polished, high-quality finish. The image should be centered on a black background to make the {color_choice} tones pop and to add depth and contrast to the overall composition."

def configure_sidebar() -> None:
    with st.sidebar:
        with st.form("my_form"):
            st.info(":rainbow**Lets get started↓**", icon="👋🏾")
            with st.expander(":rainbow[**Answer these Qs**]"):
                # Advanced Settings (for the curious minds!)
                user_name = st.text_input("Enter your name:")
                num_outputs = st.slider(
                    "Number of Auras", value=0, min_value=1, max_value=1)
                music_vibe = st.selectbox('Go to music vibe', ("", "💌🎧", "🎸🎧", "🍒🎧", "🔥🎧", "✨🎧", "💃🎧", "🌹"))
                mood_emoji = st.selectbox("Which emoji describes your mood today", ("","😊", "😰","😐", "😔","😒" ,"😡", "🥳","😍","😂","🤩"))
                angel_number = st.slider(
                    "Choose your angel number😇", value=0, min_value=0, max_value=999, step=111)
            prompt = st.text_area(
                ":orange[**Which colour would your bestie use to describe your personality✍🏾**]",
                value="orange, for a fun mood")
        

            # The Big Red "Submit" Button!
            submitted = st.form_submit_button(
                "Submit", type="primary", use_container_width=True)

        # Credits and resources
        st.divider()
        st.markdown(
            ":orange[**Resources:**]  \n"
            f"<img src='{replicate_logo}' style='height: 1em'> [{replicate_text}]({replicate_link})",
            unsafe_allow_html=True
        )
        st.markdown(
            """
            ---
            Follow Aurascope on:

            Tiktok → [@aurascope2](https://www.tiktok.com/@aurascope2)

            """
        )

        # Parse the user input to extract color and emotion
        color_choice, emotion = parse_user_input(prompt)

        return submitted, user_name, num_outputs, music_vibe, mood_emoji, angel_number, color_choice, emotion

def parse_user_input(prompt: str) -> tuple:
    if "," in prompt:
        color_choice, emotion = prompt.split(", ")
    elif " for " in prompt:
        color_choice, emotion = prompt.split(" for ")
    else:
        color_choice, emotion = "", ""
    return color_choice, emotion

def main_page(submitted: bool, user_name: str, num_outputs: int,
              music_vibe: str, mood_emoji: str,
              aura_number: int, color_choice: str,
              emotion: str) -> None:
    if submitted:
        # Include the user's name in the status message (if provided)
        status_message = f"🧙‍♀️ Finally {user_name if user_name else 'I'} I can see your Aura just a few more seconds..."

        with st.status(status_message, expanded=True) as status:
            st.write("⚙️ Spells initiated")
            st.write("🙆‍♀️ Stand up and stretch in the meantime")

        try:
            if submitted:
                # Generate the prompt using the generate_prompt function
                generated_prompt = generate_prompt(color_choice, emotion)

                # Calling the replicate API to get the image
                with generated_images_placeholder.container():
                    all_images = []  # List to store all generated images
                    output = replicate.run(
                        REPLICATE_MODEL_ENDPOINTSTABILITY,
                        input={
                            "prompt": generated_prompt,  # Use the generated_prompt here
                            "num_outputs": num_outputs
                        }
                    )

                    if output:
                        st.toast(
                            'Your image has been generated!', icon='😍')
                        # Save generated image to session state
                        st.session_state.generated_image = output

                        # Display the user's name (if provided) in bold below the heading
                        if user_name:
                            st.markdown(f"<h2 style='text-align: center;'><strong>🤩Wow {user_name} your Aura is glowinggg💅🏼</strong></h2>", unsafe_allow_html=True)

                        # Displaying the image
                        for image in st.session_state.generated_image:
                            with st.container():
                                st.image(image, caption="Your Aura 🎈",
                                         use_column_width=True)
                                # Add image to the list
                                all_images.append(image)

                                response = requests.get(image)

                    # Save all generated images to session state
                    st.session_state.all_images = all_images

                    # Create a BytesIO object
                    zip_io = io.BytesIO()

                    # Download option for each image
                    with zipfile.ZipFile(zip_io, 'w') as zipf:
                        for i, image in enumerate(st.session_state.all_images):
                            response = requests.get(image)
                            if response.status_code == 200:
                                image_data = response.content
                                # Write each image to the zip file with a name
                                zipf.writestr(
                                    f"output_file_{i+1}.png", image_data)
                            else:
                                st.error(
                                    f"Failed to fetch image {i+1} from {image}. Error code: {response.status_code}", icon="🚨")

                    # Create a download button for the zip file
                    st.download_button(
                        ":red[**Download All Images**]", data=zip_io.getvalue(), file_name="output_files.zip", mime="application/zip", use_container_width=True)

        except Exception as e:
            print(e)
            st.error(f'Encountered an error: {e}', icon="🚨")


    # Footer
    st.divider()
    footer = """<div style="text-align: center;">
                <a href="https://visitorbadge.io/status?path=https%3A%2F%2Faurascope.streamlit.app%2F">
                    <img src="https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Faurascope.streamlit.app%2F&label=aurascope&labelColor=%23ffffff&countColor=%23000000&style=plastic" />
                </a>
            </div>"""
    st.markdown(footer, unsafe_allow_html=True)

# Gallery display for inspo
    with gallery_placeholder.container():
        img = image_select(
            label="(Click on the '>' in the top left for the questions and right-click to save pictures when ready! 😉)",
            images=[
                 "gallery/love_aura.png", "gallery/laugh_aura.png", "gallery/yellow_aura.png", "gallery/green_aura.png","gallery/true_aura.png","gallery/purple_aura.png",
            ],
            captions=["Red: Passionate, confident, loving, ambitious, hard-working",                                         
                      "Orange: jovial, humorous, adventurous, loves life ",
                      "Yellow: energetic, friendly, encouraging, happy, intelligent ",
                      "Green: compassionate, healing, responible, caring, free-spirited",
                      "Light blue: self-expressive, intuitive, deep, wise, great communicator", 
                      "Violet: magical, creative, spiritual, calm",
                      ],
            use_container_width=True
        )

def main():
    submitted, user_name, num_outputs, music_vibe, mood_emoji, angel_number, color_choice, emotion = configure_sidebar()
    main_page(submitted, user_name, num_outputs, music_vibe, mood_emoji, angel_number, color_choice, emotion)

    
if __name__ == "__main__":
    main()
