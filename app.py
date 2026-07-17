from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar claves del archivo .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
modelo = genai.GenerativeModel("gemini-3.5-flash")

# Clave OpenWeather
OPENWEATHER_KEY = os.getenv("13b942d8b6eb4e4c68c73992bad30882")

app = Flask(__name__)


@app.route("/")
def inicio():
    return render_template("index.html")


# Estado del sistema
@app.route("/api/status")
def api_status():
    return jsonify({
        "nivel": "amarillo",
        "label": "Vigilancia",
        "zona_critica": "Quebrada Huaycán",
        "zonas_monitoreadas": 4,
        "sensores_activos": 8,
        "actualizado": datetime.now().strftime("%H:%M:%S")
    })


# Alertas
@app.route("/api/alertas")
def api_alertas():
    return jsonify({
        "alertas": [
            {
                "id": 1,
                "nivel": "amarillo",
                "titulo": "Lluvia moderada",
                "detalle": "Posible incremento de caudal",
                "hora": datetime.now().strftime("%H:%M")
            },
            {
                "id": 2,
                "nivel": "naranja",
                "titulo": "Zona de deslizamiento",
                "detalle": "Pendiente con humedad elevada",
                "hora": datetime.now().strftime("%H:%M")
            }
        ]
    })


# Zonas de riesgo
@app.route("/api/zonas")
def api_zonas():
    return jsonify({
        "center": {
            "lat": -12.0096,
            "lng": -76.8894
        },
        "zonas": [
            {
                "nombre": "Zona A",
                "tipo": "Deslizamiento",
                "nivel": "naranja",
                "lat": -12.005,
                "lng": -76.884,
                "sensor": "Sensor de humedad",
                "ultima_lectura": "78%"
            },
            {
                "nombre": "Zona B",
                "tipo": "Huayco",
                "nivel": "rojo",
                "lat": -12.013,
                "lng": -76.894,
                "sensor": "Sensor de caudal",
                "ultima_lectura": "Nivel elevado"
            }
        ]
    })


# Gemini IA
@app.route("/api/chat", methods=["POST"])
def api_chat():

    datos = request.get_json()
    mensaje = datos.get("mensaje", "")

    try:
        respuesta_gemini = modelo.generate_content(
            
            f"""
Eres SIATD IA, un asistente de alerta temprana
para huaycos y deslizamientos en Huaycán.

IMPORTANTE:
No inventes información.
No digas que existen sensores reales, sirenas,
conexiones con instituciones o datos que no estén
proporcionados.

Datos actuales del sistema:

Nivel de alerta: Amarillo
Estado: Vigilancia
Zona crítica: Quebrada Huaycán
Zonas monitoreadas: 4
Sensores activos: 8

Usuario:
{mensaje}
"""
        )

        respuesta = respuesta_gemini.text

    except Exception as error:
        respuesta = "Error conectando con Gemini: " + str(error)


    return jsonify({
        "respuesta": respuesta
    })


# OpenWeather
@app.route("/api/clima")
def api_clima():

    url = "https://api.openweathermap.org/data/2.5/weather"

    parametros = {
        "lat": -12.0096,
        "lon": -76.8894,
        "appid": OPENWEATHER_KEY,
        "units": "metric",
        "lang": "es"
    }

    respuesta = requests.get(url, params=parametros)
    datos = respuesta.json()

    return jsonify({
        "temperatura": datos["main"]["temp"],
        "humedad": datos["main"]["humidity"],
        "clima": datos["weather"][0]["description"]
    })


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
