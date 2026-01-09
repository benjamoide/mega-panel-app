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
    def __init__(self, id_t, nombre, zona, ondas, intensidad, distancia, duracion, max_diario, tiempo_espera_horas, tipo, tags_entreno, default_visual_group, momento_ideal_txt, fases_info=None):
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
    
    catalogo = [
        # --- GRASA ---
        Tratamiento("fat_front", "Abdomen Frontal (Grasa)", "Abdomen Frente", "NIR + RED", "100%", "10-15 cm", 10, 1, 0, "GRASA", ['Active'], "PRE", "Ideal: Antes de Entrenar")
        .set_incompatibilidades("Tatuajes oscuros. Embarazo prohibido."),
        
        Tratamiento("fat_d", "Flanco Derecho (Grasa)", "Abdomen Dcho", "NIR + RED", "100%", "10-15 cm", 10, 1, 0, "GRASA", ['Active'], "PRE", "Ideal: Antes de Entrenar")
        .set_incompatibilidades("Tatuajes oscuros. Embarazo prohibido."),
        
        Tratamiento("fat_i", "Flanco Izquierdo (Grasa)", "Abdomen Izq", "NIR + RED", "100%", "10-15 cm", 10, 1, 0, "GRASA", ['Active'], "PRE", "Ideal: Antes de Entrenar")
        .set_incompatibilidades("Tatuajes oscuros. Embarazo prohibido."),

        # --- LESIONES ---
        Tratamiento("rodilla_d", "Rodilla Derecha (Lesión)", "Rodilla Dcha", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], "FLEX", "Flexible: Antes o Después", fases_articulacion)
        .set_incompatibilidades("Implantes metálicos, Cáncer activo."),
        
        Tratamiento("rodilla_i", "Rodilla Izquierda (Lesión)", "Rodilla Izq", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], "FLEX", "Flexible: Antes o Después", fases_articulacion)
        .set_incompatibilidades("Implantes metálicos, Cáncer activo."),
        
        Tratamiento("codo_d", "Codo Derecho (Lesión)", "Codo Dcho", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], "FLEX", "Flexible: Antes o Después", fases_articulacion)
        .set_incompatibilidades("No usar si infiltración <5 días."),
        
        Tratamiento("codo_i", "Codo Izquierdo (Lesión)", "Codo Izq", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], "FLEX", "Flexible: Antes o Después", fases_articulacion)
        .set_incompatibilidades("No usar si infiltración <5 días."),
        
        # --- MÚSCULO ---
        Tratamiento("arm_d", "Antebrazo Derecho (Recuperación)", "Antebrazo Dcho", "NIR + RED", "100%", "15-30 cm", 10, 1, 0, "MUSCULAR", ['Upper'], "POST", "Ideal: Después de Entrenar")
        .set_incompatibilidades("Opcional: Pulsos 50Hz."),
        
        Tratamiento("arm_i", "Antebrazo Izquierdo (Recuperación)", "Antebrazo Izq", "NIR + RED", "100%", "15-30 cm", 10, 1, 0, "MUSCULAR", ['Upper'], "POST", "Ideal: Después de Entrenar")
        .set_incompatibilidades("Opcional: Pulsos 50Hz."),
        
        # --- PERMANENTES ---
        Tratamiento("testo", "Boost Testosterona", "Testículos", "NIR + RED", "100%", "15-20 cm", 5, 1, 0, "PERMANENTE", ['All'], "MORNING", "Mañana (Al despertar)")
        .set_incompatibilidades("No exceder tiempo. Varicocele."),
        
        Tratamiento("sleep", "Sueño y Ritmo", "Ambiente", "SOLO RED", "10-20%", "> 50 cm", 15, 1, 0, "PERMANENTE", ['All'], "NIGHT", "Noche (30 min antes dormir)")
        .set_incompatibilidades("⛔ NO USAR PULSOS."),
        
        Tratamiento("brain", "Salud Cerebral", "Cabeza", "SOLO NIR", "100%", "30 cm", 10, 1, 0, "PERMANENTE", ['All'], "FLEX", "Mañana o Tarde (Con Gafas)")
        .set_incompatibilidades("⛔ GAFAS OBLIGATORIAS. Evitar muy tarde.")
    ]
    return catalogo

# --- GESTIÓN DE DATOS ---
def cargar_datos():
    if not os.path.exists(ARCHIVO_DATOS):
        # Estructura: historial, meta_diaria, ciclos_activos, descartados
        return {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}
    try:
        with open(ARCHIVO_DATOS, 'r') as f:
            datos = json.load(f)
            # Asegurar compatibilidad
            if "descartados" not in datos: datos["descartados"] = {}
            return datos
    except:
        return {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}

def guardar_datos(datos):
    with open(ARCHIVO_DATOS, 'w') as f:
        json.dump(datos, f, indent=4)

# --- INTERFAZ PRINCIPAL ---
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

# --- INTELIGENCIA DE COMBINACIONES ---
tratamientos_activos_ids = []
registros_dia = st.session_state.db["historial"].get(fecha_str, {})
descartados_dia = st.session_state.db.get("descartados", {}).get(fecha_str, [])

for t in lista_tratamientos:
    activo = False
    if t.tipo == "PERMANENTE": activo = True
    elif t.tipo == "LESION" and st.session_state.db["ciclos_activos"].get(t.id, {}).get('activo'): activo = True
    elif t.tipo == "GRASA" and "Active" in tags_dia: activo = True
    elif t.tipo == "MUSCULAR" and "Upper" in tags_dia: activo = True
    
    if activo and t.id not in descartados_dia: # Solo cuenta si no está descartado
        tratamientos_activos_ids.append(t.id)

if "brain" in tratamientos_activos_ids and "sleep" in tratamientos_activos_ids:
    st.info("💡 **Consejo:** Separa 'Salud Cerebral' (Mañana) y 'Sueño' (Noche).")
if "fat_d" in tratamientos_activos_ids and "fat_front" in tratamientos_activos_ids:
    st.info("💡 **Consejo Fat Loss:** Alterna zonas antes y después del entreno.")

st.subheader(f"📋 Tu Plan del Día")

# --- CLASIFICACIÓN DINÁMICA ---
grupos = {
    "PRE": [],       
    "POST": [],      
    "MORNING": [],   
    "AFTERNOON": [], 
    "NIGHT": [],     
    "FLEX": [],      
    "COMPLETED": [], 
    "HIDDEN": [],
    "DISCARDED": [] # Nuevo grupo para papelera
}

mapa_seleccion = {
    "🏋️ Antes de Entrenar": "PRE",
    "🧘 Después de Entrenar": "POST",
    "🌞 Mañana": "MORNING",
    "⛅ Tarde": "AFTERNOON",
    "🌙 Noche": "NIGHT"
}

for t in lista_tratamientos:
    # 1. Filtros de validez
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
    esta_descartado = t.id in descartados_dia

    # 3. Clasificación
    if esta_descartado:
        grupos["DISCARDED"].append((t, es_ciclo_activo))
    elif not aplica_hoy:
        grupos["HIDDEN"].append((t, False))
    elif esta_completo:
        grupos["COMPLETED"].append((t, es_ciclo_activo))
    else:
        # Lógica de movimiento en tiempo real
        key_radio = f"rad_{t.id}"
        grupo_destino = t.default_visual_group
        
        # Prioridad 1: Interacción
        if key_radio in st.session_state:
            seleccion_actual = st.session_state[key_radio]
            if seleccion_actual in mapa_seleccion:
                grupo_destino = mapa_seleccion[seleccion_actual]
        # Prioridad 2: Historial
        elif num_hechos > 0:
            ultimo = sesiones_hechas[-1]['detalle']
            if "Antes" in ultimo: grupo_destino = "PRE"
            elif "Después" in ultimo: grupo_destino = "POST"
            elif "Mañana" in ultimo: grupo_destino = "MORNING"
            elif "Noche" in ultimo: grupo_destino = "NIGHT"
        
        if grupo_destino in grupos:
            grupos[grupo_destino].append((t, es_ciclo_activo))
        else:
            grupos["FLEX"].append((t, es_ciclo_activo))

# --- RENDERIZADO ---
def render_tratamiento(t, es_ciclo_activo, modo="normal"):
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
    
    # Iconos según modo
    if modo == "discarded":
        icono = "❌"
        estado_txt = "(Descartado)"
    elif completo:
        icono = "✅"
        estado_txt = "(Completado)"
    else:
        icono = "⏳" if num_hechos > 0 else "⬜"
        estado_txt = f"({num_hechos}/{t.max_diario})"

    titulo = f"{icono} {t.nombre} {estado_txt}"
    
    with st.expander(titulo):
        if info_fase: st.info(info_fase)
        
        # Si está descartado, mostrar botón de recuperar
        if modo == "discarded":
            st.caption("Este tratamiento ha sido omitido hoy.")
            if st.button("↩️ Recuperar y Realizar", key=f"rest_{t.id}"):
                if fecha_str in st.session_state.db["descartados"]:
                    if t.id in st.session_state.db["descartados"][fecha_str]:
                        st.session_state.db["descartados"][fecha_str].remove(t.id)
                        guardar_datos(st.session_state.db)
                        st.rerun()
            return # Salimos, no mostramos el resto de opciones

        # MODO NORMAL / COMPLETADO
        if modo != "readonly":
            st.caption(f"📍 Sugerido: {t.momento_ideal_txt}")
            c1, c2 = st.columns(2)
            c1.markdown(f"**Zona:** {t.zona}\n\n**Ondas:** {t.ondas}")
            c2.markdown(f"**Distancia:** {t.distancia}\n\n**Tiempo:** {t.duracion} min")
            if t.incompatibilidades: st.warning(f"⚠️ {t.incompatibilidades}")

        # Historial y Borrado de Sesiones
        if num_hechos > 0:
            st.markdown("---")
            for i, reg in enumerate(sesiones_hechas):
                col_txt, col_del = st.columns([5, 1])
                with col_txt:
                    st.success(f"✅ {reg['hora']} - {reg['detalle']}")
                with col_del:
                    if st.button("🗑️", key=f"del_{t.id}_{i}_{modo}"):
                        registros_dia[t.id].pop(i)
                        if not registros_dia[t.id]: del registros_dia[t.id]
                        guardar_datos(st.session_state.db)
                        st.rerun()

        # Registro de Nueva Sesión
        if modo == "normal" and not completo and not bloqueado_por_fin:
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
                permitir = True
                
                # Selector Momento
                opciones = []
                if t.tipo == "PERMANENTE" and "Testosterona" in t.nombre:
                    opciones = ["🌞 Mañana", "⛅ Tarde"]
                elif t.tipo == "PERMANENTE" and "Sueño" in t.nombre:
                    opciones = ["🌙 Noche"]
                else:
                    opciones = ["🏋️ Antes de Entrenar", "🧘 Después de Entrenar", "🌞 Mañana", "⛅ Tarde", "🌙 Noche"]
                
                detalle_sel = st.radio("¿Cuándo?", options=opciones, key=f"rad_{t.id}")
                
                if t.tipo == "GRASA" and "Después" in detalle_sel:
                    st.warning("⚠️ Recuerda moverte un poco después.")

                # BOTONES DE ACCIÓN: REGISTRAR O DESCARTAR
                c_reg, c_discard = st.columns([3, 1])
                
                with c_reg:
                    if st.button(f"Registrar Sesión {num_hechos+1}", key=f"btn_{t.id}"):
                        ahora = datetime.datetime.now().strftime('%H:%M')
                        if "historial" not in st.session_state.db: st.session_state.db["historial"] = {}
                        if fecha_str not in st.session_state.db["historial"]: st.session_state.db["historial"][fecha_str] = {}
                        if t.id not in st.session_state.db["historial"][fecha_str]: st.session_state.db["historial"][fecha_str][t.id] = []
                        
                        st.session_state.db["historial"][fecha_str][t.id].append({"hora": ahora, "detalle": detalle_sel})
                        guardar_datos(st.session_state.db)
                        st.rerun()
                
                with c_discard:
                    # Botón para descartar
                    if st.button("🚫 Omitir", key=f"disc_{t.id}", help="Mover a descartados por hoy"):
                        if "descartados" not in st.session_state.db: st.session_state.db["descartados"] = {}
                        if fecha_str not in st.session_state.db["descartados"]: st.session_state.db["descartados"][fecha_str] = []
                        
                        if t.id not in st.session_state.db["descartados"][fecha_str]:
                            st.session_state.db["descartados"][fecha_str].append(t.id)
                            guardar_datos(st.session_state.db)
                            st.rerun()

        # Reinicio Ciclo
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

for key, title in sections_order:
    if grupos[key]:
        st.markdown(f"### {title}")
        for t, ciclo in grupos[key]:
            render_tratamiento(t, ciclo, modo="normal")

if grupos["COMPLETED"]:
    st.markdown("### ✅ Completados Hoy")
    for t, ciclo in grupos["COMPLETED"]: render_tratamiento(t, ciclo, modo="readonly")

# SECCIÓN DE DESCARTADOS (NUEVA)
if grupos["DISCARDED"]:
    st.markdown("### ❌ Tratamientos Descartados")
    for t, ciclo in grupos["DISCARDED"]: render_tratamiento(t, ciclo, modo="discarded")

if grupos["HIDDEN"]:
    st.markdown("---")
    with st.expander("📂 Tratamientos Inactivos"):
        for t, _ in grupos["HIDDEN"]:
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{t.nombre}**")
            if t.tipo == "LESION":
                if c2.button("Activar", key=f"act_{t.id}"):
                    st.session_state.db["ciclos_activos"][t.id] = {"fecha_inicio": fecha_str, "activo": True}
                    guardar_datos(st.session_state.db)
                    st.rerun()
            else:
                c2.caption("Descanso")
