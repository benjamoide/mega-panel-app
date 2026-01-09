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

# --- CLASE DE TRATAMIENTO ---
class Tratamiento:
    def __init__(self, id_t, nombre, zona, ondas, intensidad, distancia, duracion, max_diario, tiempo_espera_horas, tipo, tags_entreno, fases_info=None):
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
        self.tags_entreno = tags_entreno # Lista de entrenamientos compatibles (ej: ['Upper', 'FullBody'])
        self.fases_info = fases_info if fases_info else {}

# --- CATÁLOGO INTELIGENTE ---
@st.cache_data
def obtener_catalogo():
    fases_articulacion = {
        7: "🔥 Fase 1: Aguda (Bajar dolor)",
        21: "🛠️ Fase 2: Proliferación (Generar tejido)",
        60: "🧱 Fase 3: Remodelación (Flexibilidad)"
    }
    
    # TIPOS DE ENTRENO: 'Cardio', 'Upper' (Superior), 'Lower' (Inferior), 'Rest' (Descanso)
    # Nota: 'All' significa que siempre se recomienda.
    
    return [
        # --- LESIONES (Prioridad Máxima - Siempre visibles si activas) ---
        Tratamiento("rodilla_d", "Rodilla Derecha (Lesión)", "Rodilla Dcha", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], fases_articulacion),
        Tratamiento("rodilla_i", "Rodilla Izquierda (Lesión)", "Rodilla Izq", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], fases_articulacion),
        Tratamiento("codo_d", "Codo Derecho (Lesión)", "Codo Dcho", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], fases_articulacion),
        Tratamiento("codo_i", "Codo Izquierdo (Lesión)", "Codo Izq", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", ['All'], fases_articulacion),
        
        # --- QUEMA DE GRASA (Solo con Cardio o Pesas - Prohibido en Descanso) ---
        Tratamiento("fat_d", "Flanco Derecho (Grasa)", "Abdomen Dcho", "NIR + RED", "100%", "10-15 cm", 10, 1, 0, "GRASA", ['Cardio', 'Upper', 'Lower']),
        Tratamiento("fat_i", "Flanco Izquierdo (Grasa)", "Abdomen Izq", "NIR + RED", "100%", "10-15 cm", 10, 1, 0, "GRASA", ['Cardio', 'Upper', 'Lower']),
        
        # --- MÚSCULO (Según zona entrenada) ---
        Tratamiento("arm_d", "Antebrazo Derecho (Recuperación)", "Antebrazo Dcho", "NIR + RED", "100%", "15-30 cm", 10, 1, 0, "MUSCULAR", ['Upper']),
        Tratamiento("arm_i", "Antebrazo Izquierdo (Recuperación)", "Antebrazo Izq", "NIR + RED", "100%", "15-30 cm", 10, 1, 0, "MUSCULAR", ['Upper']),
        
        # --- BIENESTAR (Siempre disponibles) ---
        Tratamiento("testo", "Boost Testosterona", "Testículos", "NIR + RED", "100%", "15-20 cm", 5, 1, 0, "PERMANENTE", ['All']),
        Tratamiento("brain", "Salud Cerebral", "Cabeza", "SOLO NIR", "100%", "30 cm", 10, 1, 0, "PERMANENTE", ['All']),
        Tratamiento("sleep", "Sueño y Ritmo", "Ambiente", "SOLO RED", "10-20%", "> 50 cm", 15, 1, 0, "PERMANENTE", ['All'])
    ]

# --- GESTIÓN DE DATOS ---
def cargar_datos():
    if not os.path.exists(ARCHIVO_DATOS):
        # Estructura: historial (tratamientos), meta_diaria (tipo entreno del dia), ciclos_activos
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

# 2. SELECCIÓN DE ENTRENAMIENTO (CRITERIO DE FILTRADO)
# Recuperar qué se entrenó ese día (si ya se guardó)
entreno_guardado = st.session_state.db.get("meta_diaria", {}).get(fecha_str, [])

st.info("🏋️ **Configuración del Día:** ¿Qué tipo de actividad realizas hoy?")
opciones_entreno = ["Descanso / Nada", "Cardio / Aeróbico", "Fuerza: Tren Superior (Brazos/Pecho/Espalda)", "Fuerza: Tren Inferior (Piernas)"]

# Mapeo de opciones visuales a tags internos
mapa_entreno = {
    "Descanso / Nada": "Rest",
    "Cardio / Aeróbico": "Cardio",
    "Fuerza: Tren Superior (Brazos/Pecho/Espalda)": "Upper",
    "Fuerza: Tren Inferior (Piernas)": "Lower"
}

seleccion_usuario = st.multiselect(
    "Selecciona uno o varios:", 
    opciones_entreno, 
    default=[k for k, v in mapa_entreno.items() if v in entreno_guardado]
)

# Convertir selección a tags internos (ej. ['Cardio', 'Upper'])
tags_dia = []
if not seleccion_usuario: 
    tags_dia = ["Rest"] # Por defecto descanso si no marca nada
else:
    for s in seleccion_usuario:
        tags_dia.append(mapa_entreno[s])

# Guardar automáticamente el tipo de entreno al cambiar
if set(tags_dia) != set(entreno_guardado):
    if "meta_diaria" not in st.session_state.db: st.session_state.db["meta_diaria"] = {}
    st.session_state.db["meta_diaria"][fecha_str] = tags_dia
    guardar_datos(st.session_state.db)
    st.rerun()

st.divider()

# --- MOTOR DE RECOMENDACIÓN ---
st.subheader(f"📋 Tratamientos Recomendados para hoy")

registros_dia = st.session_state.db["historial"].get(fecha_str, {})
contador_visible = 0

for t in lista_tratamientos:
    
    # --- FILTRO INTELIGENTE ---
    mostrar = False
    motivo_oculto = ""
    
    # 1. Lesiones activas: SIEMPRE mostrar
    es_ciclo_activo = False
    if t.tipo == "LESION":
        ciclo = st.session_state.db["ciclos_activos"].get(t.id)
        if ciclo and ciclo['activo']:
            mostrar = True
            es_ciclo_activo = True
        else:
            # Si es lesión pero no activa, mostrar solo si el usuario quiere activarla
            # Lo mostramos al final o en una sección de "Otros"
            motivo_oculto = "Inactivo"
    
    # 2. Permanente/Lifestyle: SIEMPRE mostrar
    elif t.tipo == "PERMANENTE":
        mostrar = True
        
    # 3. Grasa: Solo si hay actividad física (Cardio o Pesas)
    elif t.tipo == "GRASA":
        if "Rest" in tags_dia:
            mostrar = False
            motivo_oculto = "Requiere ejercicio (Día de Descanso)"
        elif any(tag in tags_dia for tag in t.tags_entreno):
            mostrar = True
            
    # 4. Muscular: Solo si coincide el grupo muscular
    elif t.tipo == "MUSCULAR":
        if any(tag in tags_dia for tag in t.tags_entreno):
            mostrar = True
        else:
            mostrar = False
            motivo_oculto = "Grupo muscular no entrenado hoy"

    # --- RENDERIZADO SI PASA EL FILTRO ---
    if mostrar:
        contador_visible += 1
        
        # Lógica de Fases (Copiada de versión anterior)
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

        # Estado visual
        hechos = len(registros_dia.get(t.id, []))
        completo = hechos >= t.max_diario
        icono = "✅" if completo else ("⏳" if hechos > 0 else "⬜")
        
        titulo = f"{icono} {t.nombre}"
        if completo: titulo += " (Completado)"
        
        with st.expander(titulo):
            # INFO
            if info_fase: st.info(info_fase)
            
            c1, c2 = st.columns(2)
            c1.markdown(f"**Zona:** {t.zona}\n\n**Ondas:** {t.ondas}")
            c2.markdown(f"**Distancia:** {t.distancia}\n\n**Tiempo:** {t.duracion} min")
            
            if t.incompatibilidades: st.warning(f"⚠️ {t.incompatibilidades}")

            # HISTORIAL HOY
            if hechos > 0:
                st.markdown("---")
                for reg in registros_dia[t.id]:
                    st.success(f"Hecho a las {reg['hora']} ({reg['detalle']})")

            # BOTONES ACCIÓN
            if not completo and not bloqueado_por_fin:
                # Validar espera 6h (si aplica)
                bloqueado_tiempo = False
                if hechos > 0 and t.tiempo_espera_horas > 0 and fecha_seleccionada == datetime.date.today():
                    last = datetime.datetime.strptime(registros_dia[t.id][-1]['hora'], "%H:%M").time()
                    now = datetime.datetime.now().time()
                    diff = now.hour - last.hour + (now.minute - last.minute)/60
                    if diff < t.tiempo_espera_horas:
                        st.error(f"⏳ Espera {round(t.tiempo_espera_horas - diff, 1)}h más.")
                        bloqueado_tiempo = True
                
                if not bloqueado_tiempo:
                    st.markdown("---")
                    detalle = "Estándar"
                    
                    # Lógica Grasa Pre-Entreno
                    permitir = True
                    if t.tipo == "GRASA":
                        st.write("🔥 **Requisito:** Entrenar en breve.")
                        if not st.checkbox("Confirmo entreno inminente", key=f"c_{t.id}"): permitir = False
                        detalle = "Pre-Entreno"
                    
                    if permitir:
                        if st.button(f"Registrar Sesión {hechos+1}", key=f"b_{t.id}"):
                            ahora = datetime.datetime.now().strftime('%H:%M')
                            if "historial" not in st.session_state.db: st.session_state.db["historial"] = {}
                            if fecha_str not in st.session_state.db["historial"]: st.session_state.db["historial"][fecha_str] = {}
                            if t.id not in st.session_state.db["historial"][fecha_str]: st.session_state.db["historial"][fecha_str][t.id] = []
                            
                            st.session_state.db["historial"][fecha_str][t.id].append({"hora": ahora, "detalle": detalle})
                            guardar_datos(st.session_state.db)
                            st.rerun()
            
            # REINICIO LESION
            if t.tipo == "LESION" and bloqueado_por_fin:
                if st.button("🔄 Reiniciar Ciclo (Recaída)", key=f"r_{t.id}"):
                     st.session_state.db["ciclos_activos"][t.id] = {"fecha_inicio": fecha_str, "activo": True}
                     guardar_datos(st.session_state.db)
                     st.rerun()

# --- SECCIÓN DE TRATAMIENTOS OCULTOS/INACTIVOS ---
if contador_visible < len(lista_tratamientos):
    st.markdown("---")
    with st.expander("📂 Ver otros tratamientos no recomendados hoy (o inactivos)"):
        for t in lista_tratamientos:
            # Repetimos lógica inversa para encontrar los ocultos
            es_visible_arriba = False
            if t.tipo == "PERMANENTE": es_visible_arriba = True
            elif t.tipo == "LESION" and st.session_state.db["ciclos_activos"].get(t.id, {}).get('activo'): es_visible_arriba = True
            elif t.tipo == "GRASA" and "Rest" not in tags_dia and any(tag in tags_dia for tag in t.tags_entreno): es_visible_arriba = True
            elif t.tipo == "MUSCULAR" and any(tag in tags_dia for tag in t.tags_entreno): es_visible_arriba = True
            
            if not es_visible_arriba:
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{t.nombre}**")
                
                # Botón para activar lesión si está inactiva
                if t.tipo == "LESION":
                    if c2.button("Activar", key=f"act_{t.id}"):
                        st.session_state.db["ciclos_activos"][t.id] = {"fecha_inicio": fecha_str, "activo": True}
                        guardar_datos(st.session_state.db)
                        st.rerun()
                else:
                    c2.caption("No prioritario hoy")
