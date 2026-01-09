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
    def __init__(self, id_t, nombre, zona, ondas, intensidad, distancia, duracion, max_diario, tiempo_espera_horas, tipo, tags_entreno, momentos_visuales_default, momento_ideal_txt, fases_info=None):
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
        self.momentos_visuales_default = momentos_visuales_default # Dónde aparece por defecto
        self.momento_ideal_txt = momento_ideal_txt 
        self.incompatibilidades = "" 
        self.fases_info = fases_info if fases_info else {}

    def set_incompatibilidades(self, texto):
        self.incompatibilidades = texto
        return self

# --- CATÁLOGO ---
@st.cache_data
def obtener_catalogo():
    fases_articulacion = {
        7: "🔥 Fase 1: Aguda (Bajar dolor)",
        21: "🛠️ Fase 2: Proliferación (Generar tejido)",
        60: "🧱 Fase 3: Remodelación (Flexibilidad)"
    }
    
    # MOMENTOS VISUALES: "PRE", "POST", "FLEX" (Flexible), "MORNING", "NIGHT", "ANY"
    
    catalogo = [
        # --- GRASA ---
        Tratamiento("fat_d", "Flanco Derecho (Grasa)", "Abdomen Dcho", "NIR + RED", "100%", "10-15 cm", 10, 1, 0, "GRASA", ['Active'], ["PRE"], "OBLIGATORIO: Antes de Entrenar")
        .set_incompatibilidades("Tatuajes oscuros. Embarazo prohibido."),
        
        Tratamiento("fat_i", "Flanco Izquierdo (Grasa)", "Abdomen Izq", "NIR + RED", "100%", "10-15 cm", 10, 1, 0, "GRASA", ['Active'], ["PRE"], "OBLIGATORIO: Antes de Entrenar")
        .set_incompatibilidades("Tatuajes oscuros. Embarazo prohibido."),

        # --- LESIONES (Por defecto en FLEXIBLE, pero se moverán si eliges Pre/Post) ---
        Tratamiento("rodilla_d", "Rodilla Derecha (Lesión)", "Rodilla Dcha", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], ["FLEX"], "Flexible: Antes o Después", fases_articulacion)
        .set_incompatibilidades("Implantes metálicos, Cáncer activo."),
        
        Tratamiento("rodilla_i", "Rodilla Izquierda (Lesión)", "Rodilla Izq", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], ["FLEX"], "Flexible: Antes o Después", fases_articulacion)
        .set_incompatibilidades("Implantes metálicos, Cáncer activo."),
        
        Tratamiento("codo_d", "Codo Derecho (Lesión)", "Codo Dcho", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], ["FLEX"], "Flexible: Antes o Después", fases_articulacion)
        .set_incompatibilidades("No usar si infiltración <5 días."),
        
        Tratamiento("codo_i", "Codo Izquierdo (Lesión)", "Codo Izq", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], ["FLEX"], "Flexible: Antes o Después", fases_articulacion)
        .set_incompatibilidades("No usar si infiltración <5 días."),
        
        # --- MÚSCULO ---
        Tratamiento("arm_d", "Antebrazo Derecho (Recuperación)", "Antebrazo Dcho", "NIR + RED", "100%", "15-30 cm", 10, 1, 0, "MUSCULAR", ['Upper'], ["POST"], "Ideal: Después de Entrenar")
        .set_incompatibilidades("Opcional: Pulsos 50Hz."),
        
        Tratamiento("arm_i", "Antebrazo Izquierdo (Recuperación)", "Antebrazo Izq", "NIR + RED", "100%", "15-30 cm", 10, 1, 0, "MUSCULAR", ['Upper'], ["POST"], "Ideal: Después de Entrenar")
        .set_incompatibilidades("Opcional: Pulsos 50Hz."),
        
        # --- RUTINAS ---
        Tratamiento("testo", "Boost Testosterona", "Testículos", "NIR + RED", "100%", "15-20 cm", 5, 1, 0, "PERMANENTE", ['All'], ["MORNING"], "Mañana (Al despertar)")
        .set_incompatibilidades("No exceder tiempo. Varicocele."),
        
        Tratamiento("sleep", "Sueño y Ritmo", "Ambiente", "SOLO RED", "10-20%", "> 50 cm", 15, 1, 0, "PERMANENTE", ['All'], ["NIGHT"], "Noche (30 min antes dormir)")
        .set_incompatibilidades("⛔ NO USAR PULSOS."),
        
        Tratamiento("brain", "Salud Cerebral", "Cabeza", "SOLO NIR", "100%", "30 cm", 10, 1, 0, "PERMANENTE", ['All'], ["ANY"], "Cualquier hora (Con Gafas)")
        .set_incompatibilidades("⛔ GAFAS OBLIGATORIAS.")
    ]
    return catalogo

# --- GESTIÓN DE DATOS ---
def cargar_datos():
    if not os.path.exists(ARCHIVO_DATOS):
        return {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}}
    try:
        with open(ARCHIVO_DATOS, 'r') as f:
            return json.load(f)
    except:
        return {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}}

def guardar_datos(datos):
    with open(ARCHIVO_DATOS, 'w') as f:
        json.dump(datos, f, indent=4)

# --- INTERFAZ PRINCIPAL ---
st.title(f"🧠 Mega Panel AI")

if 'db' not in st.session_state:
    st.session_state.db = cargar_datos()

lista_tratamientos = obtener_catalogo()

# 1. SELECCIÓN DE FECHA
c_fecha, c_resumen = st.columns([2, 1])
with c_fecha:
    fecha_seleccionada = st.date_input("📅 Fecha de Registro", datetime.date.today())
    fecha_str = fecha_seleccionada.isoformat()

# 2. SELECCIÓN DE ENTRENAMIENTO
entreno_guardado = st.session_state.db.get("meta_diaria", {}).get(fecha_str, [])
st.info("🏋️ **¿Qué rutinas tocan hoy?**")

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

seleccion_rutinas = st.multiselect("Rutinas realizadas:", nombres_rutinas, default=default_options)

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

# --- LÓGICA DE CLASIFICACIÓN DINÁMICA ---
st.subheader(f"📋 Tu Plan del Día")

registros_dia = st.session_state.db["historial"].get(fecha_str, {})

# Grupos visuales
grupos_visuales = {
    "PRE": [],
    "FLEX": [],
    "POST": [],
    "MORNING": [],
    "NIGHT": [],
    "ANY": [],
    "COMPLETED": [],
    "HIDDEN": []
}

for t in lista_tratamientos:
    
    # 1. ¿Aplica hoy?
    aplica_hoy = False
    es_ciclo_activo = False
    
    if t.tipo == "LESION":
        ciclo = st.session_state.db["ciclos_activos"].get(t.id)
        if ciclo and ciclo['activo']:
            aplica_hoy = True
            es_ciclo_activo = True
    elif t.tipo == "PERMANENTE":
        aplica_hoy = True
    elif t.tipo == "GRASA":
        if "Active" in tags_dia: aplica_hoy = True
    elif t.tipo == "MUSCULAR":
        if "Upper" in tags_dia: aplica_hoy = True

    # 2. Estado
    sesiones_hechas = registros_dia.get(t.id, [])
    num_hechos = len(sesiones_hechas)
    esta_completo = num_hechos >= t.max_diario

    # 3. CLASIFICACIÓN DINÁMICA
    if not aplica_hoy:
        grupos_visuales["HIDDEN"].append((t, False))
    elif esta_completo:
        grupos_visuales["COMPLETED"].append((t, es_ciclo_activo))
    else:
        # LÓGICA CLAVE: Si ya hay registros, ver qué eligió el usuario
        destino_final = t.momentos_visuales_default # Por defecto (lista)
        
        if num_hechos > 0:
            ultimo_detalle = sesiones_hechas[-1]['detalle']
            # Detectar palabras clave para reubicar la tarjeta
            if "Antes" in ultimo_detalle or "Pre-Entreno" in ultimo_detalle:
                destino_final = ["PRE"]
            elif "Después" in ultimo_detalle or "Post" in ultimo_detalle:
                destino_final = ["POST"]
            elif "Mañana" in ultimo_detalle:
                destino_final = ["MORNING"]
            elif "Noche" in ultimo_detalle:
                destino_final = ["NIGHT"]
        
        # Asignar a los grupos correspondientes
        for grupo in destino_final:
            grupos_visuales[grupo].append((t, es_ciclo_activo))

# --- RENDERIZADO ---

def render_tratamiento(t, es_ciclo_activo, es_solo_lectura=False):
    # Info Fase
    info_fase = ""
    bloqueado_por_fin = False
    if t.tipo == "LESION" and es_ciclo_activo:
        ciclo = st.session_state.db["ciclos_activos"].get(t.id)
        start = datetime.date.fromisoformat(ciclo['fecha_inicio'])
        dias_trans = (fecha_seleccionada - start).days
        if dias_trans > 60:
            info_fase = "🏁 Ciclo Completado"
            bloqueado_por_fin = True
        else:
            fase_txt = "Mantenimiento"
            for lim, txt in sorted(t.fases_info.items()):
                if dias_trans <= lim:
                    fase_txt = txt
                    break
            info_fase = f"🗓️ Día {dias_trans}: {fase_txt}"

    sesiones_hechas = registros_dia.get(t.id, [])
    num_hechos = len(sesiones_hechas)
    completo = num_hechos >= t.max_diario
    
    icono = "✅" if completo else ("⏳" if num_hechos > 0 else "⬜")
    titulo = f"{icono} {t.nombre} ({num_hechos}/{t.max_diario})"
    
    with st.expander(titulo):
        if info_fase: st.info(info_fase)
        if not es_solo_lectura:
            st.caption(f"📍 Recomendado: {t.momento_ideal_txt}")
            # Mostrar si ha sido movido dinámicamente
            if num_hechos > 0 and not completo:
                st.caption(f"📌 *Ubicado aquí por tu última sesión: {sesiones_hechas[-1]['detalle']}*")

            c1, c2 = st.columns(2)
            c1.markdown(f"**Zona:** {t.zona}\n\n**Ondas:** {t.ondas}")
            c2.markdown(f"**Distancia:** {t.distancia}\n\n**Tiempo:** {t.duracion} min")
            if t.incompatibilidades: st.warning(f"⚠️ {t.incompatibilidades}")

        # HISTORIAL
        if num_hechos > 0:
            st.markdown("---")
            for i, reg in enumerate(sesiones_hechas):
                col_txt, col_del = st.columns([5, 1])
                with col_txt:
                    st.success(f"✅ {reg['hora']} - {reg['detalle']}")
                with col_del:
                    if st.button("🗑️", key=f"del_{t.id}_{i}_read{es_solo_lectura}"):
                        registros_dia[t.id].pop(i)
                        if not registros_dia[t.id]: del registros_dia[t.id]
                        guardar_datos(st.session_state.db)
                        st.rerun()

        # REGISTRO
        if not es_solo_lectura and not completo and not bloqueado_por_fin:
            # Validar 6h
            bloqueado_tiempo = False
            if num_hechos > 0 and t.tiempo_espera_horas > 0 and fecha_seleccionada == datetime.date.today():
                last = datetime.datetime.strptime(sesiones_hechas[-1]['hora'], "%H:%M").time()
                now = datetime.datetime.now().time()
                diff = now.hour - last.hour + (now.minute - last.minute)/60
                if diff < t.tiempo_espera_horas:
                    st.error(f"⏳ Espera {round(t.tiempo_espera_horas - diff, 1)}h más.")
                    bloqueado_tiempo = True
            
            if not bloqueado_tiempo:
                st.markdown("---")
                detalle_sel = "Estándar"
                permitir = True
                
                # PREGUNTAS
                if t.tipo in ["LESION", "MUSCULAR"] and seleccion_rutinas:
                    detalle_sel = st.radio("Momento:", ["Antes de Entrenar", "Después de Entrenar", "Otro"], horizontal=True, key=f"rad_{t.id}")
                elif t.tipo == "GRASA":
                    st.write("🔥 **Requisito:** Entrenar YA.")
                    if not st.checkbox("Confirmo", key=f"c_{t.id}"): permitir = False
                    detalle_sel = "Pre-Entreno"
                elif t.tipo == "PERMANENTE":
                    detalle_sel = t.momento_ideal_txt.split("(")[0].strip()

                if permitir:
                    if st.button(f"Registrar Sesión {num_hechos+1}", key=f"btn_{t.id}"):
                        ahora = datetime.datetime.now().strftime('%H:%M')
                        if "historial" not in st.session_state.db: st.session_state.db["historial"] = {}
                        if fecha_str not in st.session_state.db["historial"]: st.session_state.db["historial"][fecha_str] = {}
                        if t.id not in st.session_state.db["historial"][fecha_str]: st.session_state.db["historial"][fecha_str][t.id] = []
                        
                        st.session_state.db["historial"][fecha_str][t.id].append({"hora": ahora, "detalle": detalle_sel})
                        guardar_datos(st.session_state.db)
                        st.rerun()
        
        # REINICIO
        if t.tipo == "LESION" and bloqueado_por_fin:
            if st.button("🔄 Reiniciar Ciclo", key=f"rst_{t.id}"):
                 st.session_state.db["ciclos_activos"][t.id] = {"fecha_inicio": fecha_str, "activo": True}
                 guardar_datos(st.session_state.db)
                 st.rerun()

# --- SECCIONES VISUALES ---

if grupos_visuales["PRE"]:
    st.markdown("### 🔥 Antes de Entrenar")
    for t, ciclo in grupos_visuales["PRE"]: render_tratamiento(t, ciclo)

if grupos_visuales["FLEX"]:
    st.markdown("### ⚖️ Flexible / Pendiente de Elección")
    for t, ciclo in grupos_visuales["FLEX"]: render_tratamiento(t, ciclo)

if grupos_visuales["POST"]:
    st.markdown("### 🧘 Después de Entrenar")
    for t, ciclo in grupos_visuales["POST"]: render_tratamiento(t, ciclo)

if grupos_visuales["MORNING"] or grupos_visuales["NIGHT"] or grupos_visuales["ANY"]:
    st.markdown("### 📅 Rutinas Diarias")
    if grupos_visuales["MORNING"]:
        st.caption("🌞 Mañana")
        for t, ciclo in grupos_visuales["MORNING"]: render_tratamiento(t, ciclo)
    if grupos_visuales["NIGHT"]:
        st.caption("🌙 Noche")
        for t, ciclo in grupos_visuales["NIGHT"]: render_tratamiento(t, ciclo)
    if grupos_visuales["ANY"]:
        st.caption("⚡ Cualquier Hora")
        for t, ciclo in grupos_visuales["ANY"]: render_tratamiento(t, ciclo)

if grupos_visuales["COMPLETED"]:
    st.markdown("### ✅ Completados Hoy")
    for t, ciclo in grupos_visuales["COMPLETED"]: render_tratamiento(t, ciclo, es_solo_lectura=True)

if grupos_visuales["HIDDEN"]:
    st.markdown("---")
    with st.expander("📂 Tratamientos Inactivos / No Prioritarios"):
        for t, _ in grupos_visuales["HIDDEN"]:
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{t.nombre}**")
            if t.tipo == "LESION":
                if c2.button("Activar", key=f"act_{t.id}"):
                    st.session_state.db["ciclos_activos"][t.id] = {"fecha_inicio": fecha_str, "activo": True}
                    guardar_datos(st.session_state.db)
                    st.rerun()
            else:
                c2.caption("Descanso")
