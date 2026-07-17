import os
from google import genai

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def preguntar_ia(texto):
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=texto
        )
        return response.text
    except Exception as e:
        return f"Error de Gemini: {e}"
