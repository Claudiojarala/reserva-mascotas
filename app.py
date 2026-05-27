import os
import streamlit as st
import pymongo
from google import genai
from google.genai import types

# Importaciones relacionales desde db.py
from db import SessionLocal, Reserva, Dueno, Mascota, cifrar_dato, descifrar_dato, inicializar_base_de_datos

# ==============================================================================
# 1. CARGA INTELIGENTE DE VARIABLES
# ==============================================================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")

if not GOOGLE_API_KEY or not MONGODB_URI:
    st.error("❌ Faltan configurar las variables de entorno en tu panel.")
    st.stop()

# ==============================================================================
# 2. INSTANCIACIÓN DE CLIENTES CON CACHÉ
# ==============================================================================
@st.cache_resource
def get_genai_client():
    return genai.Client(api_key=GOOGLE_API_KEY)

@st.cache_resource
def get_mongo_collection():
    client = pymongo.MongoClient(MONGODB_URI)
    db = client["pdf_embeddings_db"]
    return db["pdf_vectors"]

client_genai = get_genai_client()
collection_mongo = get_mongo_collection()

# Inicializamos las tablas en Postgres al arrancar
inicializar_base_de_datos()

# ==============================================================================
# 3. PIPELINE DE INTELIGENCIA ARTIFICIAL (RAG)
# ==============================================================================
def crear_embedding_query(texto: str):
    response = client_genai.models.embed_content(
        model="gemini-embedding-001",
        contents=texto,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    return response.embeddings.values

def buscar_contexto_pdf(embedding, k=4):
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": embedding,
                "numCandidates": 100,
                "limit": k,
            }
        },
        {
            "$project": {
                "_id": 0,
                "texto": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]
    try:
        return list(collection_mongo.aggregate(pipeline))
    except Exception as e:
        return []

def generar_respuesta_llm(pregunta: str, contextos: list) -> str:
    contexto_str = "\n\n".join([c["texto"] for c in contextos])
    prompt = f"""Eres un asistente experto para la Guardería de Mascotas Exóticas. 
Usa EXCLUSIVAMENTE el siguiente contexto técnico para responder la pregunta del usuario. 

Contexto Técnico:
{contexto_str}

Pregunta del Usuario: {pregunta}
Responde de forma concisa y clara en español."""

    response = client_genai.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text

# ==============================================================================
# 4. INTERFAZ GRÁFICA (Streamlit UI)
# ==============================================================================
st.set_page_config(page_title="Control Guardería Exótica", page_icon="🐾", layout="wide")

menu = ["💬 Chatbot Asistente IA (RAG)", "📋 Registrar Dueño y Mascota", "📅 Gestionar Reservas"]
opcion = st.sidebar.selectbox("Módulos del Sistema", menu)

# MÓDULO 1: CHATBOT (Tu ejemplo del Notebook integrado)
if opcion == "💬 Chatbot Asistente IA (RAG)":
    st.title("💬 Consultas Técnicas (MongoDB Atlas + Gemini)")
    
    if "historial" not in st.session_state:
        st.session_state.historial = []

    for msg in st.session_state.historial:
        st.chat_message("user" if msg["rol"] == "usuario" else "assistant").write(msg["texto"])

    pregunta = st.chat_input("Escribe tu duda técnica...")

    if pregunta:
        st.chat_message("user").write(pregunta)
        st.session_state.historial.append({"rol": "usuario", "texto": pregunta})

        with st.chat_message("assistant"):
            with st.spinner("Buscando en Atlas..."):
                try:
                    vector_query = crear_embedding_query(pregunta)
                    fragmentos = buscar_contexto_pdf(vector_query, k=4)
                    respuesta = generar_respuesta_llm(pregunta, fragmentos) if fragmentos else "No encontré información relevante."
                except Exception as e:
                    respuesta = f"⚠️ Error: {e}"
            st.write(respuesta)
        st.session_state.historial.append({"rol": "bot", "texto": respuesta})

# MÓDULO 2: TRANSACCIONES EN POSTGRESQL
elif opcion == "📋 Registrar Dueño y Mascota":
    st.title("📋 Registro Seguro de Clientes")
    db_session = SessionLocal()
    col1, col2 = st.columns(2)
    
    with col1:
        id_dueno = st.number_input("ID Propietario", min_value=1, step=1)
        nombre_dueno = st.text_input("Nombre Completo")
        correo = st.text_input("Correo")
        telefono = st.text_input("Teléfono")
    with col2:
        id_mascota = st.number_input("ID Mascota", min_value=1, step=1)
        nombre_mascota = st.text_input("Nombre Mascota")
        especie = st.selectbox("Especie", ["Reptil", "Ave Exótica", "Otro"])

    if st.button("Guardar Registro"):
        if nombre_dueno and correo and nombre_mascota:
            try:
                nuevo_dueno = Dueno(id_dueno=id_dueno, nombre=nombre_dueno, correo_cifrado=cifrar_dato(correo), telefono_cifrado=cifrar_dato(telefono))
                nueva_mascota = Mascota(id_mascota=id_mascota, id_dueno=id_dueno, nombre_mascota=nombre_mascota, especie=especie)
                db_session.add(nuevo_dueno)
                db_session.add(nueva_mascota)
                db_session.commit()
                st.success("✅ Datos guardados con éxito en Postgres.")
            except Exception as e:
                db_session.rollback()
                st.error(f"❌ Error: {e}")
    db_session.close()

# MÓDULO 3: GESTIÓN DE RESERVAS
elif opcion == "📅 Gestionar Reservas":
    st.title("📅 Programación de Estadías")
    db_session = SessionLocal()
    mascotas_db = db_session.query(Mascota).all()
    opciones_mascotas = {f"ID {m.id_mascota} - {m.nombre_mascota}": m.id_mascota for m in mascotas_db}
    
    if not opciones_mascotas:
        st.info("Registra una mascota primero.")
    else:
        id_reserva = st.number_input("ID Reserva", min_value=1, step=1)
        mascota_sel = st.selectbox("Selecciona la Mascota", list(opciones_mascotas.keys()))
        fecha = st.date_input("Fecha de Ingreso")
        restricciones = st.text_area("Restricciones Alimenticias")
        
        if st.button("Confirmar Reserva"):
            try:
                nueva_reserva = Reserva(id_reserva=id_reserva, id_mascota=opciones_mascotas[mascota_sel], fecha_ingreso=fecha, dieta_restriccion=restricciones)
                db_session.add(nueva_reserva)
                db_session.commit()
                st.success("✅ Reserva agendada.")
            except Exception as e:
                db_session.rollback()
                st.error(f"❌ Error: {e}")
    db_session.close()
