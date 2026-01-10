import streamlit as st
import datetime
import json
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Mega Panel AI",
    page_icon="🧬",
    layout="centered"
)

# --- ARCHIVO DE DATOS ---
ARCHIVO_DATOS = 'historial_mega_panel_final.json'

# --- CLASE DE TRATAMIENTO ---
class Tratamiento:
    def __init__(self, id_t, nombre, zona, ondas, intensidad, distancia, duracion, max_diario, tiempo_espera_horas, tipo, tags_entreno, default_visual_group, momento_ideal_txt, tips_antes, tips_despues, fases_info=None):
        self.id = id_t
        self.nombre = nombre
        self.zona = zona
        self.ondas = ondas
        self.intensidad = intensidad
        self.distancia = distancia
        self.duracion = duracion
        self.max_diario = max_diario
        self.tiempo_espera_horas = tiempo_espera_horas
        self.tipo = tipo
        self.tags_entreno = tags_entreno 
        self.default_visual_group = default_visual_group 
        self.momento_ideal_txt = momento_ideal_txt 
        self.tips_antes = tips_antes
        self.tips_despues = tips_despues
        self.incompatibilidades = "" 
        self.fases_info = fases_info if fases_info else {}

    def set_incompatibilidades(self, texto):
        self.incompatibilidades = texto
        return self

# --- CATÁLOGO COMPLETO ---
@st.cache_data
def obtener_catalogo():
    fases_articulacion = {
        7: "🔥 Fase 1: Aguda (Bajar dolor)",
        21: "🛠️ Fase 2: Proliferación (Generar tejido)",
        60: "🧱 Fase 3: Remodelación (Flexibilidad)"
    }
    
    catalogo = [
        # --- REJUVENECIMIENTO FACIAL ---
        Tratamiento("face_rejuv", "Rejuvenecimiento Facial", "Cara/Cuello", "RED + NIR (Opcional)", "50-80%", "30-50 cm", 10, 1, 0, "PERMANENTE", ['All'], "FLEX", "Cualquier hora (Piel Limpia)",
                    tips_antes=["🧼 DOBLE LIMPIEZA: Piel 100% limpia.", "🕶️ GAFAS OBLIGATORIAS si usas NIR.", "🧴 Evitar Retinol justo antes."],
                    tips_despues=["🧴 APLICAR SERUM: Absorción x2.", "❌ NO sol directo inmediato.", "💧 Hidratar mucho."])
        .set_incompatibilidades("Melasma (Calor NIR puede empeorar). Medicamentos fotosensibles."),

        # --- GRASA ---
        Tratamiento("fat_front", "Abdomen Frontal (Grasa)", "Abdomen Frente", "NIR + RED", "100%", "10-15 cm", 10, 1, 0, "GRASA", ['Active'], "PRE", "Ideal: Antes de Entrenar",
                    tips_antes=["💧 Beber agua.", "🧴 Piel limpia."],
                    tips_despues=["🏃‍♂️ ENTRENA YA (<45 min).", "❌ Ayuno post-sesión 1h."])
        .set_incompatibilidades("Tatuajes oscuros. Embarazo."),
        
        Tratamiento("fat_d", "Flanco Derecho (Grasa)", "Abdomen Dcho", "NIR + RED", "100%", "10-15 cm", 10, 1, 0, "GRASA", ['Active'], "PRE", "Ideal: Antes de Entrenar",
                    tips_antes=["💧 Beber agua."],
                    tips_despues=["🏃‍♂️ ENTRENA YA.", "❌ Ayuno post-sesión 1h."])
        .set_incompatibilidades("Tatuajes oscuros."),
        
        Tratamiento("fat_i", "Flanco Izquierdo (Grasa)", "Abdomen Izq", "NIR + RED", "100%", "10-15 cm", 10, 1, 0, "GRASA", ['Active'], "PRE", "Ideal: Antes de Entrenar",
                    tips_antes=["💧 Beber agua."],
                    tips_despues=["🏃‍♂️ ENTRENA YA.", "❌ Ayuno post-sesión 1h."])
        .set_incompatibilidades("Tatuajes oscuros."),

        # --- LESIONES ---
        Tratamiento("rodilla_d", "Rodilla Derecha (Lesión)", "Rodilla Dcha", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], "FLEX", "Flexible",
                    tips_antes=["🧴 Piel limpia.", "❄️ NO hielo antes."],
                    tips_despues=["🦶 Movilidad suave.", "🚿 Ducha normal.", "🧊 Hielo OK si hay dolor."],
                    fases_info=fases_articulacion)
        .set_incompatibilidades("Implantes metálicos. Cáncer activo."),
        
        Tratamiento("rodilla_i", "Rodilla Izquierda (Lesión)", "Rodilla Izq", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], "FLEX", "Flexible",
                    tips_antes=["🧴 Piel limpia.", "❄️ NO hielo antes."],
                    tips_despues=["🦶 Movilidad suave.", "🚿 Ducha normal."],
                    fases_info=fases_articulacion)
        .set_incompatibilidades("Implantes metálicos. Cáncer activo."),
        
        Tratamiento("codo_d", "Codo Derecho (Lesión)", "Codo Dcho", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], "FLEX", "Flexible",
                    tips_antes=["🧴 Piel limpia."],
                    tips_despues=["🔄 Estiramiento suave.", "❌ No cargar peso."],
                    fases_info=fases_articulacion)
        .set_incompatibilidades("No usar si infiltración <5 días."),
        
        Tratamiento("codo_i", "Codo Izquierdo (Lesión)", "Codo Izq", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], "FLEX", "Flexible",
                    tips_antes=["🧴 Piel limpia."],
                    tips_despues=["🔄 Estiramiento suave.", "❌ No cargar peso."],
                    fases_info=fases_articulacion)
        .set_incompatibilidades("No usar si infiltración <5 días."),
        
        # --- MÚSCULO ---
        Tratamiento("arm_d", "Antebrazo Derecho (Recuperación)", "Antebrazo Dcho", "NIR + RED", "100%", "15-30 cm", 10, 1, 0, "MUSCULAR", ['Upper'], "POST", "Ideal: Después de Entrenar",
                    tips_antes=["🚿 Quitar sudor."],
                    tips_despues=["🥩 Proteína.", "🚿 Ducha contraste OK."])
        .set_incompatibilidades("Opcional: Pulsos 50Hz."),
        
        Tratamiento("arm_i", "Antebrazo Izquierdo (Recuperación)", "Antebrazo Izq", "NIR + RED", "100%", "15-30 cm", 10, 1, 0, "MUSCULAR", ['Upper'], "POST", "Ideal: Después de Entrenar",
                    tips_antes=["🚿 Quitar sudor."],
                    tips_despues=["🥩 Proteína.", "🚿 Ducha contraste OK."])
        .set_incompatibilidades("Opcional: Pulsos 50Hz."),
        
        # --- PERMANENTES ---
        Tratamiento("testo", "Boost Testosterona", "Testículos", "NIR + RED", "100%", "15-20 cm", 5, 1, 0, "PERMANENTE", ['All'], "MORNING", "Mañana (Al despertar)",
                    tips_antes=["🚿 Piel limpia.", "❄️ Zona fresca."],
                    tips_despues=["🚿 Ducha fría.", "❌ Ropa holgada."])
        .set_incompatibilidades("Varicocele."),
        
        Tratamiento("sleep", "Sueño y Ritmo", "Ambiente", "SOLO RED", "10-20%", "> 50 cm", 15, 1, 0, "PERMANENTE", ['All'], "NIGHT", "Noche (30 min antes dormir)",
                    tips_antes=["📵 Apagar pantallas.", "💡 Luces apagadas."],
                    tips_despues=["🛌 A DORMIR.", "❌ No pantallas."])
        .set_incompatibilidades("⛔ NO USAR PULSOS."),
        
        Tratamiento("brain", "Salud Cerebral", "Cabeza", "SOLO NIR", "100%", "30 cm", 10, 1, 0, "PERMANENTE", ['All'], "FLEX", "Mañana o Tarde (Con Gafas)",
                    tips_antes=["🕶️ GAFAS PUESTAS."],
                    tips_despues=["🧠 Tarea cognitiva.", "❌ NO DORMIR."])
        .set_incompatibilidades("⛔ GAFAS OBLIGATORIAS.")
    ]
    return catalogo

# --- GESTIÓN DE DATOS ---
def cargar_datos():
    if not os.path.exists(ARCHIVO_DATOS):
        return {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}
    try:
        with open(ARCHIVO_DATOS, 'r') as f:
            datos = json.load(f)
            if "descartados" not in datos: datos["descartados"] = {}
            return datos
    except:
        return {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}

def guardar_datos(datos):
    with open(ARCHIVO_DATOS, 'w') as f:
        json.dump(datos, f, indent=4)

# --- DETECCIÓN DE CONFLICTOS ---
def verificar_conflicto(tratamiento, momento_elegido, tratamientos_hechos_hoy):
    msg = ""
    conflicto = False

    # Conflictos de Hora
    if tratamiento.id == "brain" and momento_elegido == "🌙 Noche":
        return True, "⛔ PELIGRO: Usar NIR en la cabeza de noche suprime la melatonina. Hazlo de día."
    if tratamiento.id == "sleep" and momento_elegido != "🌙 Noche":
        return True, "⚠️ CUIDADO: El protocolo de Sueño induce relajación. No recomendado si vas a estar activo."
    if tratamiento.id == "face_rejuv" and momento_elegido == "🏋️ Antes de Entrenar":
        return True, "⚠️ SUBÓPTIMO: El sudor irritará la piel y perderás el efecto de los serums."
    if tratamiento.tipo == "GRASA" and momento_elegido == "🧘 Después de Entrenar":
        msg = "⚠️ RECUERDA: Si lo haces después, debes mantener actividad ligera para oxidar la grasa."

    # Conflictos de Combinación
    ids_hechos = list(tratamientos_hechos_hoy.keys())
    if tratamiento.id == "brain" and "sleep" in ids_hechos:
        return True, "⛔ CONTRADICTORIO: Ya has hecho Sueño. Activar el cerebro ahora romperá el descanso."

    return conflicto, msg

# --- INTERFAZ ---
st.title(f"🧠 Mega Panel AI")

if 'db' not in st.session_state:
    st.session_state.db = cargar_datos()

lista_tratamientos = obtener_catalogo()

# 1. FECHA
c_fecha, c_resumen = st.columns([2, 1])
with c_fecha:
    fecha_seleccionada = st.date_input("📅 Fecha de Registro", datetime.date.today())
    fecha_str = fecha_seleccionada.isoformat()

# 2. RUTINAS
entreno_guardado = st.session_state.db.get("meta_diaria", {}).get(fecha_str, [])
opciones_rutinas = {
    "Descanso Total": [],
    "Cardio Genérico": ["Active"],
    "FULLBODY I": ["Upper", "Active"],  
    "TORSO I": ["Upper", "Active"],     
    "PREVENTIVO I": ["Active"],         
    "FULLBODY II": ["Upper", "Active"], 
    "TORSO II / CIRCUITO": ["Upper", "Active"], 
    "PREVENTIVO II": ["Active"]         
}
nombres_rutinas = list(opciones_rutinas.keys())
default_options = [x for x in entreno_guardado if x in nombres_rutinas]
seleccion_rutinas = st.multiselect("Rutinas realizadas hoy:", nombres_rutinas, default=default_options)

tags_dia = set()
if seleccion_rutinas:
    for rutina in seleccion_rutinas:
        tags_dia.update(opciones_rutinas[rutina])

if seleccion_rutinas != entreno_guardado:
    if "meta_diaria" not in st.session_state.db: st.session_state.db["meta_diaria"] = {}
    st.session_state.db["meta_diaria"][fecha_str] = seleccion_rutinas
    guardar_datos(st.session_state.db)
    st.rerun()

st.divider()

# --- CLASIFICACIÓN ---
registros_dia = st.session_state.db["historial"].get(fecha_str, {})
descartados_dia = st.session_state.db.get("descartados", {}).get(fecha_str, [])

grupos = {
    "PRE": [], "POST": [], "MORNING": [], "AFTERNOON": [], "NIGHT": [],
    "FLEX": [], "COMPLETED": [], "HIDDEN": [], "DISCARDED": []
}

mapa_seleccion = {
    "🏋️ Antes de Entrenar": "PRE",
    "🧘 Después de Entrenar": "POST",
    "🌞 Mañana": "MORNING",
    "⛅ Tarde": "AFTERNOON",
    "🌙 Noche": "NIGHT"
}

# CONSEJOS GENERALES
ids_activos_hoy = []
for t in lista_tratamientos:
    activo = False
    if t.tipo == "PERMANENTE": activo = True
    elif t.tipo == "LESION" and st.session_state.db["ciclos_activos"].get(t.id, {}).get('activo'): activo = True
    elif t.tipo == "GRASA" and "Active" in tags_dia: activo = True
    elif t.tipo == "MUSCULAR" and "Upper" in tags_dia: activo = True
    
    if activo: ids_activos_hoy.append(t.id)

if "brain" in ids_activos_hoy and "sleep" in ids_activos_hoy:
    st.info("💡 **Consejo:** Separa mucho 'Salud Cerebral' (Mañana) y 'Sueño' (Noche).")

# LOOP PRINCIPAL
for t in lista_tratamientos:
    # Filtros
    aplica_hoy = False
    es_ciclo_activo = False
    if t.tipo == "LESION":
        ciclo = st.session_state.db["ciclos_activos"].get(t.id)
        if ciclo and ciclo['activo']: aplica_hoy = True; es_ciclo_activo = True
    elif t.tipo == "PERMANENTE": aplica_hoy = True
    elif t.tipo == "GRASA" and "Active" in tags_dia: aplica_hoy = True
    elif t.tipo == "MUSCULAR" and "Upper" in tags_dia: aplica_hoy = True

    sesiones_hechas = registros_dia.get(t.id, [])
    num_hechos = len(sesiones_hechas)
    esta_completo = num_hechos >= t.max_diario
    esta_descartado = t.id in descartados_dia

    if esta_descartado: grupos["DISCARDED"].append((t, es_ciclo_activo))
    elif not aplica_hoy: grupos["HIDDEN"].append((t, False))
    elif esta_completo: grupos["COMPLETED"].append((t, es_ciclo_activo))
    else:
        key_radio = f"rad_{t.id}"
        grupo_destino = t.default_visual_group
        
        # 1. Interacción en tiempo real
        if key_radio in st.session_state and st.session_state[key_radio] in mapa_seleccion:
            grupo_destino = mapa_seleccion[st.session_state[key_radio]]
        # 2. Historial previo
        elif num_hechos > 0:
            ultimo = sesiones_hechas[-1]['detalle']
            for k, v in mapa_seleccion.items():
                if k in ultimo or v in ultimo: grupo_destino = v; break
        
        if grupo_destino in grupos: grupos[grupo_destino].append((t, es_ciclo_activo))
        else: grupos["FLEX"].append((t, es_ciclo_activo))

# --- RENDERIZADO ---
def render_tratamiento(t, es_ciclo_activo, modo="normal"):
    info_fase = ""
    bloqueado_por_fin = False
    if t.tipo == "LESION" and es_ciclo_activo:
        ciclo = st.session_state.db["ciclos_activos"].get(t.id)
        start = datetime.date.fromisoformat(ciclo['fecha_inicio'])
        dias_trans = (fecha_seleccionada - start).days
        if dias_trans > 60: info_fase = "🏁 Ciclo Completado"; bloqueado_por_fin = True
        else:
            fase_txt = "Mantenimiento"
            for lim, txt in sorted(t.fases_info.items()):
                if dias_trans <= lim: fase_txt = txt; break
            info_fase = f"🗓️ Día {dias_trans}: {fase_txt}"

    sesiones_hechas = registros_dia.get(t.id, [])
    num_hechos = len(sesiones_hechas)
    completo = num_hechos >= t.max_diario
    
    icono = "❌" if modo == "discarded" else ("✅" if completo else "⬜")
    titulo = f"{icono} {t.nombre} ({num_hechos}/{t.max_diario})"
    
    with st.expander(titulo):
        if info_fase: st.info(info_fase)
        
        if modo == "discarded":
            st.caption("Tratamiento omitido.")
            if st.button("↩️ Recuperar", key=f"rec_{t.id}"):
                if fecha_str in st.session_state.db["descartados"]:
                    st.session_state.db["descartados"][fecha_str].remove(t.id)
                    guardar_datos(st.session_state.db)
                    st.rerun()
            return

        if modo != "readonly":
            st.caption(f"📍 Sugerido: {t.momento_ideal_txt}")
            
            c1, c2 = st.columns(2)
            c1.markdown(f"**Zona:** {t.zona}\n\n**Ondas:** {t.ondas}")
            c2.markdown(f"**Distancia:** {t.distancia}\n\n**Tiempo:** {t.duracion} min")
            
            st.markdown("---")
            ca, cb = st.columns(2)
            ca.markdown("**🏁 ANTES**"); [ca.caption(f"• {x}") for x in t.tips_antes]
            cb.markdown("**🏁 DESPUÉS**"); [cb.caption(f"• {x}") for x in t.tips_despues]
            
            if t.incompatibilidades: st.warning(f"⚠️ {t.incompatibilidades}")

        # Historial y Borrado
        if num_hechos > 0:
            st.markdown("---")
            for i, reg in enumerate(sesiones_hechas):
                ct, cd = st.columns([5,1])
                ct.success(f"✅ {reg['hora']} - {reg['detalle']}")
                if cd.button("🗑️", key=f"del_{t.id}_{i}_{modo}"):
                    registros_dia[t.id].pop(i)
                    if not registros_dia[t.id]: del registros_dia[t.id]
                    guardar_datos(st.session_state.db)
                    st.rerun()

        # Registro
        if modo == "normal" and not completo and not bloqueado_por_fin:
            st.markdown("---")
            
            # Selector de Momento
            opciones = ["🏋️ Antes de Entrenar", "🧘 Después de Entrenar", "🌞 Mañana", "⛅ Tarde", "🌙 Noche"]
            if t.id == "face_rejuv": opciones = ["🌞 Mañana", "⛅ Tarde", "🌙 Noche", "🏋️ Antes de Entrenar"]
            
            seleccion = st.radio("Momento:", opciones, key=f"rad_{t.id}")
            
            # VERIFICAR CONFLICTOS
            hay_conflicto, msg_conflicto = verificar_conflicto(t, seleccion, registros_dia)
            permitir_guardar = True
            
            if hay_conflicto:
                st.error(msg_conflicto)
                if not st.checkbox("Entiendo el riesgo, confirmar.", key=f"conf_{t.id}"):
                    permitir_guardar = False
            elif msg_conflicto:
                st.warning(msg_conflicto)

            c_reg, c_disc = st.columns([3, 1])
            with c_reg:
                if permitir_guardar:
                    if st.button(f"Registrar Sesión {num_hechos+1}", key=f"btn_{t.id}"):
                        ahora = datetime.datetime.now().strftime('%H:%M')
                        if "historial" not in st.session_state.db: st.session_state.db["historial"] = {}
                        if fecha_str not in st.session_state.db["historial"]: st.session_state.db["historial"][fecha_str] = {}
                        if t.id not in st.session_state.db["historial"][fecha_str]: st.session_state.db["historial"][fecha_str][t.id] = []
                        
                        st.session_state.db["historial"][fecha_str][t.id].append({"hora": ahora, "detalle": seleccion})
                        guardar_datos(st.session_state.db)
                        st.rerun()
                else:
                    st.button("🚫 Bloqueado", disabled=True, key=f"blk_{t.id}")
            
            with c_disc:
                if st.button("🚫 Omitir", key=f"omit_{t.id}"):
                    if "descartados" not in st.session_state.db: st.session_state.db["descartados"] = {}
                    if fecha_str not in st.session_state.db["descartados"]: st.session_state.db["descartados"][fecha_str] = []
                    if t.id not in st.session_state.db["descartados"][fecha_str]:
                        st.session_state.db["descartados"][fecha_str].append(t.id)
                        guardar_datos(st.session_state.db)
                        st.rerun()
        
        if t.tipo == "LESION" and bloqueado_por_fin:
            if st.button("🔄 Reiniciar Ciclo", key=f"rst_{t.id}"):
                 st.session_state.db["ciclos_activos"][t.id] = {"fecha_inicio": fecha_str, "activo": True}
                 guardar_datos(st.session_state.db)
                 st.rerun()

# --- SECCIONES ---
sections_order = [
    ("MORNING", "🌞 Rutinas de Mañana"),
    ("PRE", "🔥 Antes de Entrenar"),
    ("POST", "🧘 Después de Entrenar"),
    ("AFTERNOON", "⛅ Rutinas de Tarde"),
    ("NIGHT", "🌙 Rutinas de Noche"),
    ("FLEX", "⚖️ Flexible / Sin Asignar")
]

st.subheader("📋 Plan del Día")
for k, t in sections_order:
    if grupos[k]:
        st.markdown(f"### {t}")
        for tr, act in grupos[k]: render_tratamiento(tr, act, "normal")

if grupos["COMPLETED"]:
    st.markdown("### ✅ Completados")
    for tr, act in grupos["COMPLETED"]: render_tratamiento(tr, act, "readonly")

if grupos["DISCARDED"]:
    st.markdown("### ❌ Descartados")
    for tr, act in grupos["DISCARDED"]: render_tratamiento(tr, act, "discarded")

if grupos["HIDDEN"]:
    st.markdown("---")
    with st.expander("📂 Inactivos"):
        for tr, _ in grupos["HIDDEN"]:
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{tr.nombre}**")
            if tr.tipo == "LESION":
                if c2.button("Activar", key=f"act_{tr.id}"):
                    st.session_state.db["ciclos_activos"][tr.id] = {"fecha_inicio": fecha_str, "activo": True}
                    guardar_datos(st.session_state.db)
                    st.rerun()
            else: c2.caption("-")
