import streamlit as st
import datetime
import json
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Mega Panel Expert",
    page_icon="🧬",
    layout="centered"
)

# --- ARCHIVO DE DATOS ---
ARCHIVO_DATOS = 'historial_mega_panel_v3.json'

# --- CLASE DE TRATAMIENTO ---
class Tratamiento:
    def __init__(self, id_t, nombre, zona, ondas, intensidad, distancia, duracion, max_diario, tiempo_espera_horas, tipo, fases_info=None):
        self.id = id_t
        self.nombre = nombre
        self.zona = zona
        self.ondas = ondas
        self.intensidad = intensidad
        self.distancia = distancia
        self.duracion = duracion
        self.max_diario = max_diario
        self.tiempo_espera_horas = tiempo_espera_horas
        self.tipo = tipo  # 'LESION' (Ciclo finito) o 'PERMANENTE' (Siempre disponible)
        
        # Diccionario de fases: { dias_limite: "Nombre Fase" }
        # Ej: { 7: "Aguda/Inflamación", 21: "Proliferación", 60: "Remodelación" }
        self.fases_info = fases_info if fases_info else {}

# --- CATÁLOGO EXPERTO ---
@st.cache_data
def obtener_catalogo():
    # FASES TÍPICAS DE RECUPERACIÓN DE TEJIDOS (Para lesiones)
    fases_articulacion = {
        7: "🔥 Fase 1: Aguda/Inflamatoria (Enfoque: Bajar dolor)",
        21: "🛠️ Fase 2: Proliferación (Enfoque: Generar tejido)",
        60: "🧱 Fase 3: Remodelación (Enfoque: Flexibilidad y Fuerza)"
    }
    
    return [
        # --- LESIONES (Tipo: LESION - Tienen fin y reinicio) ---
        Tratamiento("rodilla_d", "Rodilla Derecha (Lesión)", "Rodilla Dcha", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", fases_articulacion),
        Tratamiento("rodilla_i", "Rodilla Izquierda (Lesión)", "Rodilla Izq", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", fases_articulacion),
        Tratamiento("codo_d", "Codo Derecho (Lesión)", "Codo Dcho", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", fases_articulacion),
        Tratamiento("codo_i", "Codo Izquierdo (Lesión)", "Codo Izq", "NIR + RED", "100%", "15-20 cm", 10, 2, 6, "LESION", fases_articulacion),
        
        # --- PERMANENTES (Tipo: PERMANENTE - Siempre disponibles) ---
        Tratamiento("fat_d", "Flanco Derecho (Grasa)", "Abdomen Dcho", "NIR + RED", "100%", "10-15 cm", 10, 1, 0, "PERMANENTE"),
        Tratamiento("fat_i", "Flanco Izquierdo (Grasa)", "Abdomen Izq", "NIR + RED", "100%", "10-15 cm", 10, 1, 0, "PERMANENTE"),
        Tratamiento("arm_d", "Antebrazo Derecho (Músculo)", "Antebrazo Dcho", "NIR + RED", "100%", "15-30 cm", 10, 1, 0, "PERMANENTE"),
        Tratamiento("arm_i", "Antebrazo Izquierdo (Músculo)", "Antebrazo Izq", "NIR + RED", "100%", "15-30 cm", 10, 1, 0, "PERMANENTE"),
        Tratamiento("testo", "Boost Testosterona", "Testículos", "NIR + RED", "100%", "15-20 cm", 5, 1, 0, "PERMANENTE"),
        Tratamiento("brain", "Salud Cerebral", "Cabeza", "SOLO NIR", "100%", "30 cm", 10, 1, 0, "PERMANENTE"),
        Tratamiento("sleep", "Sueño y Ritmo", "Ambiente", "SOLO RED", "10-20%", "> 50 cm", 15, 1, 0, "PERMANENTE")
    ]

# --- GESTIÓN DE DATOS ---
def cargar_datos():
    if not os.path.exists(ARCHIVO_DATOS):
        return {"historial": {}, "ciclos_activos": {}}
    try:
        with open(ARCHIVO_DATOS, 'r') as f:
            datos = json.load(f)
            # Asegurar estructura compatible si viene de versión anterior
            if "historial" not in datos:
                return {"historial": datos, "ciclos_activos": {}}
            return datos
    except:
        return {"historial": {}, "ciclos_activos": {}}

def guardar_datos(datos):
    with open(ARCHIVO_DATOS, 'w') as f:
        json.dump(datos, f, indent=4)

# --- INTERFAZ PRINCIPAL ---
st.title(f"🧬 Mega Panel Expert")

# Carga inicial
if 'db' not in st.session_state:
    st.session_state.db = cargar_datos()

lista_tratamientos = obtener_catalogo()

# 📅 CALENDARIO
fecha_seleccionada = st.date_input("Selecciona Fecha", datetime.date.today())
fecha_str = fecha_seleccionada.isoformat()

# Barra de Progreso Global del Día
registros_dia = st.session_state.db["historial"].get(fecha_str, {})
sesiones_hoy = sum([len(sesiones) for sesiones in registros_dia.values()])
st.caption(f"Actividad del: **{fecha_seleccionada.strftime('%d/%m/%Y')}** | Sesiones: {sesiones_hoy}")
st.divider()

# --- BUCLE DE TRATAMIENTOS ---
for t in lista_tratamientos:
    
    # 1. LÓGICA DE FASES Y CICLOS (Solo para lesiones)
    info_fase = ""
    bloqueado_por_fin_ciclo = False
    dias_transcurridos = 0
    
    if t.tipo == "LESION":
        # Ver si hay un ciclo activo para esta lesión
        ciclo = st.session_state.db["ciclos_activos"].get(t.id)
        
        if ciclo and ciclo['activo']:
            fecha_inicio = datetime.date.fromisoformat(ciclo['fecha_inicio'])
            dias_transcurridos = (fecha_seleccionada - fecha_inicio).days
            
            # Determinar fase actual
            nombre_fase = "Mantenimiento / Final"
            limite_maximo = max(t.fases_info.keys()) if t.fases_info else 60
            
            if dias_transcurridos < 0:
                info_fase = "📅 Planificado para futuro"
            elif dias_transcurridos > limite_maximo:
                info_fase = "🏁 Protocolo Finalizado (Periodo de descanso recomendado)"
                bloqueado_por_fin_ciclo = True
            else:
                # Buscar en qué fase cae
                for limite, nombre in sorted(t.fases_info.items()):
                    if dias_transcurridos <= limite:
                        nombre_fase = nombre
                        break
                info_fase = f"🗓️ Día {dias_transcurridos}: {nombre_fase}"
        else:
            info_fase = "🌑 Sin protocolo activo"
            bloqueado_por_fin_ciclo = True # Bloqueado hasta que se inicie

    # 2. ESTADO DEL DÍA
    sesiones_realizadas = registros_dia.get(t.id, [])
    cantidad_hecha = len(sesiones_realizadas)
    esta_completo_hoy = cantidad_hecha >= t.max_diario

    # Icono
    if t.tipo == "LESION" and bloqueado_por_fin_ciclo and not (ciclo and ciclo.get('activo') and dias_transcurridos > 0):
        icono = "⏸️" # Pausado/No iniciado
    elif esta_completo_hoy:
        icono = "✅"
    elif cantidad_hecha > 0:
        icono = "⏳"
    else:
        icono = "⬜"

    titulo = f"{icono} {t.nombre}"
    
    # --- INTERFAZ DEL EXPANDER ---
    with st.expander(titulo):
        
        # A) GESTIÓN DE INICIO/REINICIO DE LESIÓN
        if t.tipo == "LESION":
            if not ciclo or not ciclo['activo']:
                st.info("Este tratamiento requiere activar un protocolo de recuperación.")
                if st.button(f"🚀 Iniciar Nuevo Protocolo de {t.nombre}", key=f"start_{t.id}"):
                    st.session_state.db["ciclos_activos"][t.id] = {
                        "fecha_inicio": datetime.date.today().isoformat(),
                        "activo": True
                    }
                    guardar_datos(st.session_state.db)
                    st.rerun()
            
            elif bloqueado_por_fin_ciclo and dias_transcurridos > 0:
                st.success(f"Has completado el ciclo de recuperación ({dias_transcurridos} días).")
                st.write("Si la lesión ha regresado, puedes reiniciar el contador.")
                if st.button(f"🔄 Reiniciar Protocolo (Recaída)", key=f"restart_{t.id}"):
                    st.session_state.db["ciclos_activos"][t.id] = {
                        "fecha_inicio": datetime.date.today().isoformat(),
                        "activo": True
                    }
                    guardar_datos(st.session_state.db)
                    st.rerun()
            
            else:
                st.warning(info_fase)
                st.progress(min(dias_transcurridos / 60, 1.0)) # Barra de progreso del ciclo total (aprox 60 dias)

        # B) INFORMACIÓN TÉCNICA
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Zona:** {t.zona}")
            st.markdown(f"**Luces:** {t.ondas}")
        with c2:
            st.markdown(f"**Distancia:** {t.distancia}")
            st.markdown(f"**Tiempo:** {t.duracion} min")
        
        # C) REGISTRO DIARIO (Solo si no está bloqueado por fin de ciclo o no iniciado)
        puede_registrar = True
        if t.tipo == "LESION" and bloqueado_por_fin_ciclo:
            puede_registrar = False
        
        if puede_registrar:
            # Mostrar historial de hoy
            if cantidad_hecha > 0:
                st.markdown("---")
                for i, sesion in enumerate(sesiones_realizadas):
                    st.info(f"✅ Sesión {i+1}: {sesion['hora']} - {sesion['detalle']}")
            
            # Botón para nueva sesión
            if not esta_completo_hoy:
                st.markdown("---")
                
                # Validación de 6 horas
                bloqueado_tiempo = False
                if cantidad_hecha > 0 and t.tiempo_espera_horas > 0 and fecha_seleccionada == datetime.date.today():
                    ultima = datetime.datetime.strptime(sesiones_realizadas[-1]['hora'], "%H:%M").time()
                    ahora = datetime.datetime.now().time()
                    diff = ahora.hour - ultima.hour + (ahora.minute - ultima.minute)/60
                    if diff < t.tiempo_espera_horas:
                        st.error(f"⏳ Espera {round(t.tiempo_espera_horas - diff, 1)}h para la siguiente sesión.")
                        bloqueado_tiempo = True

                if not bloqueado_tiempo:
                    col_btn, col_check = st.columns([1, 2])
                    detalle = "Estándar"
                    confirmar = True
                    
                    if t.nombre.startswith("Flanco"): # Grasa
                         st.caption("🔥 Requisito: Entrenar en 30-60 min.")
                         if not st.checkbox("Voy a entrenar", key=f"chk_{t.id}"): confirmar = False
                         detalle = "Pre-Entreno"
                    
                    if confirmar:
                        if st.button(f"Registrar Sesión {cantidad_hecha+1}", key=f"btn_{t.id}"):
                            ahora_str = datetime.datetime.now().strftime('%H:%M')
                            
                            # Crear estructura si no existe
                            if "historial" not in st.session_state.db: st.session_state.db["historial"] = {}
                            if fecha_str not in st.session_state.db["historial"]: st.session_state.db["historial"][fecha_str] = {}
                            if t.id not in st.session_state.db["historial"][fecha_str]: st.session_state.db["historial"][fecha_str][t.id] = []
                            
                            st.session_state.db["historial"][fecha_str][t.id].append({
                                "hora": ahora_str,
                                "detalle": detalle
                            })
                            guardar_datos(st.session_state.db)
                            st.rerun()
