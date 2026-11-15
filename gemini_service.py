import os
import json

from dotenv import load_dotenv
from google import genai


# ==========================================================
# LOAD .ENV
# ==========================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file."
    )


# ==========================================================
# CREATE GEMINI CLIENT
# ==========================================================

client = genai.Client(
    api_key=API_KEY
)


# ==========================================================
# GEMINI DISEASE INFORMATION
# ==========================================================

def get_disease_information(
    disease,
    confidence,
    language="en"
):

    # ------------------------------------------------------
    # LANGUAGE
    # ------------------------------------------------------

    language_names = {
        "en": "English",
        "or": "Odia",
        "hi": "Hindi"
    }

    selected_language = language_names.get(
        language,
        "English"
    )


    # ------------------------------------------------------
    # PROMPT
    # ------------------------------------------------------

    prompt = f"""
You are an agricultural assistant helping farmers.

A PlantVillage-trained CNN image classification model
predicted the following class:

Disease/Class: {disease}

CNN Confidence: {confidence:.2f}%

Generate useful information for the farmer.

Write the answer in {selected_language}.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "name": "",
    "plant": "",
    "symptoms": "",
    "cause": "",
    "treatment": "",
    "prevention": "",
    "farmer_advice": ""
}}

IMPORTANT RULES:

1. Keep the disease consistent with the CNN prediction.

2. Use simple language that an ordinary farmer can understand.

3. Explain the disease clearly.

4. Explain the plant name.

5. Explain common symptoms.

6. Explain the cause.

7. Give practical treatment advice.

8. Give practical prevention advice.

9. Do not invent specific pesticide doses.

10. If chemical treatment is mentioned, recommend
    following the product label and local agricultural
    expert recommendations.

11. Do not say that the AI diagnosis is 100% certain.

12. Mention that this is an AI-based prediction.

13. If confidence is low, recommend confirmation
    by a local agricultural expert.

14. If the class represents a healthy plant,
    explain that the plant appears healthy and
    provide general care advice.

15. Return JSON only.

16. Do not use Markdown.

17. Do not return ```json.

18. Do not change the CNN predicted disease to another disease.
"""


    # ------------------------------------------------------
    # CALL GEMINI
    # ------------------------------------------------------

    try:

        print("\nSending request to Gemini...")
        print("Model: gemini-3.8-flash")
        print("Disease:", disease)
        print("Confidence:", confidence)
        print("Language:", selected_language)


        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )


        # --------------------------------------------------
        # GET TEXT
        # --------------------------------------------------

        text = response.text.strip()


        print("\nGemini raw response:")
        print(text)


        # --------------------------------------------------
        # REMOVE MARKDOWN CODE FENCE
        # --------------------------------------------------

        if text.startswith("```json"):
            text = text[7:]

        elif text.startswith("```"):
            text = text[3:]


        if text.endswith("```"):
            text = text[:-3]


        text = text.strip()


        # --------------------------------------------------
        # CONVERT TO JSON
        # --------------------------------------------------

        data = json.loads(text)


        # --------------------------------------------------
        # REQUIRED KEYS
        # --------------------------------------------------

        required_keys = [
            "name",
            "plant",
            "symptoms",
            "cause",
            "treatment",
            "prevention",
            "farmer_advice"
        ]


        for key in required_keys:

            if key not in data:
                data[key] = "Information not available."


        return data


    # ------------------------------------------------------
    # ERROR
    # ------------------------------------------------------

    except Exception as e:

        print("\n" + "=" * 60)
        print("GEMINI ERROR")
        print("=" * 60)

        print("Error type:")
        print(type(e).__name__)

        print("\nError message:")
        print(str(e))

        print("=" * 60 + "\n")


        return {

            "name": disease,

            "plant": "Information unavailable.",

            "symptoms": "Gemini request failed.",

            "cause": "Gemini request failed.",

            "treatment": (
                "Please check the Gemini API configuration."
            ),

            "prevention": (
                "Please try the prediction again."
            ),

            "farmer_advice": (
                "This is an AI-based result. "
                "Please confirm the disease with "
                "an agricultural expert."
            )
        }