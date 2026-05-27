import os
import jwt
import datetime
import streamlit as st
from sqlalchemy.orm import Session

# Importaciones desde db.py
from db import (
    SessionLocal, Reserva, Dueno, Mascota,
    cifrar_dato, descifrar_dato,
    inicializar_base_de_datos,
    verificar_credenciales
)

# Inicializar tablas en la base de datos
inicializar_base_de_datos()

# Clave secreta para firmar tokens JWT (en producción usar variable de entorno)
JWT_SECRET = os.getenv("JWT_SECRET", "clave_secreta_academica_guarderia")

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==============================================================================
st.set_page_config(page_title="Reserva Fauna Exótica", page_icon="🦎", layout="wide")

st.markdown("""
    <style>
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
        /* Texto blanco en el sidebar verde */
        [data-testid="stSidebar"] { color: #FFFFFF !important; }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span { color: #FFFFFF !important; font-weight: 500; }
        [data-testid="stSidebar"] div[role="radiogroup"] label p { color: #FFFFFF !important; }
        .stTextInput > div > div > input { border-radius: 10px; }

        /* Estilo del panel de login */
        .login-box {
            background-color: #ffffff;
            padding: 35px 40px;
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(39,174,96,0.12);
            border-top: 5px solid #2ECC71;
            max-width: 420px;
            margin: 60px auto;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# GESTIÓN DE SESIÓN CON JWT en st.session_state
# ==============================================================================
def generar_token(usuario: str) -> str:
    """Genera un token JWT con expiración de 1 hora para el usuario autenticado."""
    payload = {
        "sub": usuario,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def validar_token(token: str) -> str | None:
    """
    Valida el token JWT. Retorna el nombre de usuario si es válido,
    o None si expiró o es inválido.
    """
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return data["sub"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Inicializar variables de sesión si no existen
if "jwt_token" not in st.session_state:
    st.session_state["jwt_token"] = None
if "usuario_activo" not in st.session_state:
    st.session_state["usuario_activo"] = None

# ==============================================================================
# PANTALLA DE LOGIN
# Se muestra si no hay token válido en session_state.
# ==============================================================================
def mostrar_login():
    st.markdown('<p class="main-title">🦎 EcoReserve — Guardería de Fauna Exótica</p>', unsafe_allow_html=True)
    st.markdown("*Plataforma de alta seguridad con encriptación relacional en tiempo real.*")
    st.markdown("<br>", unsafe_allow_html=True)

    # Centrar el formulario usando columnas
    col_izq, col_centro, col_der = st.columns([1, 1.4, 1])
    with col_centro:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("### 🔐 Iniciar Sesión")
        st.markdown("Ingresa tus credenciales para acceder al sistema.")
        st.markdown("<br>", unsafe_allow_html=True)

        usuario  = st.text_input("👤 Usuario", placeholder="Ej. boris", key="login_usuario")
        password = st.text_input("🔑 Contraseña", type="password", placeholder="••••••••", key="login_password")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Ingresar →", use_container_width=True):
            if not usuario or not password:
                st.warning("⚠️ Debes ingresar usuario y contraseña.")
            elif verificar_credenciales(usuario, password):
                # Credenciales válidas: generar JWT y guardar en session_state
                token = generar_token(usuario)
                st.session_state["jwt_token"]      = token
                st.session_state["usuario_activo"] = usuario
                st.success(f"✅ Bienvenido, **{usuario}**. Cargando sistema...")
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")

        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# APLICACIÓN PRINCIPAL
# Solo se muestra si hay un token JWT válido en session_state.
# ==============================================================================
def mostrar_app():
    usuario_activo = st.session_state.get("usuario_activo", "Usuario")

    # --------------------------------------------------------------------------
    # DASHBOARD: métricas operativas
    # --------------------------------------------------------------------------
    db_session = SessionLocal()
    total_duenos   = db_session.query(Dueno).count()
    total_mascotas = db_session.query(Mascota).count()
    total_reservas = db_session.query(Reserva).count()
    db_session.close()

    st.markdown('<p class="main-title">🦎 EcoReserve — Guardería de Fauna Exótica</p>', unsafe_allow_html=True)
    st.markdown(f"*Sesión activa: **{usuario_activo}** — Plataforma de alta seguridad con encriptación relacional en tiempo real.*")
    st.markdown("<br>", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f'<div style="background-color:#E8F5E9;padding:15px;border-radius:12px;border-bottom:4px solid #2ECC71;text-align:center;">'
            f'<span style="color:#1E8449;font-weight:bold;font-size:14px;">👥 PROPIETARIOS ACTIVOS</span><br>'
            f'<span style="font-size:30px;font-weight:800;color:#1E8449;">{total_duenos}</span></div>',
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f'<div style="background-color:#FFF3E0;padding:15px;border-radius:12px;border-bottom:4px solid #FF9800;text-align:center;">'
            f'<span style="color:#E65100;font-weight:bold;font-size:14px;">🦎 EJEMPLARES EN CUSTODIA</span><br>'
            f'<span style="font-size:30px;font-weight:800;color:#EF6C00;">{total_mascotas}</span></div>',
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f'<div style="background-color:#E3F2FD;padding:15px;border-radius:12px;border-bottom:4px solid #2196F3;text-align:center;">'
            f'<span style="color:#0D47A1;font-weight:bold;font-size:14px;">📅 PLAZAS RESERVADAS</span><br>'
            f'<span style="font-size:30px;font-weight:800;color:#1565C0;">{total_reservas}</span></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SIDEBAR: navegación + botón cerrar sesión
    # --------------------------------------------------------------------------
    st.sidebar.markdown("## 🧭 Navegación")
    menu   = ["📋 Registrar Ingreso", "📅 Agendar Hospedaje", "🔍 Sala de Auditoría Cifrada"]
    opcion = st.sidebar.radio("Selecciona un módulo:", menu)

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state["jwt_token"]      = None
        st.session_state["usuario_activo"] = None
        st.rerun()

    # --------------------------------------------------------------------------
    # MÓDULO 1: Registro seguro de clientes
    # --------------------------------------------------------------------------
    if opcion == "📋 Registrar Ingreso":
        st.markdown("### 📋 Formulario de Check-in Biológico")
        db_session = SessionLocal()

        col1, col2 = st.columns(2)
        with col1:
            st.info("👤 Datos de Identidad del Tutor")
            id_dueno      = st.number_input("Número de DNI / Pasaporte", min_value=1, step=1)
            nombre_dueno  = st.text_input("Nombre Completo del Propietario")
            correo        = st.text_input("Dirección de Correo")
            telefono      = st.text_input("Teléfono Urgencias (24/7)")
        with col2:
            st.warning("🦖 Ficha de Taxonomía de la Mascota")
            id_mascota     = st.number_input("Código de Microchip / ID Animal", min_value=1, step=1)
            nombre_mascota = st.text_input("Nombre del Especímen")
            especie        = st.selectbox(
                "Clasificación de Especie",
                ["Reptil 🐍", "Ave Exótica 🦅", "Anfibio 🐸", "Félido Salvaje 🐆", "Invertebrado 🕷️"]
            )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Encriptar y Guardar en Matriz Relacional", use_container_width=True):
            if nombre_dueno and correo and nombre_mascota:
                try:
                    # Cifrar datos sensibles con Fernet antes de persistir en PostgreSQL
                    nuevo_dueno = Dueno(
                        id_dueno         = id_dueno,
                        nombre           = nombre_dueno,
                        correo_cifrado   = cifrar_dato(correo),
                        telefono_cifrado = cifrar_dato(telefono)
                    )
                    # Limpiar el emoji de la especie seleccionada (ej: "Reptil 🐍" → "Reptil")
                    especie_limpia = especie.split()[0]
                    nueva_mascota = Mascota(
                        id_mascota     = id_mascota,
                        id_dueno       = id_dueno,
                        nombre_mascota = nombre_mascota,
                        especie        = especie_limpia
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

    # --------------------------------------------------------------------------
    # MÓDULO 2: Gestión de reservas
    # --------------------------------------------------------------------------
    elif opcion == "📅 Agendar Hospedaje":
        st.markdown("### 📅 Cronograma de Hábitats y Nutrición")
        db_session = SessionLocal()

        mascotas_db      = db_session.query(Mascota).all()
        opciones_mascotas = {
            f"🆔 ID {m.id_mascota} — Animal: {m.nombre_mascota} ({m.especie})": m.id_mascota
            for m in mascotas_db
        }

        if not opciones_mascotas:
            st.info("🦎 No se detectan animales registrados. Registra un ejemplar primero.")
        else:
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                id_reserva   = st.number_input("Código de Reserva Interno", min_value=1, step=1)
                mascota_sel  = st.selectbox("Asignar Reserva a:", list(opciones_mascotas.keys()))
                fecha        = st.date_input("Fecha de Ingreso al Recinto")
            with col_res2:
                restricciones = st.text_area("Prescripción Médica / Dieta Estricta (Vivo/Suplementos)")

                if restricciones:
                    st.markdown(
                        '<div style="background-color:#FFEBEE;padding:12px;border-radius:8px;'
                        'border-left:5px solid #D32F2F;color:#C62828;font-weight:bold;">'
                        '🚨 ALERTA NUTRICIONAL ACTIVA: Se notificará al personal de biólogos del sector.'
                        '</div>', unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<div style="background-color:#E8F5E9;padding:12px;border-radius:8px;'
                        'border-left:5px solid #2E7D32;color:#2E7D32;">'
                        '🍏 Protocolo alimenticio basal (Sin condiciones clínicas reportadas).'
                        '</div>', unsafe_allow_html=True
                    )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📅 Confirmar Asignación de Hábitat", use_container_width=True):
                try:
                    nueva_reserva = Reserva(
                        id_reserva        = id_reserva,
                        id_mascota        = opciones_mascotas[mascota_sel],
                        fecha_ingreso     = fecha,
                        dieta_restriccion = restricciones
                    )
                    db_session.add(nueva_reserva)
                    db_session.commit()
                    st.success(f"✅ Hábitat reservado con éxito bajo el registro de control #{id_reserva}.")
                except Exception as e:
                    db_session.rollback()
                    st.error(f"❌ Error de persistencia: {e}")
        db_session.close()

    # --------------------------------------------------------------------------
    # MÓDULO 3: Auditoría cifrada
    # --------------------------------------------------------------------------
    elif opcion == "🔍 Sala de Auditoría Cifrada":
        st.markdown("### 🔍 Monitor de Registros y Desencapsulado Criptográfico")
        db_session = SessionLocal()
        duenos_db  = db_session.query(Dueno).all()

        if not duenos_db:
            st.info("📂 El repositorio relacional de Postgres se encuentra vacío.")
        else:
            for d in duenos_db:
                st.markdown(
                    f'<div class="custom-card">'
                    f'<div class="card-header">👤 Propietario: <b>{d.nombre}</b> &nbsp;|&nbsp; '
                    f'<span style="font-size:14px;color:#555;">Código Relacional: <b>{d.id_dueno}</b></span></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                c_datos, c_mascotas = st.columns(2)
                with c_datos:
                    st.markdown("**🛡️ Estado de Seguridad de Datos (Capa Fernet/AES-128):**")

                    st.markdown("📧 **Correo en Postgres (Cifrado):**")
                    st.markdown(f'<div class="crypto-block">{d.correo_cifrado}</div>', unsafe_allow_html=True)
                    st.markdown(f"🔓 **Correo Descifrado (Runtime):** `{descifrar_dato(d.correo_cifrado)}`")

                    st.markdown("📞 **Teléfono en Postgres (Cifrado):**")
                    st.markdown(f'<div class="crypto-block">{d.telefono_cifrado}</div>', unsafe_allow_html=True)
                    st.markdown(f"🔓 **Teléfono Descifrado (Runtime):** `{descifrar_dato(d.telefono_cifrado)}`")

                with c_mascotas:
                    st.markdown("**🧬 Especímenes Asociados en Bioterio:**")
                    if not d.mascotas:
                        st.caption("Ningún ejemplar vinculado a este tutor.")
                    else:
                        for m in d.mascotas:
                            emoji_map = {
                                "Reptil": "🐍", "Ave": "🦅", "Anfibio": "🐸",
                                "Félido": "🐆", "Invertebrado": "🕷️"
                            }
                            emoji = emoji_map.get(m.especie, "🐾")
                            st.markdown(
                                f"### {emoji} {m.nombre_mascota} "
                                f"<span style='font-size:14px;color:#777;font-weight:normal;'>({m.especie})</span>",
                                unsafe_allow_html=True
                            )
                            if m.reservas:
                                for r in m.reservas:
                                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;📅 **Estadía #{r.id_reserva}** — Ingreso: `{r.fecha_ingreso}`")
                                    if r.dieta_restriccion:
                                        st.markdown(
                                            f"&nbsp;&nbsp;&nbsp;&nbsp;⚠️ *Dieta Crítica:* "
                                            f"<span style='color:#D32F2F;'><b>{r.dieta_restriccion}</b></span>",
                                            unsafe_allow_html=True
                                        )
                            else:
                                st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;*Sin registros de estadías activas.*")

                st.markdown("<br>", unsafe_allow_html=True)
        db_session.close()

# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# Decide si mostrar el login o la app según el estado del token JWT.
# ==============================================================================
token_actual = st.session_state.get("jwt_token")

if token_actual is None:
    # No hay token → mostrar pantalla de login
    mostrar_login()
else:
    # Hay token → validarlo antes de mostrar la app
    usuario_validado = validar_token(token_actual)
    if usuario_validado is None:
        # Token expirado o inválido → limpiar sesión y volver al login
        st.session_state["jwt_token"]      = None
        st.session_state["usuario_activo"] = None
        st.warning("⏰ Tu sesión ha expirado. Por favor, inicia sesión nuevamente.")
        mostrar_login()
    else:
        # Token válido → mostrar aplicación completa
        mostrar_app()
