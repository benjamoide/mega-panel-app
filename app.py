import streamlit as st
import datetime
from datetime import timedelta
import json
import os
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Mega Panel AI",
    page_icon="🧬",
    layout="centered"
)

# --- ARCHIVO DE DATOS ---
ARCHIVO_DATOS = 'historial_mega_panel_pro.json'

# ==============================================================================
# 1. CONSTANTES, RUTINAS Y CONFIGURACIÓN
# ==============================================================================

# Rutina de Fuerza Base
RUTINA_SEMANAL = {
    "0": ["FULLBODY I"],           # Lunes
    "1": ["TORSO I"],              # Martes
    "2": ["FULLBODY II"],          # Miércoles
    "3": ["TORSO II / CIRCUITO"],  # Jueves
    "4": ["PREVENTIVO I"],         # Viernes
    "5": ["PREVENTIVO II"],        # Sábado
    "6": ["Descanso Total"]        # Domingo
}

# Cardio por Defecto (Día: Actividad)
CARDIO_DEFAULTS_BY_DAY = {
    "0": {"actividad": "Remo Ergómetro", "tiempo": 8, "ritmo": "Intenso"},
    "2": {"actividad": "Cinta Inclinada", "tiempo": 20, "velocidad": 6.5, "inclinacion": 4},
    "5": {"actividad": "Cinta Inclinada", "tiempo": 15, "velocidad": 6.5, "inclinacion": 4}
}

# Parámetros Base Cardio
GENERIC_CARDIO_PARAMS = {
    "Remo Ergómetro": {"tiempo": 8, "ritmo": "Intenso"},
    "Cinta Inclinada": {"tiempo": 15, "velocidad": 6.5, "inclinacion": 4},
    "Elíptica": {"tiempo": 15, "velocidad": 6.5},
    "Andar": {"tiempo": 15},
    "Andar (Pasos)": {"pasos": 10000},
    "Descanso Cardio": {}
}

# Sistema de Tags (Fuerza + Cardio) para calcular compatibilidad
TAGS_ACTIVIDADES = {
    # Fuerza
    "FULLBODY I": ["Upper", "Lower", "Active"], 
    "TORSO I": ["Upper", "Active"],
    "PREVENTIVO I": ["Active"], 
    "FULLBODY II": ["Upper", "Lower", "Active"],
    "TORSO + CIRCUITO": ["Upper", "Active", "Cardio"], 
    "PREVENTIVO II": ["Active"],
    "Descanso Total": [],
    
    # Cardio
    "Remo Ergómetro": ["Active", "Cardio", "Upper", "Lower"],
    "Cinta Inclinada": ["Active", "Cardio", "Lower"],
    "Elíptica": ["Active", "Cardio", "Lower"],
    "Andar": ["Active", "Lower"],
    "Andar (Pasos)": ["Active", "Lower"],
    "Descanso Cardio": []
}

TAGS_BACKUP = TAGS_ACTIVIDADES
RUTINA_BACKUP = RUTINA_SEMANAL

# ==============================================================================
# 2. CLASE TRATAMIENTO
# ==============================================================================
class Tratamiento:
    def __init__(self, id_t, nombre, zona, ondas_txt, config_energia, herzios, distancia, duracion, max_diario, max_semanal, tipo, tags_entreno, default_visual_group, momento_ideal_txt, momentos_prohibidos, tips_antes, tips_despues, incompatible_with=None, fases_config=None):
        self.id = id_t
        self.nombre = nombre
        self.zona = zona
        self.ondas_txt = ondas_txt          
        self.config_energia = config_energia 
        self.herzios = herzios              
        self.distancia = distancia
        self.duracion = duracion
        self.max_diario = max_diario
        self.max_semanal = max_semanal
        self.tipo = tipo
        self.tags_entreno = tags_entreno 
        self.default_visual_group = default_visual_group 
        self.momento_ideal_txt = momento_ideal_txt
        self.momentos_prohibidos = momentos_prohibidos 
        self.tips_antes = tips_antes
        self.tips_despues = tips_despues
        self.incompatible_with = incompatible_with if incompatible_with else []
        self.incompatibilidades = "" 
        self.fases_config = fases_config if fases_config else []

    def set_incompatibilidades(self, texto):
        self.incompatibilidades = texto
        return self

# ==============================================================================
# 3. CATÁLOGO CIENTÍFICO COMPLETO
# ==============================================================================
def obtener_catalogo():
    fases_lesion = [
        {"nombre": "🔥 Fase 1: Inflamatoria/Aguda", "dias_fin": 7, "min_sesiones": 5},
        {"nombre": "🛠️ Fase 2: Proliferación", "dias_fin": 21, "min_sesiones": 10},
        {"nombre": "🧱 Fase 3: Remodelación", "dias_fin": 60, "min_sesiones": 20}
    ]
    
    catalogo = [
        # GRASA (CW)
        Tratamiento("fat_glutes", "Glúteos (Grasa)", "Glúteos/Caderas", "660nm + 850nm", "660nm: 100% | 850nm: 100%", "CW (0Hz)", "10-15 cm", 10, 1, 7, "GRASA", ['Active', 'Lower'], "PRE", "Ideal: Antes de Entrenar Pierna", ["🌙 Noche", "🚿 Post-Entreno / Mañana"], ["💧 Beber agua.", "🧴 Piel limpia."], ["🏃‍♂️ ACTIVIDAD YA.", "🚿 Ducha."], ["fat_front", "fat_d", "fat_i"]),
        Tratamiento("fat_front", "Abdomen Frontal (Grasa)", "Abdomen", "660nm + 850nm", "660nm: 100% | 850nm: 100%", "CW (0Hz)", "10-15 cm", 10, 1, 7, "GRASA", ['Active'], "PRE", "Ideal: Antes de Entrenar", ["🌙 Noche", "🚿 Post-Entreno / Mañana"], ["💧 Beber agua."], ["🏃‍♂️ ENTRENA YA."], ["fat_glutes"]),
        Tratamiento("fat_d", "Flanco Derecho (Grasa)", "Abdomen", "660nm + 850nm", "660nm: 100% | 850nm: 100%", "CW (0Hz)", "10-15 cm", 10, 1, 7, "GRASA", ['Active'], "PRE", "Ideal: Antes de Entrenar", ["🌙 Noche", "🚿 Post-Entreno / Mañana"], ["💧 Beber agua."], ["🏃‍♂️ ENTRENA YA."], ["fat_glutes"]),
        Tratamiento("fat_i", "Flanco Izquierdo (Grasa)", "Abdomen", "660nm + 850nm", "660nm: 100% | 850nm: 100%", "CW (0Hz)", "10-15 cm", 10, 1, 7, "GRASA", ['Active'], "PRE", "Ideal: Antes de Entrenar", ["🌙 Noche", "🚿 Post-Entreno / Mañana"], ["💧 Beber agua."], ["🏃‍♂️ ENTRENA YA."], ["fat_glutes"]),
        
        # ESTÉTICA (CW)
        Tratamiento("face_rejuv", "Rejuvenecimiento Facial", "Cara", "630nm/660nm (+850nm Opcional)", "630nm: 100% | 850nm: 50% (Opc)", "CW (0Hz)", "30-50 cm", 10, 1, 5, "PERMANENTE", ['All'], "FLEX", "Cualquier hora (Piel Limpia)", ["🏋️ Entrenamiento (Pre)"], ["🧼 DOBLE LIMPIEZA.", "🕶️ GAFAS."], ["🧴 Serum.", "❌ No sol."], []),
        
        # LESIONES (50Hz Analgesia)
        Tratamiento("foot_d", "Pie Derecho (Plantar/Lateral)", "Pie", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "50Hz (Dolor)", "10-15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible", [], ["🦶 Piel limpia."], ["🎾 Rodar pelota."], [], fases_lesion),
        Tratamiento("foot_i", "Pie Izquierdo (Plantar/Lateral)", "Pie", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "50Hz (Dolor)", "10-15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible", [], ["🦶 Piel limpia."], ["🎾 Rodar pelota."], [], fases_lesion),
        Tratamiento("epi_d", "Epicondilitis Dcha (Codo)", "Codo Lateral", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "50Hz (Dolor)", "10-15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible", [], ["🧴 Piel limpia."], ["🛑 NO pinza."], ["codo_d"], fases_lesion),
        Tratamiento("epi_i", "Epicondilitis Izq (Codo)", "Codo Lateral", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "50Hz (Dolor)", "10-15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible", [], ["🧴 Piel limpia."], ["🛑 NO pinza."], ["codo_i"], fases_lesion),
        Tratamiento("forearm_inj_d", "Tendinitis Antebrazo D", "Muñeca/Vientre", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "50Hz (Dolor)", "10-15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible", [], ["⌚ Quitar reloj."], ["👋 Movilidad suave."], ["arm_d"], fases_lesion),
        Tratamiento("forearm_inj_i", "Tendinitis Antebrazo I", "Muñeca/Vientre", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "50Hz (Dolor)", "10-15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible", [], ["⌚ Quitar reloj."], ["👋 Movilidad suave."], ["arm_i"], fases_lesion),
        Tratamiento("shoulder_d", "Hombro Dcho (Lesión)", "Deltoides", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "10Hz - 40Hz", "15-20 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible", [], ["👕 Sin ropa."], ["🔄 Pendulares."], [], fases_lesion),
        Tratamiento("shoulder_i", "Hombro Izq (Lesión)", "Deltoides", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "10Hz - 40Hz", "15-20 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible", [], ["👕 Sin ropa."], ["🔄 Pendulares."], [], fases_lesion),
        Tratamiento("rodilla_d", "Rodilla Dcha (Lesión)", "Rodilla", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "10Hz (Hueso)", "15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible", [], ["❄️ NO hielo antes."], ["🦶 Movilidad."], [], fases_lesion),
        Tratamiento("rodilla_i", "Rodilla Izq (Lesión)", "Rodilla", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "10Hz (Hueso)", "15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible", [], ["❄️ NO hielo antes."], ["🦶 Movilidad."], [], fases_lesion),
        Tratamiento("codo_d", "Codo Dcho (Genérico)", "Codo", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "10Hz", "15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible", [], ["🧴 Piel limpia."], ["🔄 Estiramiento."], ["epi_d"], fases_lesion),
        Tratamiento("codo_i", "Codo Izq (Genérico)", "Codo", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "10Hz", "15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible", [], ["🧴 Piel limpia."], ["🔄 Estiramiento."], ["epi_i"], fases_lesion),
        
        # MUSCULO (10Hz Alfa)
        Tratamiento("arm_d", "Antebrazo D (Recuperación)", "Antebrazo", "660nm + 850nm", "660nm: 100% | 850nm: 100%", "10Hz (Recuperación)", "15 cm", 10, 1, 6, "MUSCULAR", ['Upper'], "POST", "Ideal: Post-Entreno", ["🏋️ Entrenamiento (Pre)"], ["🚿 Quitar sudor."], ["🥩 Proteína."], ["forearm_inj_d"]),
        Tratamiento("arm_i", "Antebrazo I (Recuperación)", "Antebrazo", "660nm + 850nm", "660nm: 100% | 850nm: 100%", "10Hz (Recuperación)", "15 cm", 10, 1, 6, "MUSCULAR", ['Upper'], "POST", "Ideal: Post-Entreno", ["🏋️ Entrenamiento (Pre)"], ["🚿 Quitar sudor."], ["🥩 Proteína."], ["forearm_inj_i"]),
        
        # PERMANENTES
        Tratamiento("testo", "Boost Testosterona", "Testículos", "660nm + 850nm", "660nm: 100% | 850nm: 100%", "CW (0Hz)", "15 cm", 5, 1, 7, "PERMANENTE", ['All'], "MORNING", "Mañana", ["🌙 Noche", "⛅ Tarde", "🚿 Post-Entreno / Mañana"], ["🚿 Piel limpia.", "❄️ Zona fresca."], ["🚿 Ducha fría."], []),
        Tratamiento("sleep", "Sueño y Ritmo", "Ambiente", "Solo 630nm/660nm", "630nm: 20% | 850nm: 0%", "CW (0Hz)", ">50 cm", 15, 1, 7, "PERMANENTE", ['All'], "NIGHT", "Noche", ["🌞 Mañana", "⛅ Tarde", "🏋️ Entrenamiento (Pre)", "🚿 Post-Entreno / Mañana"], ["📵 Apagar pantallas."], ["🛌 A DORMIR."], ["brain"]),
        Tratamiento("brain", "Salud Cerebral", "Cabeza", "Solo 810nm/850nm", "660nm: 0% | 850nm: 100%", "40Hz (Gamma)", "30 cm", 10, 1, 5, "PERMANENTE", ['All'], "FLEX", "Mañana/Tarde", ["🌙 Noche"], ["🕶️ GAFAS."], ["🧠 Tarea cognitiva."], ["sleep"])
    ]
    return catalogo

# ==============================================================================
# 4. GESTIÓN DE DATOS Y PERSISTENCIA
# ==============================================================================
def cargar_datos_completos():
    default_db = {
        "configuracion_rutina": {"semana": RUTINA_SEMANAL, "tags": TAGS_ACTIVIDADES},
        "usuario_rutina": {"historial": {}, "meta_diaria": {}, "meta_cardio": {}, "ciclos_activos": {}, "descartados": {}, "planificados_adhoc": {}}, 
        "usuario_libre": {"historial": {}, "meta_diaria": {}, "meta_cardio": {}, "ciclos_activos": {}, "descartados": {}, "planificados_adhoc": {}}
    }
    if not os.path.exists(ARCHIVO_DATOS): return default_db
    try:
        with open(ARCHIVO_DATOS, 'r') as f:
            datos = json.load(f)
            if "configuracion_rutina" not in datos: datos["configuracion_rutina"] = default_db["configuracion_rutina"]
            for user in ["usuario_rutina", "usuario_libre"]:
                if user not in datos: datos[user] = default_db[user]
                if "meta_cardio" not in datos[user]: datos[user]["meta_cardio"] = {}
                if "planificados_adhoc" not in datos[user]: datos[user]["planificados_adhoc"] = {}
            return datos
    except: return default_db

def guardar_datos_completos(datos):
    with open(ARCHIVO_DATOS, 'w') as f:
        json.dump(datos, f, indent=4)

def obtener_rutina_completa(fecha_obj, db_global, db_usuario):
    fecha_iso = fecha_obj.isoformat()
    dia_semana_str = str(fecha_obj.weekday())
    
    rutina_manual = db_usuario.get("meta_diaria", {}).get(fecha_iso, None)
    config_semana = db_global.get("configuracion_rutina", {}).get("semana", RUTINA_SEMANAL)
    config_tags = db_global.get("configuracion_rutina", {}).get("tags", TAGS_ACTIVIDADES)
    rutina_fuerza = rutina_manual if rutina_manual is not None else config_semana.get(dia_semana_str, [])
    es_manual_fuerza = (rutina_manual is not None)
    cardio_manual = db_usuario.get("meta_cardio", {}).get(fecha_iso, None)
    if cardio_manual:
        rutina_cardio = cardio_manual
        es_manual_cardio = True
    else:
        if dia_semana_str in CARDIO_DEFAULTS_BY_DAY:
            rutina_cardio = CARDIO_DEFAULTS_BY_DAY[dia_semana_str]
        else:
            rutina_cardio = {"actividad": "Descanso Cardio"}
        es_manual_cardio = False
    tags_totales = set(['All'])
    for r in rutina_fuerza:
        if r in config_tags: tags_totales.update(config_tags[r])
    act = rutina_cardio.get("actividad", "Descanso Cardio")
    if act in TAGS_ACTIVIDADES: tags_totales.update(TAGS_ACTIVIDADES[act])
    return rutina_fuerza, rutina_cardio, tags_totales, es_manual_fuerza, es_manual_cardio, list(config_tags.keys())

def procesar_excel_rutina(uploaded_file):
    try:
        df_semana = pd.read_excel(uploaded_file, sheet_name='Semana')
        mapa_dias = {"lunes": "0", "martes": "1", "miércoles": "2", "miercoles": "2", "jueves": "3", "viernes": "4", "sábado": "5", "sabado": "5", "domingo": "6"}
        nueva_semana = {}
        for _, row in df_semana.iterrows():
            d = str(row.iloc[0]).lower().strip()
            r = str(row.iloc[1]).strip()
            if d in mapa_dias: nueva_semana[mapa_dias[d]] = [x.strip() for x in r.split(',')]
        df_tags = pd.read_excel(uploaded_file, sheet_name='Tags')
        nuevos_tags = {}
        for _, row in df_tags.iterrows():
            r = str(row.iloc[0]).strip()
            t = str(row.iloc[1])
            if pd.isna(t) or str(t).lower() == 'nan' or not str(t).strip(): nuevos_tags[r] = []
            else: nuevos_tags[r] = [x.strip() for x in str(t).split(',')]
        return {"semana": nueva_semana, "tags": nuevos_tags}
    except Exception as e: return None

# --- 5. HELPERS VISUALES Y LÓGICA ---
def mostrar_definiciones_ondas():
    with st.expander("ℹ️ Guía Técnica (nm/Hz)"):
        st.markdown("""
        **🔴 630nm / 660nm (Luz Roja):** Piel superficial, regeneración celular.
        **🟣 810nm / 850nm (NIR):** Profundidad (músculo/hueso), antiinflamatorio.
        **⚡ Frecuencias:** CW (Dosis), 10Hz (Alfa), 40Hz (Gamma), 50Hz (Analgesia).
        """)

def mostrar_ficha_tecnica(t, lista_completa):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Zona:** {t.zona}")
        st.markdown(f"**Intensidad:** {t.config_energia}")
    with c2:
        st.markdown(f"**Hz:** {t.herzios}")
        st.markdown(f"**Tiempo:** {t.duracion} min ({t.distancia})")
    st.markdown("---")
    st.caption("🚫 **Restricciones y Consejos:**")
    if t.momentos_prohibidos: st.write(f"⏰ **No usar:** {', '.join(t.momentos_prohibidos)}")
    reqs = [tag for tag in t.tags_entreno if tag != 'All']
    if reqs: st.write(f"🏋️ **Requiere:** {', '.join(reqs)}")
    if t.incompatible_with:
        mapa = {tr.id: tr.nombre for tr in lista_completa}
        nombres = [mapa.get(x, x) for x in t.incompatible_with]
        st.write(f"⚔️ **Incompatible con:** {', '.join(nombres)}")
    if t.incompatibilidades: st.warning(f"⚠️ {t.incompatibilidades}")
    c_ant, c_des = st.columns(2)
    with c_ant:
        st.markdown("**Antes:**")
        for tip in t.tips_antes: st.caption(f"• {tip}")
    with c_des:
        st.markdown("**Después:**")
        for tip in t.tips_despues: st.caption(f"• {tip}")

def analizar_bloqueos(tratamiento, momento, historial, registros_hoy, fecha_str, tags_dia, clave_usuario):
    if clave_usuario == "usuario_rutina":
        if 'Active' in tratamiento.tags_entreno and 'Active' not in tags_dia: return True, "⚠️ FALTA ACTIVIDAD"
        if 'Upper' in tratamiento.tags_entreno and 'Upper' not in tags_dia: return True, "⚠️ FALTA TORSO"
    if momento in tratamiento.momentos_prohibidos: return True, "⛔ HORARIO PROHIBIDO"
    dias_hechos = 0
    fecha_dt = datetime.date.fromisoformat(fecha_str)
    for i in range(7):
        f_check = (fecha_dt - timedelta(days=i)).isoformat()
        if f_check in historial and tratamiento.id in historial[f_check]: dias_hechos += 1
    hecho_hoy = (fecha_str in historial and tratamiento.id in historial[fecha_str])
    if not hecho_hoy and dias_hechos >= tratamiento.max_semanal: return True, "⛔ MAX SEMANAL"
    for inc in tratamiento.incompatible_with:
        if inc in registros_hoy: return True, "⛔ INCOMPATIBLE"
    return False, ""

def obtener_tratamientos_presentes(fecha_str, db_usuario, lista_tratamientos):
    # IDs de todos los tratamientos activos/planificados/registrados para cross-check
    presentes = set()
    # 1. Registrados (Hechos)
    presentes.update(db_usuario["historial"].get(fecha_str, {}).keys())
    # 2. Planificados (Ad-Hoc)
    presentes.update(db_usuario["planificados_adhoc"].get(fecha_str, {}).keys())
    # 3. Clínica Activa
    for t in lista_tratamientos:
        ciclo = db_usuario["ciclos_activos"].get(t.id)
        if ciclo and ciclo.get('activo') and ciclo.get('estado') == 'activo':
            presentes.add(t.id)
    return presentes

# ==============================================================================
# 6. MOTOR RENDERIZADO DIARIO (CORE)
# ==============================================================================
def renderizar_dia(fecha_obj):
    fecha_str = fecha_obj.isoformat()
    rutina_fuerza, rutina_cardio, tags_dia, man_f, man_c, todas_rutinas = obtener_rutina_completa(fecha_obj, st.session_state.db_global, db_usuario)
    ids_seleccionados_libre = []

    # --- A. SELECTORES RUTINA / CARDIO ---
    if clave_usuario == "usuario_rutina":
        c_fuerza, c_cardio = st.columns(2)
        
        with c_fuerza:
            st.markdown(f"**🏋️ Fuerza** ({'Manual' if man_f else 'Auto'})")
            opts_f = [k for k in todas_rutinas if "Remo" not in k and "Cinta" not in k and "Elíptica" not in k and "Andar" not in k]
            def_f = [x for x in rutina_fuerza if x in opts_f]
            sel_f = st.multiselect("Rutina:", opts_f, default=def_f, key=f"sf_{fecha_str}", label_visibility="collapsed")
            if set(sel_f) != set(rutina_fuerza):
                if "meta_diaria" not in db_usuario: db_usuario["meta_diaria"] = {}
                db_usuario["meta_diaria"][fecha_str] = sel_f
                guardar_datos_completos(st.session_state.db_global); st.rerun()
        
        with c_cardio:
            st.markdown(f"**🏃 Cardio** ({'Manual' if man_c else 'Auto'})")
            opts_c = ["Descanso Cardio", "Remo Ergómetro", "Cinta Inclinada", "Elíptica", "Andar", "Andar (Pasos)"]
            act_actual = rutina_cardio.get("actividad", "Descanso Cardio")
            if act_actual not in opts_c: act_actual = "Descanso Cardio"
            sel_c = st.selectbox("Actividad:", opts_c, index=opts_c.index(act_actual), key=f"sc_{fecha_str}", label_visibility="collapsed")
            
            params = rutina_cardio.copy(); params["actividad"] = sel_c
            if sel_c != "Descanso Cardio":
                c_p1, c_p2 = st.columns(2)
                if "tiempo" in GENERIC_CARDIO_PARAMS.get(sel_c, {}):
                    params["tiempo"] = c_p1.number_input("Min:", value=params.get("tiempo", 15), key=f"t_{fecha_str}")
                if "velocidad" in GENERIC_CARDIO_PARAMS.get(sel_c, {}):
                    params["velocidad"] = c_p2.number_input("Km/h:", value=params.get("velocidad", 6.5), key=f"v_{fecha_str}")
                if "inclinacion" in GENERIC_CARDIO_PARAMS.get(sel_c, {}):
                    params["inclinacion"] = c_p1.number_input("Inc %:", value=params.get("inclinacion", 0), key=f"i_{fecha_str}")
                if "pasos" in GENERIC_CARDIO_PARAMS.get(sel_c, {}):
                    params["pasos"] = c_p1.number_input("Pasos:", value=params.get("pasos", 10000), key=f"p_{fecha_str}")

            if params != rutina_cardio:
                if "meta_cardio" not in db_usuario: db_usuario["meta_cardio"] = {}
                db_usuario["meta_cardio"][fecha_str] = params
                guardar_datos_completos(st.session_state.db_global); st.rerun()

        key_conf = f"conf_{fecha_str}"
        if key_conf not in st.session_state: st.session_state[key_conf] = False
        if not st.session_state[key_conf]:
            if st.button("✅ Confirmar Rutina del Día", key=f"btn_c_{fecha_str}"):
                st.session_state[key_conf] = True; st.rerun()
        else:
            st.success("Rutina Confirmada")
    else:
        # Usuario Libre
        ids_guardados = db_usuario.get("meta_diaria", {}).get(fecha_str, [])
        ids_seleccionados_libre = ids_guardados
        mapa_n = {t.nombre: t.id for t in lista_tratamientos}
        mapa_i = {t.id: t.nombre for t in lista_tratamientos}
        sel_n = st.multiselect("Tratamientos hoy:", list(mapa_n.keys()), default=[mapa_i[i] for i in ids_guardados if i in mapa_i], key=f"ml_{fecha_str}")
        nuevos = [mapa_n[n] for n in sel_n]
        if set(nuevos) != set(ids_guardados):
            if "meta_diaria" not in db_usuario: db_usuario["meta_diaria"] = {}
            db_usuario["meta_diaria"][fecha_str] = nuevos
            guardar_datos_completos(st.session_state.db_global); st.rerun()
        st.session_state[f"conf_{fecha_str}"] = True

    st.divider()
    
    # --- B. PLANIFICACIÓN AD-HOC ---
    adhoc_hoy = db_usuario.get("planificados_adhoc", {}).get(fecha_str, {})
    presentes_hoy = obtener_tratamientos_presentes(fecha_str, db_usuario, lista_tratamientos)
    
    if clave_usuario == "usuario_rutina" and st.session_state.get(f"conf_{fecha_str}", False):
        with st.expander("➕ Añadir Tratamiento Adicional (Compatible)"):
            compatibles = []
            for t in lista_tratamientos:
                # Filtrar si ya está en clínica activo para no duplicar
                ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
                if ciclo and ciclo.get('activo') and ciclo.get('estado')=='activo': continue
                
                # Check Tags
                compatible_tag = False
                if 'All' in t.tags_entreno or any(tag in tags_dia for tag in t.tags_entreno): compatible_tag = True
                
                if compatible_tag:
                    # Check Incompatibilidad Cruzada con lo que YA hay hoy
                    choca = False
                    for pid in presentes_hoy:
                        # Si el nuevo choca con uno presente
                        if pid in t.incompatible_with: choca = True
                        # Si uno presente choca con el nuevo (buscar obj presente)
                        t_pres = next((tp for tp in lista_tratamientos if tp.id == pid), None)
                        if t_pres and t.id in t_pres.incompatible_with: choca = True
                    
                    if not choca:
                        compatibles.append(t)
            
            mapa_comp = {t.nombre: t for t in compatibles}
            sel_add = st.selectbox("Elegir:", ["--"] + list(mapa_comp.keys()), key=f"sad_{fecha_str}")
            if sel_add != "--":
                t_obj = mapa_comp[sel_add]
                st.caption(f"💡 {t_obj.momento_ideal_txt}")
                # FILTRO DE MOMENTOS
                opts_mom = ["🏋️ Entrenamiento (Pre)", "🚿 Post-Entreno / Mañana", "⛅ Tarde", "🌙 Noche"]
                valid_mom = [m for m in opts_mom if m not in t_obj.momentos_prohibidos]
                mom_sel = st.selectbox("Momento:", valid_mom, key=f"mad_{fecha_str}")
                
                bloq, mot = analizar_bloqueos(t_obj, mom_sel, db_usuario["historial"], {}, fecha_str, tags_dia, clave_usuario)
                if bloq: st.error(mot)
                else:
                    c_pl, c_reg = st.columns(2)
                    if c_pl.button("📅 Planificar", key=f"bad_{fecha_str}"):
                        if "planificados_adhoc" not in db_usuario: db_usuario["planificados_adhoc"] = {}
                        if fecha_str not in db_usuario["planificados_adhoc"]: db_usuario["planificados_adhoc"][fecha_str] = {}
                        db_usuario["planificados_adhoc"][fecha_str][t_obj.id] = mom_sel
                        guardar_datos_completos(st.session_state.db_global); st.rerun()
                    
                    if c_reg.button("✅ Registrar Ya", key=f"bdir_{fecha_str}"):
                        now = datetime.datetime.now().strftime('%H:%M')
                        if fecha_str not in db_usuario["historial"]: db_usuario["historial"][fecha_str] = {}
                        if t_obj.id not in db_usuario["historial"][fecha_str]: db_usuario["historial"][fecha_str][t_obj.id] = []
                        db_usuario["historial"][fecha_str][t_obj.id].append({"hora": now, "detalle": mom_sel})
                        # Opcional: añadirlo a adhoc también para que conste como planificado cumplido
                        if "planificados_adhoc" not in db_usuario: db_usuario["planificados_adhoc"] = {}
                        if fecha_str not in db_usuario["planificados_adhoc"]: db_usuario["planificados_adhoc"][fecha_str] = {}
                        db_usuario["planificados_adhoc"][fecha_str][t_obj.id] = mom_sel
                        
                        guardar_datos_completos(st.session_state.db_global); st.rerun()

    # --- C. PREPARACIÓN DE TARJETAS ---
    registros_dia = db_usuario["historial"].get(fecha_str, {})
    descartados = db_usuario.get("descartados", {}).get(fecha_str, [])
    lista_mostrar = []
    
    for t in lista_tratamientos:
        mostrar = False; origen = ""
        ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
        if ciclo and ciclo.get('activo') and ciclo.get('estado') == 'activo': mostrar = True; origen = "clinica"
        if t.id in adhoc_hoy: mostrar = True; origen = "adhoc"
        if clave_usuario != "usuario_rutina" and t.id in ids_seleccionados_libre: mostrar = True
        if mostrar: lista_mostrar.append((t, origen))

    # --- BOTÓN REGISTRAR TODO ---
    if lista_mostrar and st.button("⚡ Registrar Todos los Tratamientos del Día", key=f"all_{fecha_str}"):
        now = datetime.datetime.now().strftime('%H:%M')
        if fecha_str not in db_usuario["historial"]: db_usuario["historial"][fecha_str] = {}
        for t, origen in lista_mostrar:
            rad_key = f"rad_{t.id}_{fecha_str}"
            momento_a_guardar = st.session_state.get(rad_key)
            
            if not momento_a_guardar:
                if origen == "adhoc":
                    momento_a_guardar = adhoc_hoy.get(t.id)
                else:
                    # Lógica Fallback FLEX
                    mapa_inv = {"PRE": "🏋️ Entrenamiento (Pre)", "POST": "🚿 Post-Entreno / Mañana", "NIGHT": "🌙 Noche", "MORNING": "🌞 Mañana"}
                    pref = mapa_inv.get(t.default_visual_group)
                    
                    opts = ["🏋️ Entrenamiento (Pre)", "🚿 Post-Entreno / Mañana", "⛅ Tarde", "🌙 Noche"]
                    valid_opts = [o for o in opts if o not in t.momentos_prohibidos]
                    
                    if pref and pref in valid_opts: momento_a_guardar = pref
                    elif valid_opts: momento_a_guardar = valid_opts[0] # PRIMER VALIDO
            
            if momento_a_guardar:
                bloq, _ = analizar_bloqueos(t, momento_a_guardar, db_usuario["historial"], registros_dia, fecha_str, tags_dia, clave_usuario)
                if not bloq:
                    if t.id not in db_usuario["historial"][fecha_str] or not db_usuario["historial"][fecha_str][t.id]:
                        if t.id not in db_usuario["historial"][fecha_str]: db_usuario["historial"][fecha_str][t.id] = []
                        db_usuario["historial"][fecha_str][t.id].append({"hora": now, "detalle": momento_a_guardar})
        
        guardar_datos_completos(st.session_state.db_global); st.rerun()

    # --- AGRUPACIÓN VISUAL ---
    grupos = {"PRE": [], "POST": [], "MORNING": [], "NIGHT": [], "FLEX": [], "COMPLETED": [], "DISCARDED": [], "HIDDEN": []}
    mapa_vis = {"🏋️ Entrenamiento (Pre)": "PRE", "🚿 Post-Entreno / Mañana": "POST", "🌞 Mañana": "MORNING", "🌙 Noche": "NIGHT"}

    # Agrupar activos
    ids_mostrados = []
    for t, origen in lista_mostrar:
        ids_mostrados.append(t.id)
        hechos = len(registros_dia.get(t.id, []))
        if t.id in descartados: grupos["DISCARDED"].append((t, origen))
        elif hechos >= t.max_diario: grupos["COMPLETED"].append((t, origen))
        else:
            g = t.default_visual_group
            # Prioridad: Radio > Adhoc > Defecto
            rad_key = f"rad_{t.id}_{fecha_str}"
            if rad_key in st.session_state and st.session_state[rad_key] in mapa_vis: g = mapa_vis[st.session_state[rad_key]]
            elif origen == "adhoc" and adhoc_hoy.get(t.id) in mapa_vis: g = mapa_vis[adhoc_hoy[t.id]]
            if g in grupos: grupos[g].append((t, origen))
            else: grupos["FLEX"].append((t, origen))
    
    if clave_usuario == "usuario_rutina":
        for t in lista_tratamientos:
            if t.id not in ids_mostrados: grupos["HIDDEN"].append(t)

    # --- D. RENDERIZADO TARJETAS ---
    def render_card(item):
        t, origen = item
        hechos = len(registros_dia.get(t.id, []))
        icon = "❌" if t.id in descartados else ("✅" if hechos>=t.max_diario else "⬜")
        info_ex = ""
        ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
        if origen == "clinica" and ciclo:
            d = (fecha_obj - datetime.date.fromisoformat(ciclo['fecha_inicio'])).days
            saltos = len([s for s in ciclo.get('dias_saltados', []) if s < fecha_str])
            info_ex = f" (Día {d - saltos})"

        with st.expander(f"{icon} {t.nombre} ({hechos}/{t.max_diario}){info_ex}"):
            if t.id in descartados:
                mostrar_ficha_tecnica(t, lista_tratamientos)
                if st.button("Recuperar", key=f"rec_{t.id}_{fecha_str}"):
                    db_usuario["descartados"][fecha_str].remove(t.id)
                    guardar_datos_completos(st.session_state.db_global); st.rerun()
                return
            if hechos >= t.max_diario:
                st.success("✅ Completado")
                if st.button("↩️ Deshacer (Borrar Registro)", key=f"undo_{t.id}_{fecha_str}"):
                    del db_usuario["historial"][fecha_str][t.id]
                    guardar_datos_completos(st.session_state.db_global); st.rerun()
                return

            st.success(f"💡 {t.momento_ideal_txt}")
            mostrar_ficha_tecnica(t, lista_tratamientos)
            
            opts = ["🏋️ Entrenamiento (Pre)", "🚿 Post-Entreno / Mañana", "⛅ Tarde", "🌙 Noche"]
            valid = [o for o in opts if o not in t.momentos_prohibidos]
            idx_def = 0
            if origen == "adhoc" and adhoc_hoy.get(t.id) in valid: idx_def = valid.index(adhoc_hoy[t.id])
            
            sel = st.radio("Momento:", valid, index=idx_def, key=f"rad_{t.id}_{fecha_str}")
            
            c1, c2, c3 = st.columns([2,1,1])
            bloq, mot = analizar_bloqueos(t, sel, db_usuario["historial"], registros_dia, fecha_str, tags_dia, clave_usuario)
            if bloq: c1.warning(mot)
            
            if c1.button("Registrar", key=f"go_{t.id}_{fecha_str}", disabled=bloq):
                now = datetime.datetime.now().strftime('%H:%M')
                if fecha_str not in db_usuario["historial"]: db_usuario["historial"][fecha_str] = {}
                if t.id not in db_usuario["historial"][fecha_str]: db_usuario["historial"][fecha_str][t.id] = []
                db_usuario["historial"][fecha_str][t.id].append({"hora": now, "detalle": sel})
                guardar_datos_completos(st.session_state.db_global); st.rerun()
            
            if c2.button("Omitir", key=f"om_{t.id}_{fecha_str}"):
                if "descartados" not in db_usuario: db_usuario["descartados"] = {}
                if fecha_str not in db_usuario["descartados"]: db_usuario["descartados"][fecha_str] = []
                db_usuario["descartados"][fecha_str].append(t.id)
                if origen == "adhoc": del db_usuario["planificados_adhoc"][fecha_str][t.id]
                guardar_datos_completos(st.session_state.db_global); st.rerun()
            
            if origen == "clinica":
                if c3.button("⏭️ Saltar", help="Retrasa Fin", key=f"sk_{t.id}_{fecha_str}"):
                    if 'dias_saltados' not in ciclo: ciclo['dias_saltados'] = []
                    if fecha_str not in ciclo['dias_saltados']:
                        ciclo['dias_saltados'].append(fecha_str)
                        if "descartados" not in db_usuario: db_usuario["descartados"] = {}
                        if fecha_str not in db_usuario["descartados"]: db_usuario["descartados"][fecha_str] = []
                        db_usuario["descartados"][fecha_str].append(t.id)
                        guardar_datos_completos(st.session_state.db_global); st.rerun()
            elif origen == "adhoc":
                if c3.button("🗑️ Quitar", key=f"del_{t.id}_{fecha_str}"):
                    del db_usuario["planificados_adhoc"][fecha_str][t.id]
                    guardar_datos_completos(st.session_state.db_global); st.rerun()

    for g in ["MORNING", "PRE", "POST", "NIGHT", "FLEX"]:
        if grupos[g]:
            st.subheader(g)
            for item in grupos[g]: render_card(item)
    if grupos["COMPLETED"]:
        st.markdown("### ✅ Completados")
        for item in grupos["COMPLETED"]: render_card(item)
    if grupos["DISCARDED"]:
        st.markdown("### ❌ Descartados")
        for item in grupos["DISCARDED"]: render_card(item)
    if grupos["HIDDEN"] and clave_usuario == "usuario_rutina":
        with st.expander("Inactivos / Ocultos Hoy (Ver Detalles)"):
            for t in grupos["HIDDEN"]: 
                with st.expander(f"{t.nombre}"): mostrar_ficha_tecnica(t, lista_tratamientos)

# --- LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
def login_screen():
    st.title("🔐 Acceso")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        usr = st.selectbox("Usuario", ["Seleccionar...", "Benja", "Eva"])
        if st.button("Entrar", use_container_width=True) and usr != "Seleccionar...":
            st.session_state.logged_in = True
            st.session_state.current_user_name = usr
            st.session_state.current_user_role = "usuario_rutina" if usr == "Benja" else "usuario_libre"
            st.rerun()

if not st.session_state.logged_in: login_screen(); st.stop()

# --- CARGA GLOBAL ---
if 'db_global' not in st.session_state: st.session_state.db_global = cargar_datos_completos()
clave_usuario = st.session_state.current_user_role
db_usuario = st.session_state.db_global[clave_usuario]
lista_tratamientos = obtener_catalogo()

# --- SIDEBAR ---
with st.sidebar:
    st.write(f"Hola, **{st.session_state.current_user_name}**")
    menu_navegacion = st.radio("Menú", ["📅 Panel Diario", "🗓️ Panel Semanal", "📊 Historial", "🚑 Clínica"])
    if st.button("💾 Guardar Todo"):
        guardar_datos_completos(st.session_state.db_global); st.success("Guardado.")
    if clave_usuario == "usuario_rutina":
        with st.expander("⚙️ Importar Excel"):
            uploaded_file = st.file_uploader("Subir .xlsx", type=['xlsx'])
            if uploaded_file and st.button("Procesar"):
                new_conf = procesar_excel_rutina(uploaded_file)
                if new_conf:
                    st.session_state.db_global["configuracion_rutina"] = new_conf
                    guardar_datos_completos(st.session_state.db_global)
                    st.success("Correcto")
                    st.rerun()
    st.divider()
    mostrar_definiciones_ondas()
    st.divider()
    if st.button("Cerrar Sesión"): st.session_state.logged_in = False; st.rerun()

# ==========================================
# RUTAS DE NAVEGACIÓN
# ==========================================

if menu_navegacion == "📅 Panel Diario":
    st.title("📅 Panel Diario")
    c_f, c_r = st.columns([2,1])
    fecha_seleccionada = c_f.date_input("Fecha", datetime.date.today())
    renderizar_dia(fecha_seleccionada)

elif menu_navegacion == "🗓️ Panel Semanal":
    st.title("🗓️ Panel Semanal")
    d_ref = st.date_input("Semana de Referencia:", datetime.date.today())
    start_week = d_ref - timedelta(days=d_ref.weekday())
    tabs = st.tabs(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
    for i, tab in enumerate(tabs):
        with tab:
            dia_tab = start_week + timedelta(days=i)
            st.subheader(dia_tab.strftime("%A %d/%m"))
            renderizar_dia(dia_tab)

elif menu_navegacion == "🚑 Clínica":
    st.title("🚑 Clínica")
    
    # 1. Formulario Nuevo Tratamiento Dinámico
    with st.expander("🆕 Iniciar Nuevo Tratamiento"):
        zonas = list(DB_TRATAMIENTOS_BASE.keys())
        c1, c2, c3 = st.columns(3)
        z = c1.selectbox("Zona", ["--"] + zonas)
        if z != "--":
            pats = list(DB_TRATAMIENTOS_BASE[z].keys())
            p = c2.selectbox("Patología", ["--"] + pats)
            if p != "--":
                l = c3.selectbox("Lado", ["Derecho", "Izquierdo"])
                if l:
                    fi = st.date_input("Fecha Inicio", datetime.date.today())
                    if st.button("Comenzar Tratamiento"):
                        code_lado = "d" if l == "Derecho" else "i"
                        id_gen = f"{z.lower()[:3]}_{p.lower()[:3]}_{code_lado}"
                        id_gen = "".join(c for c in id_gen if c.isalnum() or c == "_")
                        
                        if "ciclos_activos" not in db_usuario: db_usuario["ciclos_activos"] = {}
                        db_usuario["ciclos_activos"][id_gen] = {
                            "fecha_inicio": fi.isoformat(),
                            "activo": True, "modo": "fases", "estado": "activo", "dias_saltados": []
                        }
                        guardar_datos_completos(st.session_state.db_global)
                        st.success("Tratamiento Iniciado"); st.rerun()

    st.divider()
    st.subheader("Tratamientos Activos")
    
    for t in lista_tratamientos:
        ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
        if ciclo:
            estado = ciclo.get('estado', 'activo')
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"**{t.nombre}** ({estado.upper()})")
                ini = datetime.date.fromisoformat(ciclo['fecha_inicio'])
                hoy = datetime.date.today()
                saltos = len([s for s in ciclo.get('dias_saltados', []) if s < hoy.isoformat()])
                dias = (hoy - ini).days - saltos
                c1.progress(min(dias/60, 1.0))
                c1.caption(f"Día {dias} | Inicio: {ini.strftime('%d/%m')}")
                
                if estado == 'activo':
                    if c2.button("Pausar", key=f"cp_{t.id}"):
                        ciclo['estado']='pausado'; ciclo['dias_acumulados']=dias; ciclo['activo']=False
                        guardar_datos_completos(st.session_state.db_global); st.rerun()
                else:
                    fr = c2.date_input("Retomar:", key=f"cfr_{t.id}")
                    if c2.button("Continuar", key=f"cc_{t.id}"):
                        ciclo['fecha_inicio'] = (fr - timedelta(days=ciclo['dias_acumulados'])).isoformat()
                        ciclo['estado']='activo'; ciclo['activo']=True; ciclo['dias_saltados']=[]; del ciclo['dias_acumulados']
                        guardar_datos_completos(st.session_state.db_global); st.rerun()
                
                if st.button("🗑️ Finalizar/Cancelar", key=f"cx_{t.id}"):
                    del db_usuario["ciclos_activos"][t.id]
                    guardar_datos_completos(st.session_state.db_global); st.rerun()

elif menu_navegacion == "📊 Historial":
    st.title("📊 Historial")
    vista = st.radio("Vista:", ["Semana", "Mes", "Año"], horizontal=True)
    hist = db_usuario.get("historial", {})
    t_usados = set([k for r in hist.values() for k in r.keys()])
    mapa = {t.id: t.nombre for t in lista_tratamientos}
    
    if vista == "Semana":
        d_ref = st.date_input("Semana:", datetime.date.today())
        start = d_ref - timedelta(days=d_ref.weekday())
        days = [start + timedelta(days=i) for i in range(7)]
        data = []
        for tid in t_usados:
            row = {"Tratamiento": mapa.get(tid, tid), "Total": 0}
            for i, d in enumerate(days):
                c = len(hist.get(d.isoformat(), {}).get(tid, []))
                row[["Lun","Mar","Mie","Jue","Vie","Sab","Dom"][i]] = "✅" * c
                row["Total"] += c
            if row["Total"] > 0: data.append(row)
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    elif vista == "Mes":
        d_ref = st.date_input("Mes:", datetime.date.today())
        m_str = d_ref.strftime("%Y-%m")
        counts = {}
        for f, r in hist.items():
            if f.startswith(m_str):
                for tid, l in r.items(): counts[mapa.get(tid, tid)] = counts.get(mapa.get(tid, tid), 0) + len(l)
        if counts: st.bar_chart(pd.DataFrame(list(counts.items()), columns=["T", "N"]).set_index("T"))
    elif vista == "Año":
        y_ref = st.number_input("Año:", value=datetime.date.today().year)
        y_str = str(y_ref)
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        data = []
        for tid in t_usados:
            row = {"T": mapa.get(tid, tid)}
            tot = 0
            for i in range(1, 13):
                m_key = f"{y_str}-{i:02d}"
                c = 0
                for f, r in hist.items():
                    if f.startswith(m_key): c += len(r.get(tid, []))
                row[meses[i-1]] = c
                tot += c
            if tot > 0: data.append(row)
        st.dataframe(pd.DataFrame(data), use_container_width=True)
