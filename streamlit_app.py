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
            with st.expander(":rainbow[**Refine your output here**]"):
                # Advanced Settings (for the curious minds!)

                num_outputs = st.slider(
                    "Number of images to output", value=0, min_value=1, max_value=1)
                music_vibe = st.selectbox('Go to music vibe', ('', 'Lofi', 'Phonk',
                                                       'Sad boi', 'Lit', 'Afrobeats', 'Amapiano','House'))
                mood_emoji = st.selectbox("Choose an emoji that describes your mood", ("","😊", "😐", "😔", "😡", "😍", "😂"))
                angel_number = st.slider(
                    "Choose your angel number", value=0, min_value=0, max_value=999, step=111)
            prompt = st.text_area(
                ":orange[**Chose one colour to describe your mood✍🏾**]",
                value="orange, for a fun mood")
            negative_prompt = st.text_area(":orange[**Party poopers you don't want in your Aura?(Leave as is) 🙅🏽‍♂️**]",
                                           value="the absolute worst quality, distorted features",
                                           help="This is a negative prompt, basically type what you don't want to see in the generated image")

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
            Follow me on:

            Tiktok → [@aurascope2](https://www.tiktok.com/@aurascope2)

            LinkedIn → [Ian McClue](https://www.linkedin.com/in/ian-mcclue-92786515a/)

            """
        )

        # Parse the user input to extract color and emotion
        color_choice, emotion = parse_user_input(prompt)

        return submitted, num_outputs, music_vibe, mood_emoji, angel_number, color_choice, emotion, negative_prompt

def parse_user_input(prompt: str) -> tuple:
    if "," in prompt:
        color_choice, emotion = prompt.split(", ")
    elif " for " in prompt:
        color_choice, emotion = prompt.split(" for ")
    else:
        color_choice, emotion = "", ""
    return color_choice, emotion

def main_page(submitted: bool, num_outputs: int,
              music_vibe: str, mood_emoji: str,
              aura_number: int, color_choice: str,
              emotion: str, negative_prompt: str) -> None:

    if submitted:
        with st.status('🧙‍♀️ Finally I can see your Aura just a few more seconds...', expanded=True) as status:
             st.write("⚙️ Spells initiated")
             st.write("🙆‍♀️ Stand up and strecth in the meantime")

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

                        # Displaying the image
                        for image in st.session_state.generated_image:
                            with st.container():
                                st.image(image, caption="Generated Image 🎈",
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

# Gallery display for inspo
    with gallery_placeholder.container():
        img = image_select(
            label="Hmm you're hard to read 🤔 (Click on the '>' in the top left for the questions and right-click to save pictures when ready! 😉)",
            images=[
                "gallery/true_aura.png", "gallery/love_aura.png",
                "gallery/laugh_aura.png",
            ],
            captions=["Light blue: self-expressive, intuitive, deep, wise, great communicator",
                      "Red: Passionate, confident, loving, ambitious, hard-working",
                      "Orange: jovial, humorous, adventurous, loves life ",
                      ],
            use_container_width=True
        )


def main():
    submitted, num_outputs, music_vibe, mood_emoji, angel_number, color_choice, emotion, negative_prompt = configure_sidebar()
    main_page(submitted, num_outputs, music_vibe, mood_emoji, angel_number, color_choice, emotion, negative_prompt)

if __name__ == "__main__":
    main()
