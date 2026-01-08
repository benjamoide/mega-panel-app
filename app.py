import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Mega Panel Dual", page_icon="🏋️", layout="centered")

st.markdown("""
<style>
    .big-font { font-size:18px !important; font-weight: bold; }
    .param-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #ff4b4b; }
    .safe-box { background-color: #e8fdf5; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #21c354; }
    .timeline-box { background-color: #eef5ff; padding: 15px; border-radius: 10px; margin: 15px 0; border: 1px solid #d0e1f9; }
    .alert-text { color: #9c4d08; font-weight: bold; background-color: #ffdcb2; padding: 5px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

FILE_HISTORIAL = 'historial_cumplimiento.csv'
FILE_ENTRENOS = 'historial_entrenamientos.csv'

# --- 1. BASE DE DATOS (NOMBRES ACTUALIZADOS) ---
OPCIONES_ENTRENO = [
    "Descanso",           # Domingo
    "Fullbody I",         # Lunes
    "Torso I",            # Martes
    "Preventivo I",       # Miércoles
    "Fullbody II",        # Jueves
    "Torso + Circuito",   # Viernes
    "Preventivo II"       # Sábado
]

DB_TRATAMIENTOS = {
    "🔥 Grasa Abdominal": {
        "keywords_compatibles": ["Fullbody", "Torso", "Circuito"], 
        "dias_descanso_min": 0, 
        "momento": "PRE-ENTRENO",
        "orden": 1, 
        "aviso_tiempo": "⚠️ OBLIGATORIO: Ejercicio físico en los siguientes 60 min.",
        "config": "🔴 RED + NIR (100%) | ⚡ 0 Hz (Continuo)",
        "uso": "⏱️ 15 min | 📏 CONTACTO (Pegado piel)"
    },
    "🦴 Hombro (Activación)": {
        "keywords_compatibles": ["Preventivo I"],
        "dias_descanso_min": 0,
        "momento": "PRE-ENTRENO",
        "orden": 1,
        "aviso_tiempo": "Realizar justo antes de las gomas/movilidad.",
        "config": "🔴 RED + NIR (100%) | ⚡ 0 Hz",
        "uso": "⏱️ 10 min | 📏 5-10 cm"
    },
    "🧠 Cerebro / Foco": {
        "keywords_compatibles": ["Torso I", "Torso + Circuito", "Descanso"],
        "dias_descanso_min": 1, 
        "momento": "MAÑANA",
        "orden": 1,
        "aviso_tiempo": "⛔ NO realizar tarde-noche (insomnio).",
        "config": "🌫️ SOLO NIR (100%) | ⚡ 10 Hz (Alpha)",
        "uso": "⏱️ 6 min | 📏 30 cm (A la cabeza)"
    },
    "💪 Codos (Analgesia)": {
        "keywords_compatibles": ["Fullbody", "Torso", "Preventivo I", "Descanso"],
        "dias_descanso_min": 0, 
        "alerta_repeticion": True,
        "momento": "TARDE / POST-ENTRENO",
        "orden": 2, 
        "aviso_tiempo": "Dejar 4h de separación con el entreno si hay dolor.",
        "config": "🔴 RED + NIR (100%) | ⚡ 10 Hz",
        "uso": "⏱️ 10 min | 📏 5-10 cm"
    },
    "🦵 Rodilla (Reparación)": {
        "keywords_compatibles": ["Fullbody", "Preventivo II", "Descanso"],
        "dias_descanso_min": 0,
        "alerta_repeticion": True,
        "momento": "POST-ENTRENO / NOCHE",
        "orden": 2,
        "aviso_tiempo": "Idealmente después de ducha.",
        "config": "🌫️ SOLO NIR (100%) | ⚡ 40 Hz",
        "uso": "⏱️ 15 min | 📏 5 cm (Rodear rótula)"
    },
    "😴 Sueño Profundo": {
        "keywords_compatibles": ["TODOS"], 
        "dias_descanso_min": 0,
        "momento": "NOCHE (Pre-dormir)",
        "orden": 3, 
        "aviso_tiempo": "30 min antes de dormir.",
        "config": "🔴 SOLO RED (20%) | ⚡ 0 Hz",
        "uso": "⏱️ 20 min | 📏 >1 metro (Ambiental)"
    }
}

# --- GESTIÓN DE DATOS (CON CORRECCIÓN DE ERRORES) ---
def cargar_csv(filename, cols_esperadas):
    """
    Carga el CSV de forma segura. Si el archivo existe pero tiene columnas viejas
    (que causan el KeyError), devuelve un DataFrame vacío nuevo con las columnas correctas
    para evitar el crash.
    """
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename)
            # Verificamos si las columnas que necesitamos existen
            if set(cols_esperadas).issubset(df.columns):
                return df
            else:
                # Si el archivo es viejo y no tiene las columnas nuevas, lo ignoramos temporalmente
                # para que se sobrescriba con el formato correcto.
                return pd.DataFrame(columns=cols_esperadas)
        except:
            return pd.DataFrame(columns=cols_esperadas)
    return pd.DataFrame(columns=cols_esperadas)

def guardar_estado(fecha_dt, tratamiento, campo, valor):
    cols = ["Fecha", "Tratamiento", "Seleccionado", "Realizado"]
    df = cargar_csv(FILE_HISTORIAL, cols)
    
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
    cols = ["Fecha", "Tratamiento", "Seleccionado", "Realizado"]
    df = cargar_csv(FILE_HISTORIAL, cols)
    
    fecha_str = fecha_dt.strftime("%Y-%m-%d")
    row = df[(df["Fecha"] == fecha_str) & (df["Tratamiento"] == tratamiento)]
    if not row.empty:
        return bool(row.iloc[0]["Seleccionado"]), bool(row.iloc[0]["Realizado"])
    return False, False

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
    # Aquí estaba el error antes. Ahora cargar_csv asegura que las columnas existan.
    cols = ["Fecha", "Entreno1", "Entreno2"]
    df = cargar_csv(FILE_ENTRENOS, cols)
    
    registro = df[df["Fecha"] == fecha_str]
    
    if not registro.empty:
        e1 = registro.iloc[0]["Entreno1"]
        e2 = registro.iloc[0]["Entreno2"]
        if pd.isna(e2): e2 = "Ninguno"
        return e1, e2
    
    # Lógica por defecto (Tu Rutina Base)
    rutina_base = {
        0: "Fullbody I", 
        1: "Torso I", 
        2: "Preventivo I",
        3: "Fullbody II", 
        4: "Torso + Circuito", 
        5: "Preventivo II"
    }
    return rutina_base.get(fecha_dt.weekday(), "Descanso"), "Ninguno"

def verificar_conflictos_historial(tratamiento, fecha_actual):
    cols = ["Fecha", "Tratamiento", "Seleccionado", "Realizado"]
    df = cargar_csv(FILE_HISTORIAL, cols)
    
    reglas = DB_TRATAMIENTOS.get(tratamiento, {})
    ayer = fecha_actual - timedelta(days=1)
    ayer_str = ayer.strftime("%Y-%m-%d")
    
    hecho_ayer = not df[(df["Fecha"] == ayer_str) & (df["Tratamiento"] == tratamiento) & (df["Realizado"] == True)].empty
    
    if reglas.get("dias_descanso_min", 0) > 0 and hecho_ayer:
        return True, f"⛔ ALTO: Requiere descanso. Lo hiciste ayer ({ayer_str})."
    if reglas.get("alerta_repeticion", False) and hecho_ayer:
        return False, f"⚠️ PRECAUCIÓN: Realizado ayer. Asegura 24h de descanso."
    return False, ""

def filtrar_tratamientos_compatibles(entreno1, entreno2):
    compatibles = []
    lista_entrenos = [entreno1]
    if entreno2 != "Ninguno":
        lista_entrenos.append(entreno2)
        
    for nombre, datos in DB_TRATAMIENTOS.items():
        es_compatible = False
        if "TODOS" in datos["keywords_compatibles"]:
            es_compatible = True
        else:
            for kw in datos["keywords_compatibles"]:
                for ent in lista_entrenos:
                    if kw in ent: 
                        es_compatible = True
                        break
        
        if es_compatible:
            compatibles.append(nombre)
            
    compatibles = list(set(compatibles))
    compatibles.sort(key=lambda x: DB_TRATAMIENTOS[x]["orden"])
    return compatibles

def generar_cronologia(seleccionados):
    if len(seleccionados) < 2: return None
    sel_ordenados = sorted(seleccionados, key=lambda x: DB_TRATAMIENTOS[x]["orden"])
    timeline = []
    for i in range(len(sel_ordenados) - 1):
        actual, siguiente = sel_ordenados[i], sel_ordenados[i+1]
        ord_a, ord_s = DB_TRATAMIENTOS[actual]["orden"], DB_TRATAMIENTOS[siguiente]["orden"]
        
        tiempo_msg = ""
        if ord_a == ord_s: tiempo_msg = "⏱️ **Seguido:** Deja 10 min enfriar."
        elif ord_a == 1 and ord_s == 2: tiempo_msg = "⏱️ **Espera:** Entreno + Ducha (~2h)."
        elif ord_a == 2 and ord_s == 3: tiempo_msg = "⏱️ **Espera:** Hasta la noche."
        elif ord_a == 1 and ord_s == 3: tiempo_msg = "⏱️ **Espera:** Todo el día."
        
        timeline.append((actual, tiempo_msg, siguiente))
    return timeline

# --- INTERFAZ ---
st.title("🛡️ Mega Panel Dual")

# 1. SELECTOR DE FECHA Y ENTRENOS
col_d, col_e1, col_e2 = st.columns([1, 1.5, 1.5])
fecha_sel = col_d.date_input("Fecha", datetime.now())

e1_db, e2_db = obtener_entrenos_reales(fecha_sel)

# Manejo seguro de índices
try: idx1 = OPCIONES_ENTRENO.index(e1_db)
except: idx1 = 0
opciones_e2 = ["Ninguno"] + OPCIONES_ENTRENO
try: idx2 = opciones_e2.index(e2_db)
except: idx2 = 0

nuevo_e1 = col_e1.selectbox("Entreno 1:", OPCIONES_ENTRENO, index=idx1)
nuevo_e2 = col_e2.selectbox("Entreno 2 (Opcional):", opciones_e2, index=idx2)

if nuevo_e1 != e1_db or nuevo_e2 != e2_db:
    guardar_cambio_entreno(fecha_sel, nuevo_e1, nuevo_e2)
    st.rerun()

st.divider()

# 2. SELECCIÓN INTELIGENTE (COMBINADA)
st.subheader("1️⃣ Selección Inteligente")
st.caption(f"Mostrando terapias para: **{nuevo_e1}**" + (f" + **{nuevo_e2}**" if nuevo_e2 != "Ninguno" else ""))

lista_posible = filtrar_tratamientos_compatibles(nuevo_e1, nuevo_e2)
seleccionados = []
momentos = {1: "🌅 MAÑANA", 2: "🌆 TARDE", 3: "🌙 NOCHE"}

for orden, titulo in momentos.items():
    grupo = [t for t in lista_posible if DB_TRATAMIENTOS[t]["orden"] == orden]
    if grupo:
        st.markdown(f"**{titulo}**")
        for trat in grupo:
            sel, _ = obtener_estado(fecha_sel, trat)
            conflicto, mensaje = verificar_conflictos_historial(trat, fecha_sel)
            
            if conflicto: st.error(mensaje)
            elif mensaje: st.warning(mensaje)
            
            if st.checkbox(trat, value=sel, key=f"chk_{trat}_{fecha_sel}"):
                if not sel: guardar_estado(fecha_sel, trat, "Seleccionado", True)
                seleccionados.append(trat)
            else:
                if sel: guardar_estado(fecha_sel, trat, "Seleccionado", False)

st.divider()

# 3. CRONOLOGÍA
if len(seleccionados) > 1:
    st.markdown("### ⏳ Cronología Sugerida")
    timeline_data = generar_cronologia(seleccionados)
    st.markdown('<div class="timeline-box">', unsafe_allow_html=True)
    for i, (t1, tiempo, t2) in enumerate(timeline_data):
        st.markdown(f"**{i+1}. {t1}**")
        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;⬇️&nbsp;&nbsp;*{tiempo}*")
        if i == len(timeline_data) - 1:
            st.markdown(f"**{i+2}. {t2}**")
    st.markdown('</div>', unsafe_allow_html=True)

# 4. EJECUCIÓN TÉCNICA
st.subheader("2️⃣ Ejecución Técnica")

if not seleccionados:
    st.info("👆 Selecciona arriba para comenzar.")
else:
    for trat in seleccionados:
        data = DB_TRATAMIENTOS[trat]
        _, hecho = obtener_estado(fecha_sel, trat)
        conflicto, mensaje = verificar_conflictos_historial(trat, fecha_sel)
        
        clase_caja = "param-box" if conflicto or mensaje else "safe-box"
        icono = "✅ HECHO" if hecho else "⏳ PENDIENTE"
        
        with st.container():
            st.markdown(f"### {trat} - {icono}")
            
            st.markdown(f"""
            <div class="{clase_caja}">
                <b>⚙️ CONFIG:</b> {data['config']}<br>
                <b>📏 USO:</b> {data['uso']}<br>
                <hr style="margin:5px 0">
                <i>🕒 {data['aviso_tiempo']}</i>
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

# LINK HISTORIAL
with st.expander("Ver Historial Completo"):
    # Carga segura para historial también
    df = cargar_csv(FILE_HISTORIAL, ["Fecha", "Tratamiento", "Realizado"])
    st.dataframe(df[df["Realizado"]==True].sort_values("Fecha", ascending=False))
