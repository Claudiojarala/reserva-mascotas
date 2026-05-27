import os
import streamlit as st
from sqlalchemy.orm import Session

# Importaciones relacionales desde db.py
from db import SessionLocal, Reserva, Dueno, Mascota, cifrar_dato, descifrar_dato, inicializar_base_de_datos

# Inicializar base de datos
inicializar_base_de_datos()

# ==============================================================================
# 🎨 CAPA DE DISEÑO AVANZADO: FORZAR TEXTOS BLANCOS EN EL MENÚ LATERAL VÍA CSS
# ==============================================================================
st.set_page_config(page_title="Reserva Fauna Exótica", page_icon="🦎", layout="wide")

st.markdown("""
    <style>
        /* --- ESTILOS EN EL ÁREA PRINCIPAL --- */
        .main-title {
            font-size: 42px !important;
            font-weight: 800;
            color: #1E8449;
            margin-bottom: 5px;
        }
        .custom-card {
            background-color: #ffffff;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(39, 174, 96, 0.06);
            border-left: 6px solid #2ECC71;
            margin-bottom: 25px;
        }
        .card-header {
            color: #212121;
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 15px;
        }
        .crypto-block {
            background-color: #F4F6F4;
            padding: 8px 12px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            color: #555;
            margin-bottom: 10px;
            border: 1px dashed #2ECC71;
        }

        /* --- SOLUCIÓN DE VISIBILIDAD: FORZAR TEXTO BLANCO EN EL CUADRO VERDE (SIDEBAR) --- */
        [data-testid="stSidebar"] {
            color: #FFFFFF !important;
        }
        /* Forzar títulos, textos de radio buttons y subtítulos a blanco */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] span {
            color: #FFFFFF !important;
            font-weight: 500;
        }
        /* Asegurar que las opciones del Radio Button también sean completamente blancas */
        [data-testid="stSidebar"] div[role="radiogroup"] label p {
            color: #FFFFFF !important;
        }
        
        /* Ajustar bordes redondeados en los inputs principales */
        .stTextInput > div > div > input {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# DASHBOARD: CÁLCULO DE MÉTRICAS OPERATIVAS
# ==============================================================================
db_session = SessionLocal()
total_duenos = db_session.query(Dueno).count()
total_mascotas = db_session.query(Mascota).count()
total_reservas = db_session.query(Reserva).count()
db_session.close()

# Encabezado del Sistema
st.markdown('<p class="main-title">🦎 EcoReserve — Guardería de Fauna Exótica</p>', unsafe_allow_html=True)
st.markdown("*Plataforma de alta seguridad con encriptación relacional en tiempo real.*")
st.markdown("<br>", unsafe_allow_html=True)

# Tarjetas de Métricas Estilizadas
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown('<div style="background-color: #E8F5E9; padding: 15px; border-radius: 12px; border-bottom: 4px solid #2ECC71; text-align: center;">'
                f'<span style="color: #1E8449; font-weight: bold; font-size: 14px;">👥 PROPIETARIOS ACTIVOS</span><br>'
                f'<span style="font-size: 30px; font-weight: 800; color: #1E8449;">{total_duenos}</span>'
                '</div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div style="background-color: #FFF3E0; padding: 15px; border-radius: 12px; border-bottom: 4px solid #FF9800; text-align: center;">'
                f'<span style="color: #E65100; font-weight: bold; font-size: 14px;">🦎 EJEMPLARES EN CUSTODIA</span><br>'
                f'<span style="font-size: 30px; font-weight: 800; color: #EF6C00;">{total_mascotas}</span>'
                '</div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div style="background-color: #E3F2FD; padding: 15px; border-radius: 12px; border-bottom: 4px solid #2196F3; text-align: center;">'
                f'<span style="color: #0D47A1; font-weight: bold; font-size: 14px;">📅 PLAZAS RESERVADAS</span><br>'
                f'<span style="font-size: 30px; font-weight: 800; color: #1565C0;">{total_reservas}</span>'
                '</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==============================================================================
# MENÚ LATERAL (SIDEBAR) - TODO SE VERÁ BLANCO AQUÍ
# ==============================================================================
st.sidebar.markdown("## 🧭 Navegación")
menu = ["📋 Registrar Ingreso", "📅 Agendar Hospedaje", "🔍 Sala de Auditoría Cifrada"]
opcion = st.sidebar.radio("Selecciona un módulo:", menu)

# ==============================================================================
# MÓDULO 1: REGISTRO SEGURO DE CLIENTES
# ==============================================================================
if opcion == "📋 Registrar Ingreso":
    st.markdown("### 📋 Formulario de Check-in Biológico")
    db_session = SessionLocal()
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("👤 Datos de Identidad del Tutor")
        id_dueno = st.number_input("Número de DNI / Pasaporte", min_value=1, step=1)
        nombre_dueno = st.text_input("Nombre Completo del Propietario")
        correo = st.text_input("Dirección de Correo")
        telefono = st.text_input("Teléfono Urgencias (24/7)")
    with col2:
        st.warning("🦖 Ficha de Taxonomía de la Mascota")
        id_mascota = st.number_input("Código de Microchip / ID Animal", min_value=1, step=1)
        nombre_mascota = st.text_input("Nombre del Especímen")
        especie = st.selectbox("Clasificación de Especie", ["Reptil 🐍", "Ave Exótica 🦅", "Anfibio 🐸", "Félido Salvaje 🐆", "Invertebrado 🕷️"])

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Encriptar y Guardar en Matriz Relacional", use_container_width=True):
        if nombre_dueno and correo and nombre_mascota:
            try:
                nuevo_dueno = Dueno(
                    id_dueno=id_dueno, nombre=nombre_dueno, 
                    correo_cifrado=cifrar_dato(correo), telefono_cifrado=cifrar_dato(telefono)
                )
                especie_limpia = especie.split()
                nueva_mascota = Mascota(
                    id_mascota=id_mascota, id_dueno=id_dueno, 
                    nombre_mascota=nombre_mascota, especie=especie_limpia
                )
                
                db_session.add(nuevo_dueno)
                db_session.add(nueva_mascota)
                db_session.commit()
                st.success(f"🎉 ¡Completado! {nombre_mascota} ha sido ingresado al sistema de forma segura.")
                st.balloons()
            except Exception as e:
                db_session.rollback()
                st.error(f"❌ Error transaccional en Postgres: {e}")
        else:
            st.error("⚠️ Error: Todos los campos con texto son obligatorios.")
    db_session.close()

# ==============================================================================
# MÓDULO 2: GESTIÓN DE RESERVAS
# ==============================================================================
elif opcion == "📅 Agendar Hospedaje":
    st.markdown("### 📅 Cronograma de Hábitats y Nutrición")
    db_session = SessionLocal()
    
    mascotas_db = db_session.query(Mascota).all()
    opciones_mascotas = {f"🆔 ID {m.id_mascota} — Animal: {m.nombre_mascota} ({m.especie})": m.id_mascota for m in mascotas_db}
    
    if not opciones_mascotas:
        st.info("🦎 No se detectan animales registrados. Registra un ejemplar primero.")
    else:
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            id_reserva = st.number_input("Código de Reserva Interno", min_value=1, step=1)
            mascota_sel = st.selectbox("Asignar Reserva a:", list(opciones_mascotas.keys()))
            fecha = st.date_input("Fecha de Ingreso al Recinto")
        with col_res2:
            restricciones = st.text_area("Prescripción Médica / Dieta Estricta (Vivo/Suplementos)")
            
            if restricciones:
                st.markdown('<div style="background-color: #FFEBEE; padding: 12px; border-radius: 8px; border-left: 5px solid #D32F2F; color: #C62828; font-weight: bold;">'
                            '🚨 ALERTA NUTRICIONAL ACTIVA: Se notificará al personal de biólogos del sector.'
                            '</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="background-color: #E8F5E9; padding: 12px; border-radius: 8px; border-left: 5px solid #2E7D32; color: #2E7D32;">'
                            '🍏 Protocolo alimenticio basal (Sin condiciones clínicas reportadas).'
                            '</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📅 Confirmar Asignación de Hábitat", use_container_width=True):
            try:
                nueva_reserva = Reserva(
                    id_reserva=id_reserva, id_mascota=opciones_mascotas[mascota_sel],
                    fecha_ingreso=fecha, dieta_restriccion=restricciones
                )
                db_session.add(nueva_reserva)
                db_session.commit()
                st.success(f"✅ Hábitat reservado con éxito bajo el registro de control #{id_reserva}.")
            except Exception as e:
                db_session.rollback()
                st.error(f"❌ Error de persistencia: {e}")
    db_session.close()

# ==============================================================================
# MÓDULO 3: VISUALIZACIÓN Y AUDITORÍA
# ==============================================================================
elif opcion == "🔍 Sala de Auditoría Cifrada":
    st.markdown("### 🔍 Monitor de Registros y Desencapsulado Criptográfico")
    db_session = SessionLocal()
    duenos_db = db_session.query(Dueno).all()
    
    if not duenos_db:
        st.info("📂 El repositorio relacional de Postgres se encuentra vacío.")
    else:
        for d in duenos_db:
            card_html = f"""
            <div class="custom-card">
                <div class="card-header">👤 Propietario: <b>{d.nombre}</b> &nbsp;|&nbsp; <span style='font-size:14px; color:#555;'>Código Relacional: <b>{d.id_dueno}</b></span></div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            c_datos, c_mascotas = st.columns(2)
            with c_datos:
                st.markdown("**🛡️ Estado de Seguridad de Datos (Capa AES/XOR):**")
                
                st.markdown(f"📧 **Correo en Postgres (Cifrado):**")
                st.markdown(f'<div class="crypto-block">{d.correo_cifrado}</div>', unsafe_allow_html=True)
                st.markdown(f"🔓 **Correo Descifrado (Runtime):** `{descifrar_dato(d.correo_cifrado)}`")
                
                st.markdown(f"📞 **Teléfono en Postgres (Cifrado):**")
                st.markdown(f'<div class="crypto-block">{d.telefono_cifrado}</div>', unsafe_allow_html=True)
                st.markdown(f"🔓 **Teléfono Descifrado (Runtime):** `{descifrar_dato(d.telefono_cifrado)}`")
            
            with c_mascotas:
                st.markdown("**🧬 Especímenes Asociados en Bioterio:**")
                if not d.mascotas:
                    st.caption("Ningún ejemplar vinculado a este tutor.")
                else:
                    for m in d.mascotas:
                        emoji = "🐍" if m.especie == "Reptil" else "🦅" if m.especie == "Ave" else "🐸" if m.especie == "Anfibio" else "🐆" if m.especie == "Félido" else "🕷️" if m.especie == "Invertebrado" else "🐾"
                        st.markdown(f"### {emoji} {m.nombre_mascota} <span style='font-size:14px; color:#777; font-weight:normal;'>({m.especie})</span>", unsafe_allow_html=True)
                        
                        if m.reservas:
                            for r in m.reservas:
                                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;📅 **Estadía #{r.id_reserva}** — Ingreso: `{r.fecha_ingreso}`")
                                if r.dieta_restriccion:
                                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;⚠️ *Dieta Crítica:* <span style='color:#D32F2F;'><b>{r.dieta_restriccion}</b></span>", unsafe_allow_html=True)
                        else:
                            st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;*Sin registros de estadías activas.*")
            st.markdown("<br>", unsafe_allow_html=True)
            
    db_session.close()
