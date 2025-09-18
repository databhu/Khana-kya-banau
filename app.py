import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from PIL import Image
import base64
import io
import os

st.title("🍲 Khana Kya Banau App (OpenAI only)")
st.write("Take or upload a photo of your ingredients, and get Indian recipes!")

# API Key input from user
api_key = st.text_input("Enter your OpenAI API Key:", type="password")

if api_key:
    # Initialize model only if key is provided
    llm = ChatOpenAI(model="gpt-4.1-mini", api_key=api_key)

    # Upload or Camera input
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    camera_image = st.camera_input("Take a picture")

    image = None
    if uploaded_image:
        image = Image.open(uploaded_image)
    elif camera_image:
        image = Image.open(camera_image)

    if image:
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Convert image to base64 for OpenAI
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # Step 1: Detect food items
        detection_message = HumanMessage(
            content=[
                {"type": "text", "text": "Identify all food ingredients in this image."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
            ]
        )

        with st.spinner("🔎 Detecting ingredients..."):
            detection_response = llm.invoke([detection_message])
            detected_items = detection_response.content

        st.subheader("✅ Detected Ingredients")
        st.write(detected_items)

        # Step 2: Suggest Indian recipes
        recipe_prompt = f"""
        Using the following detected items: {detected_items}.
        Suggest 3 popular Indian recipes I can make. 
        Provide ingredients and steps in simple bullet points.
        """
        with st.spinner("👨‍🍳 Generating recipes..."):
            recipe_response = llm.invoke([HumanMessage(content=recipe_prompt)])

        st.subheader("🍛 Suggested Recipes")
        st.write(recipe_response.content)

else:
    st.warning("⚠️ Please enter your OpenAI API key above to use the app.")
