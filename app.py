import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Mega Panel Ultimate", page_icon="🔴", layout="centered")

FILE_HISTORIAL = 'historial_cumplimiento.csv'
FILE_ENTRENOS = 'historial_entrenamientos.csv'

# --- BASE DE DATOS DE PROTOCOLOS (TÉCNICOS) ---
# Aquí están los ajustes exactos para tu BlockBlueLight Mega Panel
DB_PROTOCOLOS = {
    "🔥 Grasa": {
        "desc": "Movilización de lípidos antes del ejercicio.",
        "red": "100%", "nir": "100%", "hz": "0 Hz", 
        "time": "15 min", "dist": "Contacto (0-2 cm)",
        "icon": "🔥"
    },
    "💪 Codos": {
        "desc": "Analgesia para epicóndilo y tendones.",
        "red": "100%", "nir": "100%", "hz": "10 Hz", 
        "time": "10 min", "dist": "Cerca (5-10 cm)",
        "icon": "💪"
    },
    "🦵 Rodilla": {
        "desc": "Reparación profunda (LCA/Menisco).",
        "red": "0% (OFF)", "nir": "100%", "hz": "40 Hz", 
        "time": "15 min", "dist": "Cerca (5 cm)",
        "icon": "🦵"
    },
    "🦴 Hombro": {
        "desc": "Calentamiento y elasticidad fascial.",
        "red": "100%", "nir": "100%", "hz": "0 Hz", 
        "time": "10 min", "dist": "Media (5-10 cm)",
        "icon": "🦴"
    },
    "🧠 Cerebro": {
        "desc": "Neuro-protección y memoria.",
        "red": "0% (OFF)", "nir": "100%", "hz": "10 Hz", 
        "time": "6 min", "dist": "Lejos (30 cm)",
        "icon": "🧠"
    },
    "😴 Sueño": {
        "desc": "Inducción de melatonina.",
        "red": "20%", "nir": "0% (OFF)", "hz": "0 Hz", 
        "time": "20 min", "dist": "Ambiental (>1m)",
        "icon": "😴"
    }
}

OPCIONES_ENTRENO = [
    "Empuje (Fuerza)", "Tracción (Fuerza)", "Preventivo I (Hombro)",
    "Pierna (Fuerza)", "Torso (Accesorios)", "Preventivo II (Rodilla)",
    "Descanso Total", "Cardio Suave"
]

# --- GESTIÓN DE DATOS ---
def cargar_csv(filename, cols):
    if os.path.exists(filename):
        try:
            return pd.read_csv(filename)
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def guardar_estado(fecha_dt, tratamiento, campo, valor):
    # campo puede ser 'Seleccionado' o 'Realizado'
    cols = ["Fecha", "Tratamiento", "Seleccionado", "Realizado"]
    df = cargar_csv(FILE_HISTORIAL, cols)
    fecha_str = fecha_dt.strftime("%Y-%m-%d")
    
    # Upsert
    mask = (df["Fecha"] == fecha_str) & (df["Tratamiento"] == tratamiento)
    if not df[mask].empty:
        df.loc[mask, campo] = valor
    else:
        # Crear nuevo registro por defecto False en todo
        nuevo = {"Fecha": fecha_str, "Tratamiento": tratamiento, "Seleccionado": False, "Realizado": False}
        nuevo[campo] = valor
        df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    
    df.to_csv(FILE_HISTORIAL, index=False)

def obtener_estado(fecha_dt, tratamiento):
    df = cargar_csv(FILE_HISTORIAL, ["Fecha", "Tratamiento", "Seleccionado", "Realizado"])
    fecha_str = fecha_dt.strftime("%Y-%m-%d")
    row = df[(df["Fecha"] == fecha_str) & (df["Tratamiento"] == tratamiento)]
    if not row.empty:
        return bool(row.iloc[0]["Seleccionado"]), bool(row.iloc[0]["Realizado"])
    return False, False # Por defecto no seleccionado, no realizado

def guardar_cambio_entreno(fecha_dt, nuevo_entreno):
    df = cargar_csv(FILE_ENTRENOS, ["Fecha", "Entreno"])
    fecha_str = fecha_dt.strftime("%Y-%m-%d")
    mask = (df["Fecha"] == fecha_str)
    if not df[mask].empty:
        df.loc[mask, "Entreno"] = nuevo_entreno
    else:
        df = pd.concat([df, pd.DataFrame([{"Fecha": fecha_str, "Entreno": nuevo_entreno}])], ignore_index=True)
    df.to_csv(FILE_ENTRENOS, index=False)

def obtener_entreno_real(fecha_dt):
    fecha_str = fecha_dt.strftime("%Y-%m-%d")
    df = cargar_csv(FILE_ENTRENOS, ["Fecha", "Entreno"])
    registro = df[df["Fecha"] == fecha_str]
    if not registro.empty: return registro.iloc[0]["Entreno"]
    
    # Lógica por defecto
    rutina = {0: "Empuje (Fuerza)", 1: "Tracción (Fuerza)", 2: "Preventivo I (Hombro)",
              3: "Pierna (Fuerza)", 4: "Torso (Accesorios)", 5: "Preventivo II (Rodilla)"}
    return rutina.get(fecha_dt.weekday(), "Descanso Total")

# --- MOTOR DE REGLAS ---
def identificar_compatibles(nombre_entreno):
    lista = []
    # Reglas
    if any(x in nombre_entreno for x in ["Empuje", "Tracción", "Pierna", "Torso"]):
        lista.append("🔥 Grasa")
    if any(x in nombre_entreno for x in ["Empuje", "Torso", "Preventivo I"]):
        lista.append("💪 Codos")
    if any(x in nombre_entreno for x in ["Pierna", "Preventivo II"]):
        lista.append("🦵 Rodilla")
    if "Preventivo I" in nombre_entreno:
        lista.append("🦴 Hombro")
    if any(x in nombre_entreno for x in ["Tracción", "Torso", "Descanso"]):
        lista.append("🧠 Cerebro")
    lista.append("😴 Sueño")
    return lista

# --- UI COMPONENT: TARJETA DE DETALLE ---
def mostrar_tarjeta_tecnica(nombre_tratamiento):
    data = DB_PROTOCOLOS[nombre_tratamiento]
    
    with st.container():
        st.markdown(f"#### {data['icon']} {nombre_tratamiento}")
        st.caption(data['desc'])
        
        # Grid de datos técnicos
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔴 RED", data['red'])
        c2.metric("🌫️ NIR", data['nir'])
        c3.metric("⚡ Hz", data['hz'])
        c4.metric("📏 Dist", data['dist'])
        
        st.info(f"⏱️ **Tiempo:** {data['time']}")

# --- APP PRINCIPAL ---
st.title("🔴 Mega Panel Ultimate")
tab1, tab2 = st.tabs(["⚡ Planificador Diario", "🗓️ Calendario"])

with tab1:
    col_date, col_spacer = st.columns([2, 1])
    fecha_sel = col_date.date_input("Fecha", datetime.now())
    
    # SECCIÓN A: ENTRENO
    entreno_actual = obtener_entreno_real(fecha_sel)
    idx = OPCIONES_ENTRENO.index(entreno_actual) if entreno_actual in OPCIONES_ENTRENO else 6
    nuevo_entreno = st.selectbox("🏋️ Entrenamiento:", OPCIONES_ENTRENO, index=idx)
    
    if nuevo_entreno != entreno_actual:
        guardar_cambio_entreno(fecha_sel, nuevo_entreno)
        st.rerun()

    posibles = identificar_compatibles(nuevo_entreno)
    
    st.divider()
    
    # SECCIÓN B: SELECCIÓN (QUÉ QUIERO HACER)
    st.subheader("1️⃣ Selección: ¿Qué harás hoy?")
    st.caption("Marca los tratamientos que quieres incluir en tu rutina de hoy.")
    
    seleccionados_hoy = []
    
    cols_sel = st.columns(2)
    for i, nombre in enumerate(posibles):
        sel, _ = obtener_estado(fecha_sel, nombre)
        # Checkbox de selección
        col_actual = cols_sel[i % 2]
        if col_actual.checkbox(f"{nombre}", value=sel, key=f"sel_{nombre}_{fecha_sel}"):
            if not sel: guardar_estado(fecha_sel, nombre, "Seleccionado", True)
            seleccionados_hoy.append(nombre)
        else:
            if sel: guardar_estado(fecha_sel, nombre, "Seleccionado", False)

    st.divider()

    # SECCIÓN C: EJECUCIÓN (CÓMO HACERLO)
    st.subheader("2️⃣ Ejecución: Detalles Técnicos")
    
    if not seleccionados_hoy:
        st.info("👆 Selecciona arriba los tratamientos para ver sus ajustes.")
    else:
        progreso = 0
        for item in seleccionados_hoy:
            _, realizado = obtener_estado(fecha_sel, item)
            
            # Marco visual
            with st.expander(f"{item} {'✅' if realizado else ''}", expanded=not realizado):
                mostrar_tarjeta_tecnica(item)
                
                # Botón de Completado
                check_realizado = st.checkbox("✅ Marcar como COMPLETADO", value=realizado, key=f"done_{item}_{fecha_sel}")
                if check_realizado != realizado:
                    guardar_estado(fecha_sel, item, "Realizado", check_realizado)
                    st.rerun()

with tab2:
    st.subheader("Historial Visual")
    # (El código del calendario se mantiene igual que la versión anterior, 
    #  puedes copiarlo de la V4 o dejarlo simple para ahorrar espacio aquí)
    st.write("Tus datos se guardan en `historial_cumplimiento.csv`")
    df = cargar_csv(FILE_HISTORIAL, ["Fecha", "Tratamiento", "Realizado"])
    if not df.empty:
        st.dataframe(df[df["Realizado"]==True].sort_values("Fecha", ascending=False))
