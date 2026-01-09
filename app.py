import streamlit as st
import datetime
import json
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Mega Panel AI",
    page_icon="🤖",
    layout="centered"
)

# --- ARCHIVO DE DATOS ---
ARCHIVO_DATOS = 'historial_mega_panel_final.json'

# --- CLASE DE TRATAMIENTO (ACTUALIZADA) ---
class Tratamiento:
    def __init__(self, id_t, nombre, zona, ondas, intensidad, distancia, duracion, max_diario, tiempo_espera_horas, tipo, tags_entreno, momento_ideal_txt, fases_info=None):
        self.id = id_t
        self.nombre = nombre
        self.zona = zona
        self.ondas = ondas
        self.intensidad = intensidad
        self.distancia = distancia
        self.duracion = duracion
        self.max_diario = max_diario
        self.tiempo_espera_horas = tiempo_espera_horas
        self.tipo = tipo  # 'LESION', 'PERMANENTE', 'MUSCULAR', 'GRASA'
        self.tags_entreno = tags_entreno 
        self.momento_ideal_txt = momento_ideal_txt # Texto descriptivo (ej: "Pre-Entreno")
        self.incompatibilidades = "" 
        self.fases_info = fases_info if fases_info else {}

    def set_incompatibilidades(self, texto):
        self.incompatibilidades = texto
        return self

# --- CATÁLOGO CON MOMENTOS RECOMENDADOS ---
@st.cache_data
def obtener_catalogo():
    fases_articulacion = {
        7: "🔥 Fase 1: Aguda (Bajar dolor)",
        21: "🛠️ Fase 2: Proliferación (Generar tejido)",
        60: "🧱 Fase 3: Remodelación (Flexibilidad)"
    }
    
    catalogo = [
        # --- LESIONES (Flexible: Antes para calentar, Después para dolor) ---
        Tratamiento("rodilla_d", "Rodilla Derecha (Lesión)", "Rodilla Dcha", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], "Flexible: Antes o Después de Entrenar", fases_articulacion)
        .set_incompatibilidades("Implantes metálicos, Cáncer activo."),
        
        Tratamiento("rodilla_i", "Rodilla Izquierda (Lesión)", "Rodilla Izq", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], "Flexible: Antes o Después de Entrenar", fases_articulacion)
        .set_incompatibilidades("Implantes metálicos, Cáncer activo."),
        
        Tratamiento("codo_d", "Codo Derecho (Lesión)", "Codo Dcho", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], "Flexible: Antes o Después de Entrenar", fases_articulacion)
        .set_incompatibilidades("No usar si infiltración <5 días."),
        
        Tratamiento("codo_i", "Codo Izquierdo (Lesión)", "Codo Izq", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], "Flexible: Antes o Después de Entrenar", fases_articulacion)
        .set_incompatibilidades("No usar si infiltración <5 días."),
        
        # --- GRASA (Estricto: Pre-Entreno) ---
        Tratamiento("fat_d", "Flanco Derecho (Grasa)", "Abdomen Dcho", "NIR + RED", "100%", "10-15 cm", 10, 1, 0, "GRASA", ['Active'], "OBLIGATORIO: Antes de Entrenar")
        .set_incompatibilidades("Tatuajes oscuros. Embarazo prohibido."),
        
        Tratamiento("fat_i", "Flanco Izquierdo (Grasa)", "Abdomen Izq", "NIR + RED", "100%", "10-15 cm", 10, 1, 0, "GRASA", ['Active'], "OBLIGATORIO: Antes de Entrenar")
        .set_incompatibilidades("Tatuajes oscuros. Embarazo prohibido."),
        
        # --- MÚSCULO (Flexible: Preferible Post) ---
        Tratamiento("arm_d", "Antebrazo Derecho (Recuperación)", "Antebrazo Dcho", "NIR + RED", "100%", "15-30 cm", 10, 1, 0, "MUSCULAR", ['Upper'], "Ideal: Después de Entrenar")
        .set_incompatibilidades("Opcional: Pulsos 50Hz."),
        
        Tratamiento("arm_i", "Antebrazo Izquierdo (Recuperación)", "Antebrazo Izq", "NIR + RED", "100%", "15-30 cm", 10, 1, 0, "MUSCULAR", ['Upper'], "Ideal: Después de Entrenar")
        .set_incompatibilidades("Opcional: Pulsos 50Hz."),
        
        # --- BIENESTAR (Horarios fijos) ---
        Tratamiento("testo", "Boost Testosterona", "Testículos", "NIR + RED", "100%", "15-20 cm", 5, 1, 0, "PERMANENTE", ['All'], "Mañana (Al despertar)")
        .set_incompatibilidades("No exceder tiempo. Varicocele."),
        
        Tratamiento("brain", "Salud Cerebral", "Cabeza", "SOLO NIR", "100%", "30 cm", 10, 1, 0, "PERMANENTE", ['All'], "Cualquier hora (Con Gafas)")
        .set_incompatibilidades("⛔ GAFAS OBLIGATORIAS."),
        
        Tratamiento("sleep", "Sueño y Ritmo", "Ambiente", "SOLO RED", "10-20%", "> 50 cm", 15, 1, 0, "PERMANENTE", ['All'], "Noche (30 min antes dormir)")
        .set_incompatibilidades("⛔ NO USAR PULSOS.")
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

st.info("🏋️ **¿Qué toca hoy?** (Tus rutinas)")

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

seleccion_rutinas = st.multiselect(
    "Rutinas realizadas:", 
    nombres_rutinas, 
    default=default_options
)

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

# --- MOTOR DE RECOMENDACIÓN ---
st.subheader(f"📋 Tratamientos para hoy")

registros_dia = st.session_state.db["historial"].get(fecha_str, {})
contador_visible = 0

for t in lista_tratamientos:
    
    mostrar = False
    motivo_oculto = ""
    
    # Lógica de visualización
    es_ciclo_activo = False
    if t.tipo == "LESION":
        ciclo = st.session_state.db["ciclos_activos"].get(t.id)
        if ciclo and ciclo['activo']:
            mostrar = True
            es_ciclo_activo = True
        else:
            motivo_oculto = "Inactivo"
    elif t.tipo == "PERMANENTE":
        mostrar = True
    elif t.tipo == "GRASA":
        if "Active" in tags_dia: mostrar = True
        else: motivo_oculto = "Requiere ejercicio"
    elif t.tipo == "MUSCULAR":
        if "Upper" in tags_dia: mostrar = True
        else: mostrar = False

    # --- RENDERIZADO ---
    if mostrar:
        contador_visible += 1
        
        # Info Fase Lesión
        info_fase = ""
        bloqueado_por_fin = False
        dias_trans = 0
        if t.tipo == "LESION" and es_ciclo_activo:
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

        # Estado
        sesiones_hechas = registros_dia.get(t.id, [])
        num_hechos = len(sesiones_hechas)
        completo = num_hechos >= t.max_diario
        icono = "✅" if completo else ("⏳" if num_hechos > 0 else "⬜")
        
        titulo = f"{icono} {t.nombre}"
        if completo: titulo += " (Completado)"
        
        with st.expander(titulo):
            # 1. INFO TÉCNICA Y MOMENTO
            if info_fase: st.info(info_fase)
            
            # Muestra el MOMENTO RECOMENDADO
            st.markdown(f"🕒 **Recomendado:** {t.momento_ideal_txt}")

            c1, c2 = st.columns(2)
            c1.markdown(f"**Zona:** {t.zona}\n\n**Ondas:** {t.ondas}")
            c2.markdown(f"**Distancia:** {t.distancia}\n\n**Tiempo:** {t.duracion} min")
            
            if hasattr(t, 'incompatibilidades') and t.incompatibilidades:
                st.warning(f"⚠️ {t.incompatibilidades}")

            # 2. LISTA DE SESIONES REALIZADAS (CON BORRADO)
            if num_hechos > 0:
                st.markdown("---")
                st.write("**Historial hoy:**")
                for i, reg in enumerate(sesiones_hechas):
                    col_txt, col_del = st.columns([5, 1])
                    with col_txt:
                        st.success(f"✅ {reg['hora']} - {reg['detalle']}")
                    with col_del:
                        # BOTÓN DE BORRADO (UNDO)
                        if st.button("🗑️", key=f"del_{t.id}_{i}"):
                            registros_dia[t.id].pop(i) # Eliminar de la lista
                            # Si la lista queda vacía, limpiamos clave
                            if not registros_dia[t.id]:
                                del registros_dia[t.id]
                            guardar_datos(st.session_state.db)
                            st.rerun()

            # 3. REGISTRAR NUEVA SESIÓN
            if not completo and not bloqueado_por_fin:
                # Validar espera 6h
                bloqueado_tiempo = False
                if num_hechos > 0 and t.tiempo_espera_horas > 0 and fecha_seleccionada == datetime.date.today():
                    last_str = sesiones_hechas[-1]['hora']
                    last = datetime.datetime.strptime(last_str, "%H:%M").time()
                    now = datetime.datetime.now().time()
                    diff = now.hour - last.hour + (now.minute - last.minute)/60
                    if diff < t.tiempo_espera_horas:
                        st.error(f"⏳ Espera {round(t.tiempo_espera_horas - diff, 1)}h más.")
                        bloqueado_tiempo = True
                
                if not bloqueado_tiempo:
                    st.markdown("---")
                    detalle_seleccionado = "Estándar"
                    permitir = True
                    
                    # SELECTOR DE MOMENTO REAL (ANTES/DESPUÉS)
                    if t.tipo in ["LESION", "MUSCULAR"] and seleccion_rutinas:
                        # Si hay entreno y es tratamiento físico, preguntar cuándo
                        momento = st.radio(
                            "¿Cuándo lo has realizado?", 
                            ["Antes de Entrenar", "Después de Entrenar", "Otro momento"],
                            horizontal=True,
                            key=f"mom_{t.id}_{num_hechos}"
                        )
                        detalle_seleccionado = momento
                        
                    elif t.tipo == "GRASA":
                        st.write("🔥 **Requisito:** Entrenar en breve.")
                        if not st.checkbox("Confirmo entreno inminente", key=f"c_{t.id}"): permitir = False
                        detalle_seleccionado = "Pre-Entreno"
                    
                    elif t.tipo == "PERMANENTE":
                        # Para testosterona/sueño no preguntamos antes/después de entreno, se asume el recomendado
                        detalle_seleccionado = t.momento_ideal_txt.split("(")[0].strip()

                    if permitir:
                        if st.button(f"Registrar Sesión {num_hechos+1}", key=f"b_{t.id}"):
                            ahora = datetime.datetime.now().strftime('%H:%M')
                            if "historial" not in st.session_state.db: st.session_state.db["historial"] = {}
                            if fecha_str not in st.session_state.db["historial"]: st.session_state.db["historial"][fecha_str] = {}
                            if t.id not in st.session_state.db["historial"][fecha_str]: st.session_state.db["historial"][fecha_str][t.id] = []
                            
                            st.session_state.db["historial"][fecha_str][t.id].append({"hora": ahora, "detalle": detalle_seleccionado})
                            guardar_datos(st.session_state.db)
                            st.rerun()
            
            # REINICIO CICLO
            if t.tipo == "LESION" and bloqueado_por_fin:
                if st.button("🔄 Reiniciar Ciclo (Recaída)", key=f"r_{t.id}"):
                     st.session_state.db["ciclos_activos"][t.id] = {"fecha_inicio": fecha_str, "activo": True}
                     guardar_datos(st.session_state.db)
                     st.rerun()

# --- OTROS ---
if contador_visible < len(lista_tratamientos):
    st.markdown("---")
    with st.expander("📂 Otros tratamientos"):
        for t in lista_tratamientos:
            mostrar_arriba = False
            if t.tipo == "LESION" and st.session_state.db["ciclos_activos"].get(t.id, {}).get('activo'): mostrar_arriba = True
            elif t.tipo == "PERMANENTE": mostrar_arriba = True
            elif t.tipo == "GRASA" and "Active" in tags_dia: mostrar_arriba = True
            elif t.tipo == "MUSCULAR" and "Upper" in tags_dia: mostrar_arriba = True
            
            if not mostrar_arriba:
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{t.nombre}**")
                if t.tipo == "LESION":
                    if c2.button("Activar", key=f"act_{t.id}"):
                        st.session_state.db["ciclos_activos"][t.id] = {"fecha_inicio": fecha_str, "activo": True}
                        guardar_datos(st.session_state.db)
                        st.rerun()
                else:
                    c2.caption("Descanso")
