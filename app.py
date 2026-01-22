import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from PIL import Image
import base64
import io

st.set_page_config(page_title="Khana Kya Banau", page_icon="🍲")

st.title("🍲 Khana Kya Banau App")
st.write("Upload or take a photo of your ingredients and get Indian recipe ideas!")

# API Key input
api_key = st.text_input("🔑 Enter your OpenAI API Key:", type="password")

if not api_key:
    st.warning("⚠️ Please enter your OpenAI API key to continue.")
    st.stop()

# Initialize LLM (Vision-capable + cost-effective)
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=api_key
)

# Image input
uploaded_image = st.file_uploader("📤 Upload an image", type=["jpg", "jpeg", "png"])
camera_image = st.camera_input("📷 Take a picture")

image = None
if uploaded_image:
    image = Image.open(uploaded_image)
elif camera_image:
    image = Image.open(io.BytesIO(camera_image.getvalue()))

if not image:
    st.info("👆 Upload or capture an image to get started.")
    st.stop()

# Show image
st.image(image, caption="📸 Input Image", use_column_width=True)

# Convert image to Base64
buffered = io.BytesIO()
image.save(buffered, format="PNG")
img_base64 = base64.b64encode(buffered.getvalue()).decode()

# ---------- Step 1: Detect Ingredients ----------
detection_message = HumanMessage(
    content=[
        {
            "type": "text",
            "text": (
                "Identify all visible food ingredients in this image. "
                "Return ONLY a comma-separated list of ingredient names. "
                "Do not add explanations."
            )
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{img_base64}"
            }
        }
    ]
)

with st.spinner("🔎 Detecting ingredients..."):
    try:
        detection_response = llm.invoke([detection_message])
        detected_items = detection_response.content.strip()
    except Exception as e:
        st.error(f"❌ Ingredient detection failed: {e}")
        st.stop()

st.subheader("✅ Detected Ingredients")
st.write(detected_items)

# ---------- Step 2: Generate Recipes ----------
recipe_prompt = f"""
Using the following ingredients: {detected_items}

Suggest 3 popular Indian recipes.

For each recipe provide:
- Recipe name
- Required ingredients
- Simple step-by-step instructions

Keep the language simple and easy to understand.
"""

with st.spinner("👨‍🍳 Generating recipes..."):
    try:
        recipe_response = llm.invoke(
            [HumanMessage(content=recipe_prompt)]
        )
    except Exception as e:
        st.error(f"❌ Recipe generation failed: {e}")
        st.stop()

st.subheader("🍛 Suggested Indian Recipes")
st.write(recipe_response.content)

