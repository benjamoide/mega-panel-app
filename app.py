import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Mega Panel Guardian", page_icon="🛡️", layout="centered")

st.markdown("""
<style>
    .big-font { font-size:18px !important; font-weight: bold; }
    .param-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #ff4b4b; }
    .safe-box { background-color: #e8fdf5; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #21c354; }
    .alert-text { color: #9c4d08; font-weight: bold; background-color: #ffdcb2; padding: 5px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

FILE_HISTORIAL = 'historial_cumplimiento.csv'
FILE_ENTRENOS = 'historial_entrenamientos.csv'

# --- 1. CEREBRO DE REGLAS Y DESCANSOS ---
DB_TRATAMIENTOS = {
    "🔥 Grasa Abdominal": {
        "compatible_con": ["Empuje", "Tracción", "Pierna", "Torso", "Cardio"], 
        "dias_descanso_min": 0, # Se puede hacer a diario
        "momento": "PRE-ENTRENO",
        "orden": 1,
        "aviso_tiempo": "⚠️ OBLIGATORIO: Ejercicio físico en los siguientes 60 min.",
        "config": "🔴 RED + NIR (100%) | ⚡ 0 Hz (Continuo)",
        "uso": "⏱️ 15 min | 📏 CONTACTO (Pegado piel)"
    },
    "🦴 Hombro (Activación)": {
        "compatible_con": ["Preventivo I (Hombro)"],
        "dias_descanso_min": 0,
        "momento": "PRE-ENTRENO",
        "orden": 1,
        "aviso_tiempo": "Realizar justo antes de las gomas/movilidad.",
        "config": "🔴 RED + NIR (100%) | ⚡ 0 Hz",
        "uso": "⏱️ 10 min | 📏 5-10 cm"
    },
    "🧠 Cerebro / Foco": {
        "compatible_con": ["Tracción", "Torso", "Descanso Total"],
        "dias_descanso_min": 1, # Días alternos recomendados
        "momento": "MAÑANA",
        "orden": 1,
        "aviso_tiempo": "⛔ NO realizar tarde-noche (insomnio).",
        "config": "🌫️ SOLO NIR (100%) | ⚡ 10 Hz (Alpha)",
        "uso": "⏱️ 6 min | 📏 30 cm (A la cabeza)"
    },
    "💪 Codos (Analgesia)": {
        "compatible_con": ["Empuje", "Torso", "Preventivo I (Hombro)", "Descanso Total"],
        "dias_descanso_min": 0, # Se permite diario, pero ojo repetición
        "alerta_repeticion": True, # Avisar si se hizo ayer
        "momento": "TARDE / POST-ENTRENO",
        "orden": 2,
        "aviso_tiempo": "Dejar 4h de separación con el entreno.",
        "config": "🔴 RED + NIR (100%) | ⚡ 10 Hz",
        "uso": "⏱️ 10 min | 📏 5-10 cm"
    },
    "🦵 Rodilla (Reparación)": {
        "compatible_con": ["Pierna", "Preventivo II (Rodilla)", "Descanso Total"],
        "dias_descanso_min": 0,
        "alerta_repeticion": True,
        "momento": "POST-ENTRENO / NOCHE",
        "orden": 2,
        "aviso_tiempo": "Idealmente después de ducha.",
        "config": "🌫️ SOLO NIR (100%) | ⚡ 40 Hz",
        "uso": "⏱️ 15 min | 📏 5 cm (Rodear rótula)"
    },
    "😴 Sueño Profundo": {
        "compatible_con": ["TODOS"], 
        "dias_descanso_min": 0,
        "momento": "NOCHE (Pre-dormir)",
        "orden": 3,
        "aviso_tiempo": "30 min antes de dormir.",
        "config": "🔴 SOLO RED (20%) | ⚡ 0 Hz",
        "uso": "⏱️ 20 min | 📏 >1 metro (Ambiental)"
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
    df = cargar_csv(FILE_HISTORIAL, ["Fecha", "Tratamiento", "Seleccionado", "Realizado"])
    fecha_str = fecha_dt.strftime("%Y-%m-%d")
    mask = (df["Fecha"] == fecha_str) & (df["Tratamiento"] == tratamiento)
    if not df[mask].empty:
        df.loc[mask, campo] = valor
    else:
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
    return False, False

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
    
    rutina_base = {0: "Empuje (Fuerza)", 1: "Tracción (Fuerza)", 2: "Preventivo I (Hombro)",
                   3: "Pierna (Fuerza)", 4: "Torso (Accesorios)", 5: "Preventivo II (Rodilla)"}
    return rutina_base.get(fecha_dt.weekday(), "Descanso Total")

# --- LÓGICA DE VIGILANCIA HISTÓRICA ---
def verificar_conflictos_historial(tratamiento, fecha_actual):
    """
    Revisa si el tratamiento se hizo ayer o antes y si viola la regla de descanso.
    Retorna: (bool_conflicto, mensaje_alerta)
    """
    df = cargar_csv(FILE_HISTORIAL, ["Fecha", "Tratamiento", "Seleccionado", "Realizado"])
    reglas = DB_TRATAMIENTOS.get(tratamiento, {})
    
    # 1. Verificar Día Anterior (Ayer)
    ayer = fecha_actual - timedelta(days=1)
    ayer_str = ayer.strftime("%Y-%m-%d")
    
    hecho_ayer = not df[(df["Fecha"] == ayer_str) & (df["Tratamiento"] == tratamiento) & (df["Realizado"] == True)].empty
    
    # REGLA A: Días de descanso obligatorio (ej. Cerebro)
    dias_min = reglas.get("dias_descanso_min", 0)
    if dias_min > 0 and hecho_ayer:
        return True, f"⛔ ALTO: Este tratamiento requiere descanso. Lo hiciste ayer ({ayer_str}). Hoy toca pausa."
        
    # REGLA B: Alerta de repetición (Precaución para lesiones)
    alerta_rep = reglas.get("alerta_repeticion", False)
    if alerta_rep and hecho_ayer:
        return False, f"⚠️ PRECAUCIÓN: Realizado ayer. Asegura 24h de descanso real o reduce intensidad."
        
    return False, ""

def filtrar_tratamientos_compatibles(entreno_hoy):
    compatibles = []
    for nombre, datos in DB_TRATAMIENTOS.items():
        if "TODOS" in datos["compatible_con"] or any(e in entreno_hoy for e in datos["compatible_con"]):
            compatibles.append(nombre)
    compatibles.sort(key=lambda x: DB_TRATAMIENTOS[x]["orden"])
    return compatibles

# --- INTERFAZ ---
st.title("🛡️ Panel Guardian")

# 1. FECHA
col_d, col_e = st.columns([1, 2])
fecha_sel = col_d.date_input("Fecha", datetime.now())
entreno_db = obtener_entreno_real(fecha_sel)
idx = OPCIONES_ENTRENO.index(entreno_db) if entreno_db in OPCIONES_ENTRENO else 6
nuevo_entreno = col_e.selectbox("Entreno hoy:", OPCIONES_ENTRENO, index=idx)

if nuevo_entreno != entreno_db:
    guardar_cambio_entreno(fecha_sel, nuevo_entreno)
    st.rerun()

st.divider()

# 2. SELECCIÓN CON ESCÁNER DE HISTORIAL
st.subheader("1️⃣ Selección Inteligente")

lista_posible = filtrar_tratamientos_compatibles(nuevo_entreno)
seleccionados = []
momentos = {1: "🌅 MAÑANA", 2: "🌆 TARDE", 3: "🌙 NOCHE"}

for orden, titulo in momentos.items():
    grupo = [t for t in lista_posible if DB_TRATAMIENTOS[t]["orden"] == orden]
    if grupo:
        st.markdown(f"**{titulo}**")
        for trat in grupo:
            sel, _ = obtener_estado(fecha_sel, trat)
            
            # --- VIGILANCIA AQUÍ ---
            conflicto, mensaje = verificar_conflictos_historial(trat, fecha_sel)
            label_text = trat
            
            # Mostrar alerta visual junto al checkbox
            if conflicto:
                st.error(mensaje) # Muestra caja roja si está prohibido
            elif mensaje:
                st.warning(mensaje) # Muestra caja amarilla si es precaución
            
            # Si hay conflicto grave, deshabilitar o avisar fuerte
            disabled_chk = False # Podríamos poner True si queremos bloquear totalmente
            
            if st.checkbox(label_text, value=sel, key=f"chk_{trat}_{fecha_sel}", disabled=disabled_chk):
                if not sel: guardar_estado(fecha_sel, trat, "Seleccionado", True)
                seleccionados.append(trat)
            else:
                if sel: guardar_estado(fecha_sel, trat, "Seleccionado", False)
        st.write("")

st.divider()

# 3. EJECUCIÓN
st.subheader("2️⃣ Ejecución Técnica")

if not seleccionados:
    st.info("👆 Selecciona arriba (si el historial lo permite).")
else:
    for trat in seleccionados:
        data = DB_TRATAMIENTOS[trat]
        _, hecho = obtener_estado(fecha_sel, trat)
        
        # Volver a chequear historial para mostrar aviso dentro de la tarjeta también
        conflicto, mensaje = verificar_conflictos_historial(trat, fecha_sel)
        
        clase_caja = "param-box" if conflicto or mensaje else "safe-box"
        icono_estado = "✅ HECHO" if hecho else "⏳ PENDIENTE"
        
        with st.container():
            st.markdown(f"### {trat}")
            st.caption(f"Estado: **{icono_estado}**")
            
            if mensaje:
                st.markdown(f'<div class="alert-text">{mensaje}</div>', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="{clase_caja}">
                <span style="font-size:16px">⚙️ <b>CONFIG:</b> {data['config']}</span><br>
                <span style="font-size:16px">📏 <b>USO:</b> {data['uso']}</span><br>
                <br><i>🕒 {data['aviso_tiempo']}</i>
            </div>
            """, unsafe_allow_html=True)
            
            if st.checkbox(f"Finalizar {trat}", value=hecho, key=f"done_{trat}"):
                if not hecho: 
                    guardar_estado(fecha_sel, trat, "Realizado", True)
                    st.rerun()
            else:
                if hecho: 
                    guardar_estado(fecha_sel, trat, "Realizado", False)
                    st.rerun()
            st.divider()

# Link Historial
with st.expander("Ver Historial Completo"):
    df = cargar_csv(FILE_HISTORIAL, ["Fecha", "Tratamiento", "Realizado"])
    st.dataframe(df[df["Realizado"]==True].sort_values("Fecha", ascending=False))
