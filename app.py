import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Mega Panel Plan", page_icon="🔴", layout="centered")

# --- GESTIÓN DE DATOS (CSV LOCAL) ---
FILE_HISTORIAL = 'historial_cumplimiento.csv'

def cargar_historial():
    if os.path.exists(FILE_HISTORIAL):
        try:
            return pd.read_csv(FILE_HISTORIAL)
        except:
            return pd.DataFrame(columns=["Fecha", "Tratamiento", "Realizado"])
    else:
        return pd.DataFrame(columns=["Fecha", "Tratamiento", "Realizado"])

def guardar_accion(fecha_dt, nombre_tratamiento, realizado):
    df = cargar_historial()
    fecha_str = fecha_dt.strftime("%Y-%m-%d")
    
    # Actualizar o Crear registro
    mask = (df["Fecha"] == fecha_str) & (df["Tratamiento"] == nombre_tratamiento)
    if not df[mask].empty:
        df.loc[mask, "Realizado"] = realizado
    else:
        nuevo = pd.DataFrame([{"Fecha": fecha_str, "Tratamiento": nombre_tratamiento, "Realizado": realizado}])
        df = pd.concat([df, nuevo], ignore_index=True)
    
    df.to_csv(FILE_HISTORIAL, index=False)

# --- LÓGICA DE TRATAMIENTOS ---
def obtener_tratamientos_del_dia(fecha_dt):
    dia_semana = fecha_dt.weekday() # 0=Lunes
    tratamientos = []
    
    # Rutina Base
    rutina = {
        0: "Empuje (Fuerza)", 1: "Tracción (Fuerza)", 2: "Preventivo I (Hombro)",
        3: "Pierna (Fuerza)", 4: "Torso (Accesorios)", 5: "Preventivo II (Rodilla)",
        6: "Descanso Total"
    }
    entreno_hoy = rutina.get(dia_semana, "Descanso")

    # Reglas de Mega Panel
    if dia_semana in [0, 1, 3, 4]:
        tratamientos.append({"Nombre": "🔥 Grasa", "Desc": "15' Abdomen (0Hz, 100%) - Pre Entreno"})
    if dia_semana in [0, 2, 4]: 
        tratamientos.append({"Nombre": "💪 Codos", "Desc": "10' (10Hz) - Tarde"})
    if dia_semana in [3, 5]:
        tratamientos.append({"Nombre": "🦵 Rodilla", "Desc": "15' (40Hz) - Post Entreno"})
    if dia_semana == 2:
        tratamientos.append({"Nombre": "🦴 Hombro", "Desc": "10' (0Hz) - Pre Gomas"})
    if dia_semana in [1, 4, 6]:
        tratamientos.append({"Nombre": "🧠 Cerebro", "Desc": "6' NIR (10Hz) - Mañana"})
    
    tratamientos.append({"Nombre": "😴 Sueño", "Desc": "Ambiente Rojo - Noche"})

    return entreno_hoy, tratamientos

# --- VISUALIZACIÓN CALENDARIO ---
def calcular_estado_dia(fecha_dt, historial):
    fecha_str = fecha_dt.strftime("%Y-%m-%d")
    _, tareas_teoricas = obtener_tratamientos_del_dia(fecha_dt)
    if not tareas_teoricas: return "⚪"
    
    tareas_hechas = historial[(historial["Fecha"] == fecha_str) & (historial["Realizado"] == True)]
    
    if len(tareas_hechas) == len(tareas_teoricas): return "🟢"
    elif len(tareas_hechas) > 0: return "🟡"
    elif fecha_dt < datetime.now().date(): return "🔴"
    else: return "⚪"

def mostrar_calendario_mensual():
    st.subheader(f"📅 Calendario - {datetime.now().strftime('%B %Y')}")
    hoy = datetime.now()
    cal = calendar.monthcalendar(hoy.year, hoy.month)
    historial = cargar_historial()
    
    cols = st.columns(7)
    dias = ["L", "M", "X", "J", "V", "S", "D"]
    for i, d in enumerate(dias): cols[i].markdown(f"**{d}**")
        
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day != 0:
                fecha_cal = date(hoy.year, hoy.month, day)
                estado = calcular_estado_dia(fecha_cal, historial)
                cols[i].markdown(f"**{day}**\n{estado}")

# --- INTERFAZ APP ---
st.title("🔴 Mega Panel App")
tab1, tab2 = st.tabs(["📝 Hoy", "🗓️ Mes"])

with tab1:
    fecha_sel = st.date_input("Fecha", datetime.now())
    entreno, lista = obtener_tratamientos_del_dia(fecha_sel)
    st.info(f"🏋️ **{entreno}**")
    
    historial = cargar_historial()
    fecha_str = fecha_sel.strftime("%Y-%m-%d")
    
    for t in lista:
        key = f"{fecha_str}_{t['Nombre']}"
        estado = False
        row = historial[(historial["Fecha"] == fecha_str) & (historial["Tratamiento"] == t['Nombre'])]
        if not row.empty: estado = bool(row.iloc[0]["Realizado"])
        
        if st.checkbox(f"**{t['Nombre']}**: {t['Desc']}", value=estado, key=key):
            if not estado: guardar_accion(fecha_sel, t['Nombre'], True)
        else:
            if estado: guardar_accion(fecha_sel, t['Nombre'], False)

with tab2:
    mostrar_calendario_mensual()
    st.caption("🟢 Completo | 🟡 Parcial | 🔴 Nada")
