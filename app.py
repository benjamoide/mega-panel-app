import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os

# --- CONFIGURACIÓN VISUAL SIMPLE (MOBILE FRIENDLY) ---
st.set_page_config(page_title="Mega Panel Mobile", page_icon="📱", layout="centered")

FILE_HISTORIAL = 'historial_cumplimiento.csv'
FILE_ENTRENOS = 'historial_entrenamientos.csv'

# --- BASE DE DATOS ---
OPCIONES_ENTRENO = [
    "Descanso", "Fullbody I", "Torso I", "Preventivo I",
    "Fullbody II", "Torso + Circuito", "Preventivo II"
]

DB_TRATAMIENTOS = {
    "🔥 Grasa Abdominal": {
        "keywords_compatibles": ["Fullbody", "Torso", "Circuito"], 
        "dias_descanso_min": 0, "momento": "PRE-ENTRENO", "orden": 1, 
        "aviso": "⚠️ OBLIGATORIO: Ejercicio en los siguientes 60 min.",
        "config": "🔴 RED + NIR (100%) | 0 Hz",
        "uso": "15 min | CONTACTO PIEL"
    },
    "🦴 Hombro (Activación)": {
        "keywords_compatibles": ["Preventivo I"],
        "dias_descanso_min": 0, "momento": "PRE-ENTRENO", "orden": 1,
        "aviso": "Hacer justo antes de las gomas.",
        "config": "🔴 RED + NIR (100%) | 0 Hz",
        "uso": "10 min | 5-10 cm"
    },
    "🧠 Cerebro / Foco": {
        "keywords_compatibles": ["Torso I", "Torso + Circuito", "Descanso"],
        "dias_descanso_min": 1, "momento": "MAÑANA", "orden": 1,
        "aviso": "⛔ NO realizar tarde-noche.",
        "config": "🌫️ SOLO NIR (100%) | 10 Hz",
        "uso": "6 min | 30 cm (Cabeza)"
    },
    "💪 Codos (Analgesia)": {
        "keywords_compatibles": ["Fullbody", "Torso", "Preventivo I", "Descanso"],
        "dias_descanso_min": 0, "alerta_repeticion": True,
        "momento": "TARDE / POST", "orden": 2, 
        "aviso": "Dejar 4h de separación con entreno.",
        "config": "🔴 RED + NIR (100%) | 10 Hz",
        "uso": "10 min | 5-10 cm"
    },
    "🦵 Rodilla (Reparación)": {
        "keywords_compatibles": ["Fullbody", "Preventivo II", "Descanso"],
        "dias_descanso_min": 0, "alerta_repeticion": True,
        "momento": "NOCHE / POST", "orden": 2,
        "aviso": "Idealmente después de ducha.",
        "config": "🌫️ SOLO NIR (100%) | 40 Hz",
        "uso": "15 min | 5 cm (Rodear)"
    },
    "😴 Sueño Profundo": {
        "keywords_compatibles": ["TODOS"], 
        "dias_descanso_min": 0, "momento": "NOCHE", "orden": 3, 
        "aviso": "30 min antes de dormir.",
        "config": "🔴 SOLO RED (20%) | 0 Hz",
        "uso": "20 min | Ambiental (>1m)"
    }
}

# --- FUNCIONES DE DATOS (Anti-Crash) ---
def cargar_csv(filename, cols_esperadas):
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename)
            if set(cols_esperadas).issubset(df.columns): return df
            return pd.DataFrame(columns=cols_esperadas)
        except: return pd.DataFrame(columns=cols_esperadas)
    return pd.DataFrame(columns=cols_esperadas)

def guardar_estado(fecha_dt, tratamiento, valor):
    cols = ["Fecha", "Tratamiento", "Realizado"]
    df = cargar_csv(FILE_HISTORIAL, cols)
    fecha_str = fecha_dt.strftime("%Y-%m-%d")
    
    mask = (df["Fecha"] == fecha_str) & (df["Tratamiento"] == tratamiento)
    if not df[mask].empty:
        df.loc[mask, "Realizado"] = valor
    else:
        nuevo = pd.DataFrame([{"Fecha": fecha_str, "Tratamiento": tratamiento, "Realizado": valor}])
        df = pd.concat([df, nuevo], ignore_index=True)
    df.to_csv(FILE_HISTORIAL, index=False)

def obtener_realizado(fecha_dt, tratamiento):
    cols = ["Fecha", "Tratamiento", "Realizado"]
    df = cargar_csv(FILE_HISTORIAL, cols)
    fecha_str = fecha_dt.strftime("%Y-%m-%d")
    row = df[(df["Fecha"] == fecha_str) & (df["Tratamiento"] == tratamiento)]
    if not row.empty: return bool(row.iloc[0]["Realizado"])
    return False

def guardar_cambio_entreno(fecha_dt, entreno1, entreno2):
    cols = ["Fecha", "Entreno1", "Entreno2"]
    df = cargar_csv(FILE_ENTRENOS, cols)
    fecha_str = fecha_dt.strftime("%Y-%m-%d")
    mask = (df["Fecha"] == fecha_str)
    e2_val = entreno2 if entreno2 != "Ninguno" else None
    
    if not df[mask].empty:
        df.loc[mask, "Entreno1"] = entreno1
        df.loc[mask, "Entreno2"] = e2_val
    else:
        nuevo = pd.DataFrame([{"Fecha": fecha_str, "Entreno1": entreno1, "Entreno2": e2_val}])
        df = pd.concat([df, nuevo], ignore_index=True)
    df.to_csv(FILE_ENTRENOS, index=False)

def obtener_entrenos_reales(fecha_dt):
    fecha_str = fecha_dt.strftime("%Y-%m-%d")
    cols = ["Fecha", "Entreno1", "Entreno2"]
    df = cargar_csv(FILE_ENTRENOS, cols)
    registro = df[df["Fecha"] == fecha_str]
    
    if not registro.empty:
        e1 = registro.iloc[0]["Entreno1"]
        e2 = registro.iloc[0]["Entreno2"]
        if pd.isna(e2): e2 = "Ninguno"
        return e1, e2
    
    rutina_base = {0: "Fullbody I", 1: "Torso I", 2: "Preventivo I",
                   3: "Fullbody II", 4: "Torso + Circuito", 5: "Preventivo II"}
    return rutina_base.get(fecha_dt.weekday(), "Descanso"), "Ninguno"

def filtrar_compatibles(entreno1, entreno2):
    compatibles = []
    lista_entrenos = [entreno1]
    if entreno2 != "Ninguno": lista_entrenos.append(entreno2)
    
    for nombre, datos in DB_TRATAMIENTOS.items():
        if "TODOS" in datos["keywords_compatibles"]:
            compatibles.append(nombre)
        else:
            for kw in datos["keywords_compatibles"]:
                if any(kw in ent for ent in lista_entrenos):
                    compatibles.append(nombre)
                    break
    return sorted(list(set(compatibles)), key=lambda x: DB_TRATAMIENTOS[x]["orden"])

def verificar_historial(tratamiento, fecha_actual):
    cols = ["Fecha", "Tratamiento", "Realizado"]
    df = cargar_csv(FILE_HISTORIAL, cols)
    reglas = DB_TRATAMIENTOS.get(tratamiento, {})
    ayer = fecha_actual - timedelta(days=1)
    ayer_str = ayer.strftime("%Y-%m-%d")
    hecho_ayer = not df[(df["Fecha"] == ayer_str) & (df["Tratamiento"] == tratamiento) & (df["Realizado"] == True)].empty
    
    if reglas.get("dias_descanso_min", 0) > 0 and hecho_ayer:
        return True, "⛔ REQUIERE PAUSA (Hecho ayer)"
    if reglas.get("alerta_repeticion", False) and hecho_ayer:
        return False, "⚠️ PRECAUCIÓN: Hecho ayer"
    return False, ""

# --- INTERFAZ MÓVIL OPTIMIZADA ---
st.title("📱 Mega Panel Mobile")

# 1. FECHA Y ENTRENOS (Compacto)
c1, c2 = st.columns([1, 2])
fecha_sel = c1.date_input("Fecha", datetime.now(), label_visibility="collapsed")
e1_db, e2_db = obtener_entrenos_reales(fecha_sel)

try: idx1 = OPCIONES_ENTRENO.index(e1_db)
except: idx1 = 0
opciones_e2 = ["Ninguno"] + OPCIONES_ENTRENO
try: idx2 = opciones_e2.index(e2_db)
except: idx2 = 0

with st.expander(f"🏋️ Entreno: {e1_db} " + (f"+ {e2_db}" if e2_db != "Ninguno" else ""), expanded=False):
    ne1 = st.selectbox("Entreno 1", OPCIONES_ENTRENO, index=idx1)
    ne2 = st.selectbox("Entreno 2", opciones_e2, index=idx2)
    if ne1 != e1_db or ne2 != e2_db:
        guardar_cambio_entreno(fecha_sel, ne1, ne2)
        st.rerun()

st.divider()

# 2. LISTA DE TRATAMIENTOS (ACORDEÓN)
lista = filtrar_compatibles(ne1, ne2)
momentos = {1: "🌅 MAÑANA", 2: "🌆 TARDE", 3: "🌙 NOCHE"}

# Barra de progreso diaria
hechos_hoy = sum([1 for t in lista if obtener_realizado(fecha_sel, t)])
if len(lista) > 0:
    st.progress(hechos_hoy / len(lista))
    st.caption(f"Progreso: {hechos_hoy}/{len(lista)} completados")

for orden, titulo in momentos.items():
    grupo = [t for t in lista if DB_TRATAMIENTOS[t]["orden"] == orden]
    if grupo:
        st.subheader(titulo)
        for trat in grupo:
            data = DB_TRATAMIENTOS[trat]
            hecho = obtener_realizado(fecha_sel, trat)
            conflicto, msg_hist = verificar_historial(trat, fecha_sel)
            
            # Título del Acordeón con Estado
            icono = "✅" if hecho else "⬜"
            alerta_icon = "⚠️" if msg_hist else ""
            
            # El Expander es la clave para mobile
            with st.expander(f"{icono} {trat} {alerta_icon}"):
                
                # AVISOS DEL HISTORIAL
                if conflicto:
                    st.error(msg_hist)
                elif msg_hist:
                    st.warning(msg_hist)
                
                # FICHA TÉCNICA (Nativa de Streamlit, se ve bien siempre)
                st.info(f"**CONFIG:** {data['config']}")
                st.success(f"**USO:** {data['uso']}")
                st.caption(f"🕒 {data['aviso']}")
                
                # Checkbox de Acción
                # Si hay conflicto grave, deshabilitamos el botón
                deshabilitado = True if conflicto else False
                
                check = st.checkbox("Marcar como REALIZADO", value=hecho, key=f"d_{trat}", disabled=deshabilitado)
                if check != hecho:
                    guardar_estado(fecha_sel, trat, check)
                    st.rerun()

# 3. LINK HISTORIAL
st.divider()
with st.expander("📊 Ver Historial"):
    df = cargar_csv(FILE_HISTORIAL, ["Fecha", "Tratamiento", "Realizado"])
    st.dataframe(df[df["Realizado"]==True].sort_values("Fecha", ascending=False), use_container_width=True)
