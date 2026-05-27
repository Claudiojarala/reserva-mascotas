import os
import streamlit as st
from sqlalchemy.orm import Session

# Importaciones de tu db.py
from db import SessionLocal, Reserva, Dueno, Mascota, cifrar_dato, descifrar_dato, inicializar_base_de_datos

# Inicializar las tablas relacionales en la base Postgres de Railway
inicializar_base_de_datos()

st.set_page_config(page_title="Gestión Guardería Exótica", page_icon="🐾", layout="wide")

# Menú de navegación lateral
menu = ["📋 Registrar Dueño y Mascota", "📅 Programar Reservas", "🔍 Visualizar Registros"]
opcion = st.sidebar.selectbox("Módulos del Sistema", menu)

# --- MÓDULO 1: REGISTRO SEGURO ---
if opcion == "📋 Registrar Dueño y Mascota":
    st.title("📋 Registro Seguro de Clientes (Datos Cifrados)")
    db_session = SessionLocal()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Datos del Propietario")
        id_dueno = st.number_input("DNI / ID del Dueño", min_value=1, step=1)
        nombre_dueno = st.text_input("Nombre Completo")
        correo = st.text_input("Correo Electrónico")
        telefono = st.text_input("Teléfono de Contacto")
    with col2:
        st.subheader("Datos de la Mascota")
        id_mascota = st.number_input("Código de la Mascota", min_value=1, step=1)
        nombre_mascota = st.text_input("Nombre de la Mascota")
        especie = st.selectbox("Especie Exótica", ["Reptil", "Ave Exótica", "Anfibio", "Félido", "Otro"])

    if st.button("Guardar Registro"):
        if nombre_dueno and correo and nombre_mascota:
            try:
                # Aplicamos el enmascaramiento criptográfico
                nuevo_dueno = Dueno(
                    id_dueno=id_dueno, 
                    nombre=nombre_dueno, 
                    correo_cifrado=cifrar_dato(correo), 
                    telefono_cifrado=cifrar_dato(telefono)
                )
                nueva_mascota = Mascota(
                    id_mascota=id_mascota, 
                    id_dueno=id_dueno, 
                    nombre_mascota=nombre_mascota, 
                    especie=especie
                )
                
                db_session.add(nuevo_dueno)
                db_session.add(nueva_mascota)
                db_session.commit()
                st.success(f"✅ Dueño y mascota '{nombre_mascota}' almacenados con éxito.")
            except Exception as e:
                db_session.rollback()
                st.error(f"⚠️ Error al guardar: {e}")
        else:
            st.warning("Completa los campos obligatorios.")
    db_session.close()

# --- MÓDULO 2: GESTIÓN DE RESERVAS ---
elif opcion == "📅 Programar Reservas":
    st.title("📅 Reservas de Hospedaje")
    db_session = SessionLocal()
    
    mascotas_db = db_session.query(Mascota).all()
    opciones_mascotas = {f"ID {m.id_mascota} - {m.nombre_mascota} ({m.especie})": m.id_mascota for m in mascotas_db}
    
    if not opciones_mascotas:
        st.info("No existen mascotas registradas en el sistema relacional todavía.")
    else:
        id_reserva = st.number_input("Código de Reserva Único", min_value=1, step=1)
        mascota_sel = st.selectbox("Selecciona la Mascota Hospedada", list(opciones_mascotas.keys()))
        fecha = st.date_input("Fecha de Ingreso")
        restricciones = st.text_area("Restricciones Alimenticias o Cuidados Especiales")
        
        if st.button("Confirmar Reserva"):
            try:
                nueva_reserva = Reserva(
                    id_reserva=id_reserva,
                    id_mascota=opciones_mascotas[mascota_sel],
                    fecha_ingreso=fecha,
                    dieta_restriccion=restricciones
                )
                db_session.add(nueva_reserva)
                db_session.commit()
                st.success(f"✅ Reserva #{id_reserva} agendada de forma satisfactoria.")
            except Exception as e:
                db_session.rollback()
                st.error(f"⚠️ Error al agendar: {e}")
    db_session.close()

# --- MÓDULO 3: VISUALIZACIÓN Y AUDITORÍA ---
elif opcion == "🔍 Visualizar Registros":
    st.title("🔍 Base de Datos en Producción y Descifrado")
    db_session = SessionLocal()
    
    st.subheader("Lista de Clientes Registrados")
    duenos_db = db_session.query(Dueno).all()
    
    for d in duenos_db:
        with st.expander(f"👤 Dueño: {d.nombre} (ID: {d.id_dueno})"):
            st.text(f"🔒 Correo Cifrado (DB): {d.correo_cifrado}")
            st.text(f"🔓 Correo Descifrado (App): {descifrar_dato(d.correo_cifrado)}")
            st.text(f"🔒 Teléfono Cifrado (DB): {d.telefono_cifrado}")
            st.text(f"🔓 Teléfono Descifrado (App): {descifrar_dato(d.telefono_cifrado)}")
            st.markdown("**Mascotas Asociadas:**")
            for m in d.mascotas:
                st.write(f"🐾 {m.nombre_mascota} — Tipo: {m.especie} (ID: {m.id_mascota})")
                
    db_session.close()
