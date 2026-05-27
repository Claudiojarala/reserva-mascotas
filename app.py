import os
import streamlit as st
from sqlalchemy.orm import Session

# Importaciones directas desde tu db.py relacional
from db import SessionLocal, Reserva, Dueno, Mascota, cifrar_dato, descifrar_dato, inicializar_base_de_datos

# Inicializar las tablas relacionales en la base Postgres de Railway
inicializar_base_de_datos()

# ==============================================================================
# CONFIGURACIÓN DE LA INTERFAZ GRÁFICA (Estilo Profesional)
# ==============================================================================
st.set_page_config(page_title="Gestión Guardería Exótica", page_icon="🐾", layout="wide")

# --- CONTROL DE CONTENIDO DINÁMICO (Métricas Rápidas en el Home) ---
db_session = SessionLocal()
total_duenos = db_session.query(Dueno).count()
total_mascotas = db_session.query(Mascota).count()
total_reservas = db_session.query(Reserva).count()
db_session.close()

# Encabezado Principal del Dashboard
st.markdown("# 🐾 Panel de Control — Guardería de Fauna Exótica")
st.caption("Sistema transaccional seguro con capa criptográfica integrada en persistencia.")

# Renderizado de Tarjetas de Métricas (Inspirado en Sazón Perú)
m1, m2, m3 = st.columns(3)
with m1:
    st.metric(label="👥 Propietarios Registrados", value=total_duenos)
with m2:
    st.metric(label="🦎 Pacientes en Sistema", value=total_mascotas)
with m3:
    st.metric(label="📅 Estadías/Reservas Activas", value=total_reservas)

st.divider()

# Menú de navegación lateral estilizado
menu = ["📋 Registrar Dueño y Mascota", "📅 Programar Reservas", "🔍 Visualizar Registros y Auditoría"]
opcion = st.sidebar.selectbox("Módulos del Sistema", menu)

# ==============================================================================
# MÓDULO 1: REGISTRO SEGURO DE CLIENTES
# ==============================================================================
if opcion == "📋 Registrar Dueño y Mascota":
    st.subheader("📋 Alta de Clientes y Especies Exóticas")
    db_session = SessionLocal()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 👤 Datos del Propietario")
        id_dueno = st.number_input("DNI / ID del Dueño", min_value=1, step=1)
        nombre_dueno = st.text_input("Nombre Completo")
        correo = st.text_input("Correo Electrónico")
        telefono = st.text_input("Teléfono de Contacto")
    with col2:
        st.markdown("### 🦎 Características del Especécimen")
        id_mascota = st.number_input("Código de la Mascota Único", min_value=1, step=1)
        nombre_mascota = st.text_input("Nombre de la Mascota")
        especie = st.selectbox("Especie Clasificada", ["Reptil", "Ave Exótica", "Anfibio", "Félido", "Otro"])

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Guardar Registro en Base de Datos", use_container_width=True):
        if nombre_dueno and correo and nombre_mascota:
            try:
                # Aplicamos la máscara criptográfica definida en tu db.py
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
                st.success(f"✅ Éxito: Se ha guardado a {nombre_dueno} y su mascota '{nombre_mascota}' de forma cifrada.")
                st.balloons()
            except Exception as e:
                db_session.rollback()
                st.error(f"⚠️ Error en la transacción relacional: {e}")
        else:
            st.warning("⚠️ Campos Mandatorios: Por favor, completa los datos obligatorios antes de guardar.")
    db_session.close()

# ==============================================================================
# MÓDULO 2: GESTIÓN DE RESERVAS Y ALERTAS DE DIETA
# ==============================================================================
elif opcion == "📅 Programar Reservas":
    st.subheader("📅 Planificación de Estadías y Dietas Clínicas")
    db_session = SessionLocal()
    
    mascotas_db = db_session.query(Mascota).all()
    opciones_mascotas = {f"ID {m.id_mascota} - {m.nombre_mascota} ({m.especie})": m.id_mascota for m in mascotas_db}
    
    if not opciones_mascotas:
        st.info("ℹ️ Base relacional vacía. Registra una mascota en el módulo anterior para agendar hospedajes.")
    else:
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            id_reserva = st.number_input("Código de Reserva Único", min_value=1, step=1)
            mascota_sel = st.selectbox("Selecciona la Mascota Hospedada", list(opciones_mascotas.keys()))
            fecha = st.date_input("Fecha de Ingreso al Recinto")
        with col_res2:
            restricciones = st.text_area("Restricciones Alimenticias o Cuidados Clínicos Especiales (Crucial)")
            
            # Alerta dinámica visual en tiempo real según lo que escribe el usuario
            if restricciones:
                st.error("🚨 **ATENCIÓN:** Se ha especificado una restricción médica. Se registrará como alerta de alta prioridad.")
            else:
                st.success("🍏 **DIETA ESTÁNDAR:** Mascota sana sin condiciones clínicas especiales reportadas.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📅 Confirmar y Reservar Plaza", use_container_width=True):
            try:
                nueva_reserva = Reserva(
                    id_reserva=id_reserva,
                    id_mascota=opciones_mascotas[mascota_sel],
                    fecha_ingreso=fecha,
                    dieta_restriccion=restricciones
                )
                db_session.add(nueva_reserva)
                db_session.commit()
                st.success(f"✅ Reserva #{id_reserva} programada y vinculada correctamente.")
            except Exception as e:
                db_session.rollback()
                st.error(f"⚠️ Fallo al guardar la reserva: {e}")
    db_session.close()

# ==============================================================================
# MÓDULO 3: VISUALIZACIÓN DE REGISTROS Y AUDITORÍA CRIPTOGRÁFICA
# ==============================================================================
elif opcion == "🔍 Visualizar Registros y Auditoría":
    st.subheader("🔍 Auditoría de Datos en Producción y Desencapsulado")
    db_session = SessionLocal()
    
    duenos_db = db_session.query(Dueno).all()
    
    if not duenos_db:
        st.info("ℹ️ No hay registros guardados en la base de datos de Postgres en Railway.")
    else:
        for d in duenos_db:
            # Tarjeta contenedora visual por cada cliente
            with st.container():
                st.markdown(f"### 👤 Cliente: {d.nombre} — (Código Relacional: `{d.id_dueno}`)")
                
                c_datos, c_mascotas = st.columns(2)
                with c_datos:
                    st.markdown("**🛡️ Seguridad de Datos en Reposo (Campos Cifrados):**")
                    st.caption(f"📧 **Correo en Postgres:** `{d.correo_cifrado[:22]}...`")
                    st.markdown(f"🔓 **Correo Descifrado:** {descifrar_dato(d.correo_cifrado)}")
                    st.caption(f"📞 **Teléfono en Postgres:** `{d.telefono_cifrado[:22]}...`")
                    st.markdown(f"🔓 **Teléfono Descifrado:** {descifrar_dato(d.telefono_cifrado)}")
                
                with c_mascotas:
                    st.markdown("**🦎 Especímenes Asociados:**")
                    if not d.mascotas:
                        st.caption("Este cliente no cuenta con mascotas asignadas.")
                    else:
                        for m in d.mascotas:
                            # Emojis dinámicos idénticos al estilo de Sazón Perú
                            emoji = "🦎" if m.especie == "Reptil" else "🦅" if m.especie == "Ave Exótica" else "🐸" if m.especie == "Anfibio" else "🐆" if m.especie == "Félido" else "🐾"
                            st.markdown(f"{emoji} **{m.nombre_mascota}** — *{m.especie}* (ID: `{m.id_mascota}`)")
                            
                            # Mostrar las reservas e indicaciones médicas directamente en la tarjeta de la mascota
                            if m.reservas:
                                for r in m.reservas:
                                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;📅 **Reserva #{r.id_reserva}** (Ingreso: {r.fecha_ingreso})")
                                    if r.dieta_restriccion:
                                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;❌ *Dieta Estricta:* `{r.dieta_restriccion}`")
                            else:
                                st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;*Sin estadías agendadas actualmente.*")
                st.markdown("---")
                
    db_session.close()
