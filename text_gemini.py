import os

from dotenv import load_dotenv
from google import genai


# Load .env
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")

print("API key found:", bool(api_key))

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )


# Create Gemini client
client = genai.Client(api_key=api_key)


# Send test request
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Explain tomato late blight in one simple sentence."
)


# Print response
print("\nGemini response:")
print(response.text)