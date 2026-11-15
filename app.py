from gemini_service import get_disease_information
from flask import Flask, render_template, request, jsonify

import tensorflow as tf
import numpy as np

from PIL import Image

import json

from gemini_service import get_disease_information


# ==========================================================
# FLASK APPLICATION
# ==========================================================

app = Flask(__name__)


# ==========================================================
# FILE PATHS
# ==========================================================

MODEL_PATH = "leaf_disease_model (2).keras"
CLASS_NAMES_PATH = "class_names.json"


# ==========================================================
# LOAD CNN MODEL
# ==========================================================

print("=" * 60)
print("LOADING MODEL")
print("=" * 60)

model = tf.keras.models.load_model(
    MODEL_PATH
)

print("MODEL LOADED")
print("Input shape:", model.input_shape)
print("Output shape:", model.output_shape)


# ==========================================================
# LOAD CLASS NAMES
# ==========================================================

with open(
    CLASS_NAMES_PATH,
    "r",
    encoding="utf-8"
) as f:

    class_names = json.load(f)


print("Number of classes:", len(class_names))

print("=" * 60)

for i, class_name in enumerate(class_names):
    print(i, "->", class_name)

print("=" * 60)


# ==========================================================
# IMAGE PREPROCESSING
# ==========================================================

def preprocess_image(image):

    # Convert image to RGB
    image = image.convert("RGB")

    # Your model expects 224 x 224
    image = image.resize(
        (224, 224)
    )

    # Convert to NumPy array
    image = np.array(
        image,
        dtype=np.float32
    )

    # Add batch dimension
    image = np.expand_dims(
        image,
        axis=0
    )

    return image


# ==========================================================
# HOME PAGE
# ==========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================================================
# PREDICT
# ==========================================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    try:

        # --------------------------------------------------
        # CHECK IMAGE
        # --------------------------------------------------

        if "image" not in request.files:

            return jsonify({
                "error": "No image uploaded."
            }), 400


        file = request.files["image"]


        if file.filename == "":

            return jsonify({
                "error": "No image selected."
            }), 400


        # --------------------------------------------------
        # GET LANGUAGE
        # --------------------------------------------------

        language = request.form.get(
            "language",
            "en"
        )


        print("\n" + "=" * 60)
        print("NEW PREDICTION")
        print("=" * 60)

        print("Language:", language)


        # --------------------------------------------------
        # OPEN IMAGE
        # --------------------------------------------------

        image = Image.open(
            file.stream
        )


        print(
            "Image format:",
            image.format
        )

        print(
            "Original image size:",
            image.size
        )


        # --------------------------------------------------
        # PREPROCESS IMAGE
        # --------------------------------------------------

        processed_image = preprocess_image(
            image
        )


        # --------------------------------------------------
        # CNN PREDICTION
        # --------------------------------------------------

        predictions = model.predict(
            processed_image,
            verbose=0
        )


        # --------------------------------------------------
        # FIND PREDICTED CLASS
        # --------------------------------------------------

        predicted_index = int(
            np.argmax(predictions[0])
        )


        predicted_class = class_names[
            predicted_index
        ]


        # --------------------------------------------------
        # CONFIDENCE
        # --------------------------------------------------

        confidence = float(
            predictions[0][predicted_index] * 100
        )


        print("\nCNN RESULT")
        print("-" * 40)

        print(
            "Predicted class:",
            predicted_class
        )

        print(
            "Confidence:",
            round(confidence, 2),
            "%"
        )


        # --------------------------------------------------
        # SEND CNN RESULT TO GEMINI
        # --------------------------------------------------

        print("\nSending result to Gemini...")


        gemini_info = get_disease_information(

            disease=predicted_class,

            confidence=confidence,

            language=language
        )


        # --------------------------------------------------
        # PRINT GEMINI RESULT
        # --------------------------------------------------

        print("\nGemini information received.")

        print("=" * 60)


        # --------------------------------------------------
        # RETURN RESULT TO JAVASCRIPT
        # --------------------------------------------------

        return jsonify({

            "success": True,

            "disease": predicted_class,

            "confidence": round(
                confidence,
                2
            ),

            "name": gemini_info.get(
                "name",
                predicted_class
            ),

            "plant": gemini_info.get(
                "plant",
                "Information not available."
            ),

            "symptoms": gemini_info.get(
                "symptoms",
                "Information not available."
            ),

            "cause": gemini_info.get(
                "cause",
                "Information not available."
            ),

            "treatment": gemini_info.get(
                "treatment",
                "Information not available."
            ),

            "prevention": gemini_info.get(
                "prevention",
                "Information not available."
            ),

            "farmer_advice": gemini_info.get(
                "farmer_advice",
                "Information not available."
            )
        })


    # ======================================================
    # ERROR HANDLING
    # ======================================================

    except Exception as e:

        print("\n" + "=" * 60)
        print("FLASK ERROR")
        print("=" * 60)

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )

        print("=" * 60)


        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ==========================================================
# RUN FLASK
# ==========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )