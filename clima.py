import requests

API_KEY = "13b942d8b6eb4e4c68c73992bad30882"

def obtener_clima(ciudad):
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={ciudad}"
        f"&appid={API_KEY}"
        "&units=metric"
        "&lang=es"
    )

    respuesta = requests.get(url)

    if respuesta.status_code != 200:
        return f"Error obteniendo el clima: {respuesta.json()}"

    datos = respuesta.json()

    temperatura = datos["main"]["temp"]
    humedad = datos["main"]["humidity"]
    descripcion = datos["weather"][0]["description"]
    viento = datos["wind"]["speed"]

    return (
        f"Ciudad: {ciudad}\n"
        f"Clima: {descripcion}\n"
        f"Temperatura: {temperatura}°C\n"
        f"Humedad: {humedad}%\n"
        f"Viento: {viento} m/s"
    )

if __name__ == "__main__":
    ciudad = input("Ingresa una ciudad: ")
    print(obtener_clima(ciudad))
