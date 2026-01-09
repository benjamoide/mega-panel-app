import streamlit as st
import datetime
import json
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Mega Panel Control",
    page_icon="🔴",
    layout="mobile"
)

# --- NOMBRE DEL ARCHIVO PARA GUARDAR DATOS ---
ARCHIVO_DATOS = 'historial_mega_panel.json'

class Tratamiento:
    def __init__(self, id_t, nombre, zona, ondas, intensidad, distancia, duracion, frecuencia, momento_tipo, incompatibilidades):
        self.id = id_t
        self.nombre = nombre
        self.zona = zona
        self.ondas = ondas
        self.intensidad = intensidad
        self.distancia = distancia
        self.duracion = duracion
        self.frecuencia = frecuencia
        self.momento_tipo = momento_tipo 
        self.incompatibilidades = incompatibilidades
        self.completado_hoy = False
        self.detalle_realizacion = ""

    def to_dict(self):
        return {
            "completado": self.completado_hoy,
            "detalle": self.detalle_realizacion
        }

# --- FUNCIÓN PARA CARGAR TRATAMIENTOS ---
@st.cache_data
def obtener_catalogo():
    return [
        # --- DOLOR ARTICULAR ---
        Tratamiento("rodilla_d", "Rodilla Derecha (Dolor)", "Rodilla Dcha", "NIR + RED (Todo ON)", "100%", "15-20 cm", 10, "6-7x/sem", "Flexible_Entreno", "Implantes metálicos (calor), Cáncer activo."),
        Tratamiento("rodilla_i", "Rodilla Izquierda (Dolor)", "Rodilla Izq", "NIR + RED (Todo ON)", "100%", "15-20 cm", 10, "6-7x/sem", "Flexible_Entreno", "Implantes metálicos (calor), Cáncer activo."),
        Tratamiento("codo_d", "Codo Derecho (Dolor)", "Codo Dcho", "NIR + RED (Todo ON)", "100%", "15-20 cm", 10, "6-7x/sem", "Flexible_Entreno", "No usar si hubo infiltración hace <5 días."),
        Tratamiento("codo_i", "Codo Izquierdo (Dolor)", "Codo Izq", "NIR + RED (Todo ON)", "100%", "15-20 cm", 10, "6-7x/sem", "Flexible_Entreno", "No usar si hubo infiltración hace <5 días."),
        
        # --- GRASA ---
        Tratamiento("fat_d", "Flanco Derecho (Quema Grasa)", "Abdomen Dcho", "NIR + RED (Todo ON)", "100%", "10-15 cm (Muy Cerca)", 10, "5-7x/sem", "Pre_Obligatorio", "Cuidado con tatuajes oscuros. Embarazo prohibido."),
        Tratamiento("fat_i", "Flanco Izquierdo (Quema Grasa)", "Abdomen Izq", "NIR + RED (Todo ON)", "100%", "10-15 cm (Muy Cerca)", 10, "5-7x/sem", "Pre_Obligatorio", "Cuidado con tatuajes oscuros. Embarazo prohibido."),
        
        # --- MÚSCULO ---
        Tratamiento("arm_d", "Antebrazo Derecho (Músculo)", "Antebrazo Dcho", "NIR + RED", "100%", "15-30 cm", 10, "3-5x/sem", "Flexible_Entreno", "Opcional: Pulsos 50Hz para drenar."),
        Tratamiento("arm_i", "Antebrazo Izquierdo (Músculo)", "Antebrazo Izq", "NIR + RED", "100%", "15-30 cm", 10, "3-5x/sem", "Flexible_Entreno", "Opcional: Pulsos 50Hz para drenar."),
        
        # --- ESPECIALES ---
        Tratamiento("testo", "Boost Testosterona", "Testículos", "NIR + RED", "100%", "15-20 cm", 5, "5-7x/sem", "Mañana", "No exceder tiempo. Consultar varicocele."),
        Tratamiento("brain", "Salud Cerebral (Cognitivo)", "Cabeza/Frente", "SOLO NIR (Infrarrojo)", "100%", "30 cm", 10, "5-7x/sem", "Cualquiera", "⛔ GAFAS OBLIGATORIAS. NIR daña la retina."),
        Tratamiento("sleep", "Sueño y Ritmo Circadiano", "Ambiente Habitación", "SOLO RED (Rojo)", "10-20% (Bajo)", "> 50 cm", 15, "Diario", "Noche", "⛔ NO USAR PULSOS. Luz fija y suave.")
    ]

# --- GESTIÓN DE ESTADO (PERSISTENCIA) ---
def cargar_estado():
    if not os.path.exists(ARCHIVO_DATOS):
        return {}
    try:
        with open(ARCHIVO_DATOS, 'r') as f:
            datos = json.load(f)
        hoy = datetime.date.today().isoformat()
        # Si es otro día, reiniciamos (devolvemos dict vacío)
        if datos.get('fecha') != hoy:
            return {}
        return datos.get('registros', {})
    except:
        return {}

def guardar_estado(registros):
    datos = {
        'fecha': datetime.date.today().isoformat(),
        'registros': registros
    }
    with open(ARCHIVO_DATOS, 'w') as f:
        json.dump(datos, f, indent=4)

# --- INICIALIZAR SESSION STATE ---
if 'registros' not in st.session_state:
    st.session_state.registros = cargar_estado()

# --- INTERFAZ PRINCIPAL ---
st.title(f"🔴 Mega Panel Control")
st.caption(f"Fecha: {datetime.date.today().strftime('%d/%m/%Y')}")

lista_tratamientos = obtener_catalogo()

# Barra de progreso
completados = len(st.session_state.registros)
total = len(lista_tratamientos)
progreso = completados / total
st.progress(progreso, text=f"Progreso Diario: {completados}/{total}")

st.divider()

# --- GENERAR LISTA DE TRATAMIENTOS ---
for t in lista_tratamientos:
    # Verificar si está completado en el estado actual
    esta_completado = t.id in st.session_state.registros
    
    # Icono y Color según estado
    icono = "✅" if esta_completado else "⬜"
    
    # Usamos un expander para cada tratamiento
    with st.expander(f"{icono} {t.nombre}"):
        
        # 1. Mostrar Información Técnica
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Zona:** {t.zona}")
            st.markdown(f"**Luces:** {t.ondas}")
            st.markdown(f"**Intensidad:** {t.intensidad}")
        with c2:
            st.markdown(f"**Distancia:** {t.distancia}")
            st.markdown(f"**Tiempo:** {t.duracion} min")
            st.markdown(f"**Frec:** {t.frecuencia}")
            
        if t.incompatibilidades:
            st.warning(f"⚠️ {t.incompatibilidades}")

        # 2. Lógica de Advertencia Horaria (Visual)
        hora_actual = datetime.datetime.now().hour
        if t.momento_tipo == 'Mañana' and hora_actual > 12:
            st.info("💡 Consejo: Este tratamiento es mejor por la mañana.")
        elif t.momento_tipo == 'Noche' and hora_actual < 19:
            st.info("💡 Consejo: Este tratamiento es para antes de dormir.")

        # 3. Interfaz de Registro
        if esta_completado:
            detalle = st.session_state.registros[t.id]['detalle']
            st.success(f"Completado a las: {detalle}")
            # Botón para deshacer (opcional)
            if st.button("Deshacer", key=f"undo_{t.id}"):
                del st.session_state.registros[t.id]
                guardar_estado(st.session_state.registros)
                st.rerun()
        else:
            # Selector de Momento (si aplica)
            nota_extra = ""
            
            if t.momento_tipo == 'Flexible_Entreno':
                momento = st.radio("¿Momento del entreno?", ["Antes", "Después"], horizontal=True, key=f"rad_{t.id}")
                nota_extra = f"Realizado {momento.upper()}-ENTRENO"
            
            elif t.momento_tipo == 'Pre_Obligatorio':
                st.error("🔥 REQUISITO: Debes entrenar en los próximos 30-60 min.")
                confirmacion = st.checkbox("Confirmo que voy a entrenar", key=f"chk_{t.id}")
                if not confirmacion:
                    st.stop() # Detiene la ejecución de este bloque hasta que marque
                nota_extra = "Realizado PRE-ENTRENO (Obligatorio)"

            # Botón de Completar
            if st.button("Marcar como Realizado", key=f"btn_{t.id}"):
                ahora_str = datetime.datetime.now().strftime('%H:%M')
                detalle_final = f"{ahora_str} {nota_extra}"
                
                # Guardar en Session State y JSON
                st.session_state.registros[t.id] = {
                    'completado': True,
                    'detalle': detalle_final
                }
                guardar_estado(st.session_state.registros)
                st.rerun() # Recargar página para actualizar iconos
