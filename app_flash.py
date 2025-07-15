from flask import Flask, request, jsonify
import json
import google.generativeai as genai
from flask_cors import CORS  # Para evitar problemas de CORS en desarrollo

# === FLASK APP ===
app = Flask(__name__)
CORS(app)

# === CONFIGURACIÓN CLIENTE GEMINI ===
genai.configure(api_key="AIzaSyAkfE2DMALUG20gRsjA54PtXscm00cWnOM")

model = genai.GenerativeModel("models/gemini-1.5-flash")

# === CARGAR TOURS ===
def cargar_tours():
    with open('tours_ingles.json', 'r', encoding='utf-8') as f:
        tours = json.load(f)
    print(f"✅ {len(tours)} tours loaded.")
    return tours

# === RESUMEN DE TOURS ===
def obtener_resumen_tours(tours):
    resumen = ""
    for tour in tours:
        nombre = tour.get("titulo", "No title")
        descripcion = tour.get("descripcion", "No description")
        resumen += f"Name: {nombre}\nDescription: {descripcion}\n\n"
    return resumen

tours = cargar_tours()
resumen_tours = obtener_resumen_tours(tours)

# === GENERADOR DE RESPUESTAS ===
def generar_respuesta(pregunta, contexto):
    instruccion = (
        "You are a helpful travel assistant for IncaLake, a Peruvian travel agency. "
        "Use the following tour information to answer any questions. "
        "Always reply in English. "
        "Be clear, concise, and friendly. "
        "Limit your answer to 3 short paragraphs or 4–5 bullet points maximum. "
        "Avoid unnecessary details unless the user asks for more.\n\n"
        f"Available tours:\n{contexto}"
    )

    try:
        response = model.generate_content(
            [instruccion, pregunta],
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 512
            }
        )
        return response.text
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return "IncaLake: Sorry, something went wrong. Please try again later."


# === API ENDPOINT ===
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    pregunta = data.get('message', '')
    respuesta = generar_respuesta(pregunta, resumen_tours)
    return jsonify({'response': respuesta})

if __name__ == '__main__':
    app.run(debug=True)
