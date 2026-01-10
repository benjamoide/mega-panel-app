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

# --- RUTINA POR DEFECTO ---
RUTINA_BACKUP = {
    "0": ["FULLBODY I"], "1": ["TORSO I"], "2": ["FULLBODY II"],
    "3": ["TORSO II / CIRCUITO"], "4": ["PREVENTIVO I"], "5": ["PREVENTIVO II"],
    "6": ["Descanso Total"]
}

TAGS_BACKUP = {
    "FULLBODY I": ["Upper", "Lower", "Active"], 
    "TORSO I": ["Upper", "Active"],
    "FULLBODY II": ["Upper", "Lower", "Active"], 
    "TORSO II / CIRCUITO": ["Upper", "Active", "Cardio"],
    "PREVENTIVO I": ["Active"], 
    "PREVENTIVO II": ["Active"],
    "Cardio Genérico": ["Active"], 
    "Caminar 10.000 pasos": ["Active"],
    "Descanso Total": []
}

# --- CLASE DE TRATAMIENTO ---
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

# --- CATÁLOGO ---
def obtener_catalogo():
    fases_lesion = [
        {"nombre": "🔥 Fase 1: Inflamatoria/Aguda", "dias_fin": 7, "min_sesiones": 5},
        {"nombre": "🛠️ Fase 2: Proliferación", "dias_fin": 21, "min_sesiones": 10},
        {"nombre": "🧱 Fase 3: Remodelación", "dias_fin": 60, "min_sesiones": 20}
    ]
    
    catalogo = [
        # --- GRASA ---
        Tratamiento("fat_glutes", "Glúteos (Grasa)", "Glúteos/Caderas", "660nm + 850nm", "660nm: 100% | 850nm: 100%", "CW (0Hz)", "10-15 cm", 10, 1, 7, "GRASA", ['Active', 'Lower'], "PRE", "Ideal: Antes de Entrenar Pierna",
                    momentos_prohibidos=["🌙 Noche", "🚿 Post-Entreno / Mañana"], 
                    tips_antes=["💧 Beber agua.", "🧴 Piel limpia.", "👖 Ropa mínima."],
                    tips_despues=["🏃‍♂️ ACTIVIDAD YA: Sentadillas/Caminar.", "❌ NO sentarse en 45 min.", "🚿 Ducha post-ejercicio."],
                    incompatible_with=["fat_front", "fat_d", "fat_i"])
        .set_incompatibilidades("Tatuajes oscuros (absorben calor). Embarazo."),

        Tratamiento("fat_front", "Abdomen Frontal (Grasa)", "Abdomen", "660nm + 850nm", "660nm: 100% | 850nm: 100%", "CW (0Hz)", "10-15 cm", 10, 1, 7, "GRASA", ['Active'], "PRE", "Ideal: Antes de Entrenar",
                    momentos_prohibidos=["🌙 Noche", "🚿 Post-Entreno / Mañana"],
                    tips_antes=["💧 Beber agua.", "🧴 Piel limpia."],
                    tips_despues=["🏃‍♂️ ENTRENA YA.", "❌ Ayuno 1h post-sesión."],
                    incompatible_with=["fat_glutes"]),
        
        Tratamiento("fat_d", "Flanco Derecho (Grasa)", "Abdomen", "660nm + 850nm", "660nm: 100% | 850nm: 100%", "CW (0Hz)", "10-15 cm", 10, 1, 7, "GRASA", ['Active'], "PRE", "Ideal: Antes de Entrenar",
                    momentos_prohibidos=["🌙 Noche", "🚿 Post-Entreno / Mañana"],
                    tips_antes=["💧 Beber agua."],
                    tips_despues=["🏃‍♂️ ENTRENA YA."],
                    incompatible_with=["fat_glutes"]),
        
        Tratamiento("fat_i", "Flanco Izquierdo (Grasa)", "Abdomen", "660nm + 850nm", "660nm: 100% | 850nm: 100%", "CW (0Hz)", "10-15 cm", 10, 1, 7, "GRASA", ['Active'], "PRE", "Ideal: Antes de Entrenar",
                    momentos_prohibidos=["🌙 Noche", "🚿 Post-Entreno / Mañana"],
                    tips_antes=["💧 Beber agua."],
                    tips_despues=["🏃‍♂️ ENTRENA YA."],
                    incompatible_with=["fat_glutes"]),

        # --- ESTÉTICA ---
        Tratamiento("face_rejuv", "Rejuvenecimiento Facial", "Cara", "630nm/660nm (+850nm Opcional)", "630nm: 100% | 850nm: 50% (Opc)", "CW (0Hz)", "30-50 cm", 10, 1, 5, "PERMANENTE", ['All'], "FLEX", "Cualquier hora (Piel Limpia)",
                    momentos_prohibidos=["🏋️ Entrenamiento (Pre)"],
                    tips_antes=["🧼 DOBLE LIMPIEZA.", "🕶️ GAFAS OBLIGATORIAS.", "🧴 No Retinol."],
                    tips_despues=["🧴 Serum hidratante.", "❌ No sol directo.", "🚿 Ducha agua fría en cara OK."])
        .set_incompatibilidades("Melasma (Calor 850nm empeora, usar solo 630nm). Fotosensibilidad."),

        # --- LESIONES ---
        Tratamiento("foot_d", "Pie Derecho (Plantar/Lateral)", "Pie", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "50Hz (Dolor)", "10-15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["🦶 Piel limpia.", "❌ Quitar calcetín."],
                    tips_despues=["🎾 Rodar pelota suave.", "❌ Evitar saltos/impacto.", "🧊 Hielo si dolor."],
                    fases_config=fases_lesion)
        .set_incompatibilidades("Implantes metálicos."),

        Tratamiento("foot_i", "Pie Izquierdo (Plantar/Lateral)", "Pie", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "50Hz (Dolor)", "10-15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["🦶 Piel limpia.", "❌ Quitar calcetín."],
                    tips_despues=["🎾 Rodar pelota suave.", "❌ Evitar saltos.", "🧊 Hielo si dolor."],
                    fases_config=fases_lesion)
        .set_incompatibilidades("Implantes metálicos."),

        Tratamiento("epi_d", "Epicondilitis Dcha (Codo)", "Codo Lateral", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "50Hz (Dolor)", "10-15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["🧴 Piel limpia.", "❌ Quitar cincha."],
                    tips_despues=["🛑 NO hacer pinza con dedos.", "🚫 No rotaciones (llaves).", "🧊 Hielo local."],
                    incompatible_with=["codo_d"], 
                    fases_config=fases_lesion)
        .set_incompatibilidades("Infiltración <5 días."),

        Tratamiento("epi_i", "Epicondilitis Izq (Codo)", "Codo Lateral", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "50Hz (Dolor)", "10-15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["🧴 Piel limpia.", "❌ Quitar cincha."],
                    tips_despues=["🛑 NO hacer pinza.", "🚫 No rotaciones.", "🧊 Hielo local."],
                    incompatible_with=["codo_i"],
                    fases_config=fases_lesion)
        .set_incompatibilidades("Infiltración <5 días."),

        Tratamiento("forearm_inj_d", "Tendinitis Antebrazo D", "Muñeca/Vientre", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "50Hz (Dolor)", "10-15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["⌚ Quitar reloj.", "🧴 Piel limpia."],
                    tips_despues=["👋 Movilidad suave.", "❌ No cargar peso muerto.", "🧊 Hielo local."],
                    incompatible_with=["arm_d"],
                    fases_config=fases_lesion)
        .set_incompatibilidades("Implantes."),

        Tratamiento("forearm_inj_i", "Tendinitis Antebrazo I", "Muñeca/Vientre", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "50Hz (Dolor)", "10-15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["⌚ Quitar reloj.", "🧴 Piel limpia."],
                    tips_despues=["👋 Movilidad suave.", "❌ No cargar peso.", "🧊 Hielo local."],
                    incompatible_with=["arm_i"],
                    fases_config=fases_lesion)
        .set_incompatibilidades("Implantes."),

        Tratamiento("shoulder_d", "Hombro Dcho (Lesión)", "Deltoides", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "10Hz - 40Hz", "15-20 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["👕 Sin ropa compresiva.", "🧴 Piel limpia."],
                    tips_despues=["🔄 Movimientos pendulares.", "❌ No elevar brazo sobre cabeza.", "🧊 Hielo si dolor."],
                    fases_config=fases_lesion)
        .set_incompatibilidades("Marcapasos. Implantes."),

        Tratamiento("shoulder_i", "Hombro Izq (Lesión)", "Deltoides", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "10Hz - 40Hz", "15-20 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["👕 Sin ropa compresiva.", "🧴 Piel limpia."],
                    tips_despues=["🔄 Movimientos pendulares.", "❌ No elevar brazo sobre cabeza.", "🧊 Hielo si dolor."],
                    fases_config=fases_lesion)
        .set_incompatibilidades("Marcapasos. Implantes."),

        Tratamiento("rodilla_d", "Rodilla Dcha (Lesión)", "Rodilla", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "10Hz (Hueso)", "15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["❄️ NO hielo antes.", "🧴 Piel limpia."],
                    tips_despues=["🦶 Movilidad sin carga.", "🚿 Ducha fría OK.", "🧊 Hielo OK."],
                    fases_config=fases_lesion)
        .set_incompatibilidades("Implantes metálicos."),
        
        Tratamiento("rodilla_i", "Rodilla Izq (Lesión)", "Rodilla", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "10Hz (Hueso)", "15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["❄️ NO hielo antes.", "🧴 Piel limpia."],
                    tips_despues=["🦶 Movilidad sin carga.", "🚿 Ducha fría OK.", "🧊 Hielo OK."],
                    fases_config=fases_lesion)
        .set_incompatibilidades("Implantes metálicos."),
        
        Tratamiento("codo_d", "Codo Dcho (Genérico)", "Codo", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "10Hz", "15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["🧴 Piel limpia."],
                    tips_despues=["🔄 Estiramiento suave.", "❌ No cargar peso.", "🚿 Ducha normal."],
                    incompatible_with=["epi_d"],
                    fases_config=fases_lesion)
        .set_incompatibilidades("No infiltración <5 días."),
        
        Tratamiento("codo_i", "Codo Izq (Genérico)", "Codo", "660nm + 850nm", "660nm: 50% | 850nm: 100%", "10Hz", "15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["🧴 Piel limpia."],
                    tips_despues=["🔄 Estiramiento suave.", "❌ No cargar peso.", "🚿 Ducha normal."],
                    incompatible_with=["epi_i"],
                    fases_config=fases_lesion)
        .set_incompatibilidades("No infiltración <5 días."),
        
        # --- MÚSCULO ---
        Tratamiento("arm_d", "Antebrazo D (Recuperación)", "Antebrazo", "660nm + 850nm", "660nm: 100% | 850nm: 100%", "10Hz (Recuperación)", "15 cm", 10, 1, 6, "MUSCULAR", ['Upper'], "POST", "Ideal: Post-Entreno",
                    momentos_prohibidos=["🏋️ Entrenamiento (Pre)"], 
                    tips_antes=["🚿 Quitar sudor.", "💧 Beber agua."],
                    tips_despues=["🥩 Proteína.", "🚿 Ducha contraste (Frío/Calor).", "🛌 Descansar zona."],
                    incompatible_with=["forearm_inj_d"])
        .set_incompatibilidades("Opcional: Pulsos 50Hz."),
        
        Tratamiento("arm_i", "Antebrazo I (Recuperación)", "Antebrazo", "660nm + 850nm", "660nm: 100% | 850nm: 100%", "10Hz (Recuperación)", "15 cm", 10, 1, 6, "MUSCULAR", ['Upper'], "POST", "Ideal: Post-Entreno",
                    momentos_prohibidos=["🏋️ Entrenamiento (Pre)"],
                    tips_antes=["🚿 Quitar sudor.", "💧 Beber agua."],
                    tips_despues=["🥩 Proteína.", "🚿 Ducha contraste.", "🛌 Descansar zona."],
                    incompatible_with=["forearm_inj_i"])
        .set_incompatibilidades("Opcional: Pulsos 50Hz."),
        
        # --- PERMANENTES ---
        Tratamiento("testo", "Boost Testosterona", "Testículos", "660nm + 850nm", "660nm: 100% | 850nm: 100%", "CW (0Hz)", "15 cm", 5, 1, 7, "PERMANENTE", ['All'], "MORNING", "Mañana",
                    momentos_prohibidos=["🌙 Noche", "⛅ Tarde", "🚿 Post-Entreno / Mañana"], 
                    tips_antes=["🚿 Piel limpia.", "❄️ Zona fresca (no calentar)."],
                    tips_despues=["🚿 Ducha fría obligatoria/recomendada.", "❌ Ropa holgada.", "🏋️ Pesas luego ayuda."])
        .set_incompatibilidades("Varicocele."),
        
        Tratamiento("sleep", "Sueño y Ritmo", "Ambiente", "Solo 630nm/660nm", "630nm: 20% | 850nm: 0%", "CW (0Hz)", ">50 cm", 15, 1, 7, "PERMANENTE", ['All'], "NIGHT", "Noche",
                    momentos_prohibidos=["🌞 Mañana", "⛅ Tarde", "🏋️ Entrenamiento (Pre)", "🚿 Post-Entreno / Mañana"],
                    tips_antes=["📵 Apagar pantallas/móvil.", "💡 Luces apagadas."],
                    tips_despues=["🛌 Dormir inmediatamente.", "❌ PROHIBIDO mirar móvil.", "🚿 Ducha tibia relaja."],
                    incompatible_with=["brain"])
        .set_incompatibilidades("⛔ NO USAR PULSOS."),
        
        Tratamiento("brain", "Salud Cerebral", "Cabeza", "Solo 810nm/850nm", "660nm: 0% | 850nm: 100%", "40Hz (Gamma)", "30 cm", 10, 1, 5, "PERMANENTE", ['All'], "FLEX", "Mañana/Tarde",
                    momentos_prohibidos=["🌙 Noche"],
                    tips_antes=["🕶️ GAFAS PUESTAS OBLIGATORIAS."],
                    tips_despues=["🧠 Tarea cognitiva/Trabajo.", "🛑 No dormir siesta inmediata."],
                    incompatible_with=["sleep"])
        .set_incompatibilidades("⛔ GAFAS OBLIGATORIAS.")
    ]
    return catalogo

# --- GESTIÓN DE DATOS ---
def cargar_datos_completos():
    if not os.path.exists(ARCHIVO_DATOS):
        return {"configuracion_rutina": {"semana": RUTINA_BACKUP, "tags": TAGS_BACKUP},
                "usuario_rutina": {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}, 
                "usuario_libre": {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}}
    try:
        with open(ARCHIVO_DATOS, 'r') as f:
            datos = json.load(f)
            if "configuracion_rutina" not in datos: datos["configuracion_rutina"] = {"semana": RUTINA_BACKUP, "tags": TAGS_BACKUP}
            for user in ["usuario_rutina", "usuario_libre"]:
                if user not in datos: datos[user] = {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}
            return datos
    except:
        return {"configuracion_rutina": {"semana": RUTINA_BACKUP, "tags": TAGS_BACKUP},
                "usuario_rutina": {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}, 
                "usuario_libre": {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}}

def guardar_datos_completos(datos):
    with open(ARCHIVO_DATOS, 'w') as f:
        json.dump(datos, f, indent=4)

def obtener_rutina_y_tags(fecha_obj, db_global, db_usuario):
    fecha_iso = fecha_obj.isoformat()
    dia_semana = str(fecha_obj.weekday())
    rutina_manual = db_usuario.get("meta_diaria", {}).get(fecha_iso, None)
    config_semana = db_global.get("configuracion_rutina", {}).get("semana", RUTINA_BACKUP)
    config_tags = db_global.get("configuracion_rutina", {}).get("tags", TAGS_BACKUP)
    
    if rutina_manual is not None:
        rutina_nombres = rutina_manual
        es_manual = True
    else:
        rutina_nombres = config_semana.get(dia_semana, [])
        es_manual = False
    
    tags_calculados = set()
    for nombre in rutina_nombres:
        if nombre in config_tags:
            tags_calculados.update(config_tags[nombre])
    tags_calculados.add('All')
    return rutina_nombres, tags_calculados, list(config_tags.keys()), es_manual

# --- HELPERS ---
def mostrar_definiciones_ondas():
    with st.expander("ℹ️ Guía Técnica (nm/Hz)"):
        st.markdown("""
        **🔴 630nm / 660nm (Luz Roja):** Piel superficial, regeneración celular.
        **🟣 810nm / 850nm (NIR):** Profundidad (músculo/hueso), antiinflamatorio.
        **⚡ Frecuencias:**
        * **CW (0Hz):** Dosis continua (Piel/Grasa).
        * **10Hz (Alfa):** Regeneración, relajación.
        * **40Hz (Gamma):** Cerebro/Cognición.
        * **50Hz:** Analgesia (Dolor).
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
        if 'Active' in tratamiento.tags_entreno and 'Active' not in tags_dia: return True, "⚠️ FALTA ACTIVIDAD: Requiere ejercicio."
        if 'Upper' in tratamiento.tags_entreno and 'Upper' not in tags_dia: return True, "⚠️ SINERGIA BAJA: Requiere torso."
    if momento in tratamiento.momentos_prohibidos: return True, "⛔ HORARIO PROHIBIDO."
    dias_hechos = 0
    fecha_dt = datetime.date.fromisoformat(fecha_str)
    for i in range(7):
        f_check = (fecha_dt - timedelta(days=i)).isoformat()
        if f_check in historial and tratamiento.id in historial[f_check]: dias_hechos += 1
    hecho_hoy = (fecha_str in historial and tratamiento.id in historial[fecha_str])
    if not hecho_hoy and dias_hechos >= tratamiento.max_semanal: return True, "⛔ LÍMITE SEMANAL."
    for inc in tratamiento.incompatible_with:
        if inc in registros_hoy: return True, "⛔ INCOMPATIBLE."
    return False, ""

# --- COMPONENTE RENDERIZAR DÍA ---
def renderizar_dia(fecha_obj):
    fecha_str = fecha_obj.isoformat()
    rutina_hoy_nombres, tags_dia, todas_rutinas, es_manual = obtener_rutina_y_tags(fecha_obj, st.session_state.db_global, db_usuario)
    
    if clave_usuario == "usuario_rutina":
        defaults_seguros = [x for x in rutina_hoy_nombres if x in todas_rutinas]
        key_sel = f"sel_rut_{fecha_str}"
        sel = st.multiselect(f"Rutina ({'Manual' if es_manual else 'Auto'}):", todas_rutinas, default=defaults_seguros, key=key_sel)
        if set(sel) != set(rutina_hoy_nombres):
            if "meta_diaria" not in db_usuario: db_usuario["meta_diaria"] = {}
            db_usuario["meta_diaria"][fecha_str] = sel
            guardar_datos_completos(st.session_state.db_global); st.rerun()
        config_tags = st.session_state.db_global.get("configuracion_rutina", {}).get("tags", TAGS_BACKUP)
        tags_dia = set()
        for r in sel: 
            if r in config_tags: tags_dia.update(config_tags[r])
        tags_dia.add('All')
    else:
        ids_guardados = db_usuario.get("meta_diaria", {}).get(fecha_str, [])
        mapa_n = {t.nombre: t.id for t in lista_tratamientos}
        mapa_i = {t.id: t.nombre for t in lista_tratamientos}
        key_multi = f"multi_lib_{fecha_str}"
        sel_n = st.multiselect("Tratamientos hoy:", list(mapa_n.keys()), default=[mapa_i[i] for i in ids_guardados if i in mapa_i], key=key_multi)
        nuevos = [mapa_n[n] for n in sel_n]
        if set(nuevos) != set(ids_guardados):
            if "meta_diaria" not in db_usuario: db_usuario["meta_diaria"] = {}
            db_usuario["meta_diaria"][fecha_str] = nuevos
            guardar_datos_completos(st.session_state.db_global); st.rerun()
        tags_dia = {'All', 'Active', 'Upper', 'Lower'}

    st.divider()
    registros_dia = db_usuario["historial"].get(fecha_str, {})
    descartados = db_usuario.get("descartados", {}).get(fecha_str, [])
    grupos = {"PRE": [], "POST": [], "MORNING": [], "NIGHT": [], "FLEX": [], "COMPLETED": [], "HIDDEN": [], "DISCARDED": []}
    mapa_vis = {"🏋️ Entrenamiento (Pre)": "PRE", "🚿 Post-Entreno / Mañana": "POST", "🌞 Mañana": "MORNING", "🌙 Noche": "NIGHT"}

    for t in lista_tratamientos:
        aplica = False
        if t.tipo == "LESION":
            ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
            if ciclo and ciclo.get('activo') and ciclo.get('estado') == 'activo': aplica = True
            else: continue 
        elif clave_usuario == "usuario_rutina":
            if t.tipo == "PERMANENTE": aplica = True
            elif t.tipo == "GRASA" and "Active" in tags_dia: aplica = True
            elif t.tipo == "MUSCULAR":
                if any(tag in tags_dia for tag in t.tags_entreno): aplica = True
        else:
            if t.id in ids_seleccionados_libre or len(registros_dia.get(t.id, [])) > 0: aplica = True

        hechos = len(registros_dia.get(t.id, []))
        if t.id in descartados: grupos["DISCARDED"].append(t)
        elif not aplica: grupos["HIDDEN"].append(t)
        elif hechos >= t.max_diario: grupos["COMPLETED"].append(t)
        else:
            g = t.default_visual_group
            rad_key = f"rad_{t.id}_{fecha_str}"
            if rad_key in st.session_state and st.session_state[rad_key] in mapa_vis: g = mapa_vis[st.session_state[rad_key]]
            elif hechos > 0:
                last = registros_dia[t.id][-1]['detalle']
                for k,v in mapa_vis.items():
                    if k in last: g = v
            if g in grupos: grupos[g].append(t)
            else: grupos["FLEX"].append(t)

    def render_tarjeta(t, modo="normal"):
        hechos = len(registros_dia.get(t.id, []))
        icon = "❌" if modo=="discarded" else ("✅" if hechos>=t.max_diario else "⬜")
        info_ex = ""
        if t.tipo == "LESION":
            ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
            if ciclo:
                d = (fecha_obj - datetime.date.fromisoformat(ciclo['fecha_inicio'])).days
                info_ex = f" (Día {d})"

        with st.expander(f"{icon} {t.nombre} ({hechos}/{t.max_diario}){info_ex}"):
            if modo=="discarded":
                mostrar_ficha_tecnica(t, lista_tratamientos)
                if st.button("Recuperar", key=f"rec_{t.id}_{fecha_str}"):
                    db_usuario["descartados"][fecha_str].remove(t.id)
                    guardar_datos_completos(st.session_state.db_global); st.rerun()
                return
            if modo!="readonly":
                st.success(f"💡 {t.momento_ideal_txt}")
                mostrar_ficha_tecnica(t, lista_tratamientos)
            if hechos > 0:
                st.markdown("---")
                for i, r in enumerate(registros_dia.get(t.id, [])):
                    c_txt, c_del = st.columns([5,1])
                    c_txt.info(f"✅ {r['hora']} ({r['detalle']})")
                    if c_del.button("🗑️", key=f"d_{t.id}_{i}_{fecha_str}"):
                        registros_dia[t.id].pop(i)
                        if not registros_dia[t.id]: del registros_dia[t.id]
                        guardar_datos_completos(st.session_state.db_global); st.rerun()
            if modo=="normal":
                st.markdown("---")
                opts = ["🏋️ Entrenamiento (Pre)", "🚿 Post-Entreno / Mañana", "⛅ Tarde", "🌙 Noche"]
                valid = [o for o in opts if o not in t.momentos_prohibidos]
                sel = st.radio("Momento:", valid, key=f"rad_{t.id}_{fecha_str}")
                bloq, mot = analizar_bloqueos(t, sel, db_usuario["historial"], registros_dia, fecha_str, tags_dia, clave_usuario)
                c_go, c_no = st.columns([3,1])
                with c_go:
                    if bloq:
                        st.error(mot)
                        st.button("🚫 Bloqueado", disabled=True, key=f"bx_{t.id}_{fecha_str}")
                    else:
                        if st.button("Registrar", key=f"go_{t.id}_{fecha_str}"):
                            now = datetime.datetime.now().strftime('%H:%M')
                            if fecha_str not in db_usuario["historial"]: db_usuario["historial"][fecha_str] = {}
                            if t.id not in db_usuario["historial"][fecha_str]: db_usuario["historial"][fecha_str][t.id] = []
                            db_usuario["historial"][fecha_str][t.id].append({"hora": now, "detalle": sel})
                            guardar_datos_completos(st.session_state.db_global); st.rerun()
                with c_no:
                    if st.button("Omitir", key=f"om_{t.id}_{fecha_str}"):
                        if "descartados" not in db_usuario: db_usuario["descartados"] = {}
                        if fecha_str not in db_usuario["descartados"]: db_usuario["descartados"][fecha_str] = []
                        db_usuario["descartados"][fecha_str].append(t.id)
                        guardar_datos_completos(st.session_state.db_global); st.rerun()

    cats = ["MORNING", "PRE", "POST", "NIGHT", "FLEX"]
    for c in cats:
        if grupos[c]:
            st.subheader(c)
            for t in grupos[c]: render_tarjeta(t)
    if grupos["COMPLETED"]:
        st.markdown("### ✅ Completados")
        for t in grupos["COMPLETED"]: render_tarjeta(t, "readonly")
    if grupos["DISCARDED"]:
        st.markdown("### ❌ Descartados")
        for t in grupos["DISCARDED"]: render_tarjeta(t, "discarded")
    if grupos["HIDDEN"] and clave_usuario == "usuario_rutina":
        with st.expander("Inactivos / Ocultos Hoy (Ver Detalles)"):
            for t in grupos["HIDDEN"]: 
                with st.expander(f"{t.nombre}"):
                    mostrar_ficha_tecnica(t, lista_tratamientos)

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

if not st.session_state.logged_in:
    login_screen(); st.stop()

# --- CARGA GLOBAL ---
if 'db_global' not in st.session_state: st.session_state.db_global = cargar_datos_completos()
clave_usuario = st.session_state.current_user_role
db_usuario = st.session_state.db_global[clave_usuario]
lista_tratamientos = obtener_catalogo()

# --- SIDEBAR ---
with st.sidebar:
    st.write(f"Hola, **{st.session_state.current_user_name}**")
    menu_navegacion = st.radio("Menú", ["📅 Panel Diario", "🗓️ Panel Semanal", "📊 Historial", "🚑 Clínica"])
    if clave_usuario == "usuario_rutina":
        with st.expander("⚙️ Importar Excel"):
            uploaded_file = st.file_uploader("Subir .xlsx", type=['xlsx'])
            if uploaded_file and st.button("Procesar"):
                try:
                    df_sem = pd.read_excel(uploaded_file, sheet_name='Semana')
                    df_tag = pd.read_excel(uploaded_file, sheet_name='Tags')
                    st.success("Simulado")
                except: st.error("Error Excel")
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
    hoy = datetime.date.today()
    inicio_sem = hoy - timedelta(days=hoy.weekday())
    tabs = st.tabs(["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"])
    for i, tab in enumerate(tabs):
        with tab:
            dia_tab = inicio_sem + timedelta(days=i)
            st.subheader(dia_tab.strftime("%A %d/%m"))
            renderizar_dia(dia_tab)

elif menu_navegacion == "🚑 Clínica":
    st.title("🚑 Clínica de Recuperación")
    
    def comprobar_inicio_seguro(tratamiento_nuevo, fecha_inicio_obj, ciclos_activos, historial_usuario):
        fecha_inicio_str = fecha_inicio_obj.isoformat()
        for id_activo, datos in ciclos_activos.items():
            if datos.get('activo') and id_activo in tratamiento_nuevo.incompatible_with:
                nom = next((t.nombre for t in lista_tratamientos if t.id == id_activo), id_activo)
                return False, f"⚠️ CONFLICTO PROTOCOLO: Tienes activo '{nom}'."
        if clave_usuario == "usuario_rutina":
            rutina, tags_dia_inicio, _, _ = obtener_rutina_y_tags(fecha_inicio_obj, st.session_state.db_global, db_usuario)
            for tag_req in tratamiento_nuevo.tags_entreno:
                if tag_req != 'All' and tag_req not in tags_dia_inicio:
                    return False, f"⚠️ INCOMPATIBLE: El {fecha_inicio_str} toca {rutina}. Falta '{tag_req}'."
        return True, ""

    tratamientos_lesion = [t for t in lista_tratamientos if t.tipo == "LESION"]
    for t in tratamientos_lesion:
        ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
        estado_actual = ciclo.get('estado', 'activo') if ciclo else 'inactivo'
        container = st.container(border=True)
        with container:
            c1, c2 = st.columns([3, 1])
            c1.subheader(f"{t.nombre}")
            c1.caption(f"📍 {t.zona} | {t.herzios}")
            if ciclo and estado_actual != 'inactivo':
                inicio = datetime.date.fromisoformat(ciclo['fecha_inicio'])
                hoy = datetime.date.today()
                if estado_actual == 'pausado':
                    dias = ciclo.get('dias_acumulados', 0)
                    status_txt = f"⏸️ PAUSADO (Día {dias})"
                else:
                    dias = (hoy - inicio).days
                    status_txt = f"✅ ACTIVO (Día {dias})"
                fase_txt = "Mantenimiento"
                progreso = 0.0
                if ciclo.get('modo') == 'fases':
                    for f in t.fases_config:
                        if dias <= f['dias_fin']: fase_txt = f['nombre']; progreso = max(0.0, min(dias/60, 1.0)); break
                    if dias > 60: fase_txt="Finalizado"; progreso=1.0
                c1.info(f"{status_txt} | {fase_txt}")
                c1.progress(progreso)
                cc = c1.columns(3)
                if estado_actual == 'activo':
                    if cc[0].button("⏸️ Pausar", key=f"p_{t.id}"):
                        ciclo['estado']='pausado'; ciclo['dias_acumulados']=dias; ciclo['activo']=False
                        guardar_datos_completos(st.session_state.db_global); st.rerun()
                elif estado_actual == 'pausado':
                    fr = cc[0].date_input("Retomar:", datetime.date.today(), key=f"fr_{t.id}")
                    if cc[0].button("▶️ Continuar", key=f"c_{t.id}"):
                        ciclo['fecha_inicio'] = (fr - timedelta(days=ciclo['dias_acumulados'])).isoformat()
                        ciclo['estado']='activo'; ciclo['activo']=True; del ciclo['dias_acumulados']
                        guardar_datos_completos(st.session_state.db_global); st.rerun()
                if cc[1].button("🔄 Reiniciar", key=f"r_{t.id}"):
                    db_usuario["ciclos_activos"][t.id] = {"fecha_inicio": datetime.date.today().isoformat(), "activo": True, "modo": "fases", "estado": "activo"}
                    guardar_datos_completos(st.session_state.db_global); st.rerun()
                if cc[2].button("🗑️ Cancelar", key=f"x_{t.id}"):
                    del db_usuario["ciclos_activos"][t.id]; guardar_datos_completos(st.session_state.db_global); st.rerun()
            else:
                fi = c2.date_input("Inicio:", datetime.date.today(), key=f"fi_{t.id}")
                if c2.button("Comenzar", key=f"go_{t.id}"):
                    ok, m = comprobar_inicio_seguro(t, fi, db_usuario.get("ciclos_activos",{}), db_usuario.get("historial",{}))
                    if ok:
                        if "ciclos_activos" not in db_usuario: db_usuario["ciclos_activos"] = {}
                        db_usuario["ciclos_activos"][t.id] = {"fecha_inicio": fi.isoformat(), "activo": True, "modo": "fases", "estado": "activo"}
                        guardar_datos_completos(st.session_state.db_global); st.rerun()
                    else: st.error(m)

elif menu_navegacion == "📊 Historial":
    st.title("📊 Historial y Progreso")
    
    # Selector de Vista Principal
    vista_historial = st.radio("Vista:", ["Semana", "Mes", "Año"], horizontal=True)
    historial = db_usuario.get("historial", {})
    
    # Preparar tratamientos
    mapa_ids = {t.id: t.nombre for t in lista_tratamientos}
    tratamientos_usados = set()
    for f, regs in historial.items():
        for tid in regs.keys(): tratamientos_usados.add(tid)
    
    if vista_historial == "Semana":
        st.subheader("📅 Vista Semanal")
        d_ref = st.date_input("Seleccionar semana (por día):", datetime.date.today())
        start_week = d_ref - timedelta(days=d_ref.weekday())
        days_week = [start_week + timedelta(days=i) for i in range(7)]
        headers = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        data = []
        for tid in tratamientos_usados:
            row = {"Tratamiento": mapa_ids.get(tid, tid), "Total": 0}
            total_sem = 0
            for i, d in enumerate(days_week):
                d_str = d.isoformat()
                count = len(historial.get(d_str, {}).get(tid, []))
                row[headers[i]] = "✅" * count if count > 0 else ""
                total_sem += count
            row["Total"] = total_sem
            if total_sem > 0: data.append(row) # Solo mostrar si hay actividad
            
        if data: st.dataframe(pd.DataFrame(data).set_index("Tratamiento"), use_container_width=True)
        else: st.info("No hay datos en esta semana.")

    elif vista_historial == "Mes":
        st.subheader("📆 Vista Mensual")
        # Selector mes/año (simplificado con date_input)
        d_ref = st.date_input("Seleccionar Mes (día cualquiera):", datetime.date.today())
        mes_str = d_ref.strftime("%Y-%m")
        
        counts = {}
        for f_str, regs in historial.items():
            if f_str.startswith(mes_str):
                for tid, sessions in regs.items():
                    nom = mapa_ids.get(tid, tid)
                    counts[nom] = counts.get(nom, 0) + len(sessions)
        
        if counts:
            df = pd.DataFrame(list(counts.items()), columns=["Tratamiento", "Sesiones"]).sort_values("Sesiones", ascending=False)
            c1, c2 = st.columns([1, 2])
            c1.dataframe(df, hide_index=True, use_container_width=True)
            c2.bar_chart(df.set_index("Tratamiento"))
        else: st.info("No hay datos en este mes.")

    elif vista_historial == "Año":
        st.subheader("📈 Vista Anual")
        year_sel = st.number_input("Año:", value=datetime.date.today().year, step=1)
        year_str = str(year_sel)
        
        months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        data_anual = []
        
        for tid in tratamientos_usados:
            row = {"Tratamiento": mapa_ids.get(tid, tid)}
            total_anual = 0
            for m_idx in range(1, 13):
                m_str = f"{year_str}-{m_idx:02d}"
                count_mes = 0
                for f_str, regs in historial.items():
                    if f_str.startswith(m_str):
                        count_mes += len(regs.get(tid, []))
                row[months[m_idx-1]] = count_mes if count_mes > 0 else 0
                total_anual += count_mes
            row["Total"] = total_anual
            if total_anual > 0: data_anual.append(row)
            
        if data_anual:
            st.dataframe(pd.DataFrame(data_anual).set_index("Tratamiento"), use_container_width=True)
        else: st.info("No hay datos en este año.")
