import streamlit as st
import datetime
from datetime import timedelta
import json
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Mega Panel AI",
    page_icon="🧬",
    layout="centered"
)

# --- ARCHIVO DE DATOS ---
ARCHIVO_DATOS = 'historial_mega_panel_pro.json'

# --- CLASE DE TRATAMIENTO ---
class Tratamiento:
    def __init__(self, id_t, nombre, zona, ondas, intensidad, distancia, duracion, max_diario, max_semanal, tipo, tags_entreno, default_visual_group, momento_ideal_txt, momentos_prohibidos, tips_antes, tips_despues, fases_config=None):
        self.id = id_t
        self.nombre = nombre
        self.zona = zona
        self.ondas = ondas
        self.intensidad = intensidad
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
        self.incompatibilidades = "" 
        self.fases_config = fases_config if fases_config else []

    def set_incompatibilidades(self, texto):
        self.incompatibilidades = texto
        return self

# --- CATÁLOGO ---
@st.cache_data
def obtener_catalogo():
    fases_lesion = [
        {"nombre": "🔥 Fase 1: Inflamatoria/Aguda", "dias_fin": 7, "min_sesiones": 5},
        {"nombre": "🛠️ Fase 2: Proliferación", "dias_fin": 21, "min_sesiones": 10},
        {"nombre": "🧱 Fase 3: Remodelación", "dias_fin": 60, "min_sesiones": 20}
    ]
    
    catalogo = [
        # --- NUEVO: GRASA GLÚTEOS ---
        Tratamiento("fat_glutes", "Glúteos (Grasa)", "Glúteos/Caderas", "NIR + RED", "100%", "10-15 cm", 10, 1, 7, "GRASA", ['Active', 'Lower'], "PRE", "Ideal: Antes de Entrenar Pierna",
                    momentos_prohibidos=["🌙 Noche", "🧘 Después de Entrenar"], 
                    tips_antes=["💧 Beber agua.", "🧴 Piel limpia (sin cremas).", "👖 Ropa mínima."],
                    tips_despues=["🏃‍♂️ ACTIVIDAD YA: Sentadillas/Caminar.", "❌ NO sentarse en 45 min.", "🚿 Ducha post-ejercicio."])
        .set_incompatibilidades("Tatuajes oscuros. Embarazo."),

        # --- REJUVENECIMIENTO FACIAL ---
        Tratamiento("face_rejuv", "Rejuvenecimiento Facial", "Cara/Cuello", "RED + NIR", "50%", "30-50 cm", 10, 1, 5, "PERMANENTE", ['All'], "FLEX", "Cualquier hora (Piel Limpia)",
                    momentos_prohibidos=["🏋️ Antes de Entrenar"],
                    tips_antes=["🧼 DOBLE LIMPIEZA.", "🕶️ GAFAS OBLIGATORIAS.", "🧴 No Retinol."],
                    tips_despues=["🧴 Serum hidratante.", "❌ No sol directo."])
        .set_incompatibilidades("Melasma, Fotosensibilidad."),

        # --- GRASA ABDOMEN ---
        Tratamiento("fat_front", "Abdomen Frontal (Grasa)", "Abdomen", "NIR + RED", "100%", "10-15 cm", 10, 1, 7, "GRASA", ['Active'], "PRE", "Ideal: Antes de Entrenar",
                    momentos_prohibidos=["🌙 Noche", "🧘 Después de Entrenar"],
                    tips_antes=["💧 Beber agua.", "🧴 Piel limpia."],
                    tips_despues=["🏃‍♂️ ENTRENA YA.", "❌ Ayuno 1h."])
        .set_incompatibilidades("Tatuajes oscuros."),
        
        Tratamiento("fat_d", "Flanco Derecho (Grasa)", "Abdomen Dcho", "NIR + RED", "100%", "10-15 cm", 10, 1, 7, "GRASA", ['Active'], "PRE", "Ideal: Antes de Entrenar",
                    momentos_prohibidos=["🌙 Noche", "🧘 Después de Entrenar"],
                    tips_antes=["💧 Beber agua."],
                    tips_despues=["🏃‍♂️ ENTRENA YA.", "❌ Ayuno 1h."])
        .set_incompatibilidades("Tatuajes oscuros."),
        
        Tratamiento("fat_i", "Flanco Izquierdo (Grasa)", "Abdomen Izq", "NIR + RED", "100%", "10-15 cm", 10, 1, 7, "GRASA", ['Active'], "PRE", "Ideal: Antes de Entrenar",
                    momentos_prohibidos=["🌙 Noche", "🧘 Después de Entrenar"],
                    tips_antes=["💧 Beber agua."],
                    tips_despues=["🏃‍♂️ ENTRENA YA.", "❌ Ayuno 1h."])
        .set_incompatibilidades("Tatuajes oscuros."),

        # --- LESIONES: HOMBRO (NUEVO) ---
        Tratamiento("shoulder_d", "Hombro Derecho (Lesión)", "Deltoides/Manguito", "NIR + RED", "100%", "15-20 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["🧴 Piel limpia.", "👕 Sin ropa compresiva."],
                    tips_despues=["🔄 Movimientos pendulares.", "❌ No elevar brazo sobre cabeza 1h.", "🧊 Hielo si dolor agudo."],
                    fases_config=fases_lesion)
        .set_incompatibilidades("Marcapasos (cercanía). Implantes metálicos."),

        Tratamiento("shoulder_i", "Hombro Izquierdo (Lesión)", "Deltoides/Manguito", "NIR + RED", "100%", "15-20 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["🧴 Piel limpia.", "👕 Sin ropa compresiva."],
                    tips_despues=["🔄 Movimientos pendulares.", "❌ No elevar brazo sobre cabeza 1h.", "🧊 Hielo si dolor agudo."],
                    fases_config=fases_lesion)
        .set_incompatibilidades("Marcapasos. Implantes metálicos."),

        # --- LESIONES: ANTEBRAZO (NUEVO - DISTINTO A RECUPERACIÓN) ---
        Tratamiento("forearm_inj_d", "Antebrazo Derecho (Tendinitis)", "Epicóndilo/Flexores", "NIR + RED", "100%", "10-15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["⌚ Quitar reloj/pulseras.", "🧴 Piel limpia."],
                    tips_despues=["👋 Movilidad muñeca suave.", "❌ Evitar agarre fuerte/pesado.", "🧊 Hielo local OK."],
                    fases_config=fases_lesion)
        .set_incompatibilidades("Implantes."),

        Tratamiento("forearm_inj_i", "Antebrazo Izquierdo (Tendinitis)", "Epicóndilo/Flexores", "NIR + RED", "100%", "10-15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["⌚ Quitar reloj/pulseras.", "🧴 Piel limpia."],
                    tips_despues=["👋 Movilidad muñeca suave.", "❌ Evitar agarre fuerte.", "🧊 Hielo local OK."],
                    fases_config=fases_lesion)
        .set_incompatibilidades("Implantes."),

        # --- LESIONES: RODILLA Y CODO ---
        Tratamiento("rodilla_d", "Rodilla Derecha (Lesión)", "Rodilla Dcha", "NIR + RED", "100%", "15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["🧴 Piel limpia.", "❄️ NO hielo antes."],
                    tips_despues=["🦶 Movilidad.", "🧊 Hielo OK después."],
                    fases_config=fases_lesion)
        .set_incompatibilidades("Implantes metálicos. Cáncer activo."),
        
        Tratamiento("rodilla_i", "Rodilla Izquierda (Lesión)", "Rodilla Izq", "NIR + RED", "100%", "15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["🧴 Piel limpia.", "❄️ NO hielo antes."],
                    tips_despues=["🦶 Movilidad.", "🧊 Hielo OK después."],
                    fases_config=fases_lesion)
        .set_incompatibilidades("Implantes metálicos."),
        
        Tratamiento("codo_d", "Codo Derecho (Lesión)", "Codo Dcho", "NIR + RED", "100%", "15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["🧴 Piel limpia."],
                    tips_despues=["🔄 Estiramiento suave.", "❌ No cargar."],
                    fases_config=fases_lesion)
        .set_incompatibilidades("No infiltración <5 días."),
        
        Tratamiento("codo_i", "Codo Izquierdo (Lesión)", "Codo Izq", "NIR + RED", "100%", "15 cm", 10, 2, 7, "LESION", ['All'], "FLEX", "Flexible",
                    momentos_prohibidos=[],
                    tips_antes=["🧴 Piel limpia."],
                    tips_despues=["🔄 Estiramiento suave.", "❌ No cargar."],
                    fases_config=fases_lesion)
        .set_incompatibilidades("No infiltración <5 días."),
        
        # --- MÚSCULO (Recuperación Post-Entreno) ---
        Tratamiento("arm_d", "Antebrazo Derecho (Recuperación)", "Antebrazo Dcho", "NIR + RED", "100%", "15 cm", 10, 1, 6, "MUSCULAR", ['Upper'], "POST", "Ideal: Después de Entrenar",
                    momentos_prohibidos=["🏋️ Antes de Entrenar"], 
                    tips_antes=["🚿 Quitar sudor."],
                    tips_despues=["🥩 Proteína.", "🚿 Ducha contraste."])
        .set_incompatibilidades("Opcional: Pulsos 50Hz."),
        
        Tratamiento("arm_i", "Antebrazo Izquierdo (Recuperación)", "Antebrazo Izq", "NIR + RED", "100%", "15 cm", 10, 1, 6, "MUSCULAR", ['Upper'], "POST", "Ideal: Después de Entrenar",
                    momentos_prohibidos=["🏋️ Antes de Entrenar"],
                    tips_antes=["🚿 Quitar sudor."],
                    tips_despues=["🥩 Proteína.", "🚿 Ducha contraste."])
        .set_incompatibilidades("Opcional: Pulsos 50Hz."),
        
        # --- PERMANENTES ---
        Tratamiento("testo", "Boost Testosterona", "Testículos", "NIR + RED", "100%", "15 cm", 5, 1, 7, "PERMANENTE", ['All'], "MORNING", "Mañana",
                    momentos_prohibidos=["🌙 Noche", "⛅ Tarde", "🧘 Después de Entrenar"], 
                    tips_antes=["🚿 Piel limpia.", "❄️ Zona fresca."],
                    tips_despues=["🚿 Ducha fría."])
        .set_incompatibilidades("Varicocele."),
        
        Tratamiento("sleep", "Sueño y Ritmo", "Ambiente", "SOLO RED", "20%", ">50 cm", 15, 1, 7, "PERMANENTE", ['All'], "NIGHT", "Noche",
                    momentos_prohibidos=["🌞 Mañana", "⛅ Tarde", "🏋️ Antes de Entrenar", "🧘 Después de Entrenar"],
                    tips_antes=["📵 Apagar pantallas."],
                    tips_despues=["🛌 A DORMIR."])
        .set_incompatibilidades("⛔ NO USAR PULSOS."),
        
        Tratamiento("brain", "Salud Cerebral", "Cabeza", "SOLO NIR", "100%", "30 cm", 10, 1, 5, "PERMANENTE", ['All'], "FLEX", "Mañana o Tarde",
                    momentos_prohibidos=["🌙 Noche"],
                    tips_antes=["🕶️ GAFAS PUESTAS."],
                    tips_despues=["🧠 Tarea cognitiva."])
        .set_incompatibilidades("⛔ GAFAS OBLIGATORIAS.")
    ]
    return catalogo

# --- GESTIÓN DE DATOS ---
def cargar_datos_completos():
    if not os.path.exists(ARCHIVO_DATOS):
        return {"usuario_rutina": {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}, 
                "usuario_libre": {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}}
    try:
        with open(ARCHIVO_DATOS, 'r') as f:
            datos = json.load(f)
            for user in ["usuario_rutina", "usuario_libre"]:
                if user not in datos: datos[user] = {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}
            return datos
    except:
        return {"usuario_rutina": {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}, 
                "usuario_libre": {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}}

def guardar_datos_completos(datos):
    with open(ARCHIVO_DATOS, 'w') as f:
        json.dump(datos, f, indent=4)

# --- LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user_role' not in st.session_state: st.session_state.current_user_role = None

def login_screen():
    st.title("🔐 Acceso Mega Panel")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        usr = st.selectbox("Usuario", ["Seleccionar...", "Benja", "Eva"])
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Entrar", use_container_width=True):
            if usr != "Seleccionar...":
                st.session_state.logged_in = True
                st.session_state.current_user_name = usr
                st.session_state.current_user_role = "usuario_rutina" if usr == "Benja" else "usuario_libre"
                st.rerun()

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# --- CARGA GLOBAL ---
if 'db_global' not in st.session_state:
    st.session_state.db_global = cargar_datos_completos()

clave_usuario = st.session_state.current_user_role
db_usuario = st.session_state.db_global[clave_usuario]
lista_tratamientos = obtener_catalogo()

# --- SIDEBAR NAVEGACIÓN ---
with st.sidebar:
    st.write(f"Hola, **{st.session_state.current_user_name}**")
    menu_navegacion = st.radio("Menú", ["📅 Panel Diario", "🚑 Clínica de Lesiones"])
    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

# ==========================================
# PANTALLA 1: CLÍNICA DE LESIONES
# ==========================================
if menu_navegacion == "🚑 Clínica de Lesiones":
    st.title("🚑 Gestión de Recuperación")
    st.markdown("Inicia, sigue o cancela tratamientos de larga duración (lesiones).")
    
    tratamientos_lesion = [t for t in lista_tratamientos if t.tipo == "LESION"]
    
    for t in tratamientos_lesion:
        ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
        activo = ciclo and ciclo.get('activo')
        
        container = st.container(border=True)
        with container:
            c1, c2 = st.columns([3, 1])
            c1.subheader(f"{t.nombre}")
            c1.caption(f"Zona: {t.zona} | {t.distancia}")
            
            if activo:
                inicio = datetime.date.fromisoformat(ciclo['fecha_inicio'])
                dias = (datetime.date.today() - inicio).days
                
                fase_txt = "Mantenimiento"
                progreso = 0.0
                color_barra = "blue"
                
                if ciclo.get('modo') == 'fases':
                    for f in t.fases_config:
                        if dias <= f['dias_fin']:
                            fase_txt = f['nombre']
                            progreso = min(dias / 60, 1.0)
                            break
                    if dias > 60: fase_txt = "Ciclo Finalizado"; progreso = 1.0; color_barra = "green"
                
                c1.info(f"✅ **EN CURSO** | **Fase:** {fase_txt} | **Día:** {dias}")
                c1.progress(progreso)
                
                col_stop, col_restart = c1.columns(2)
                if col_stop.button("🛑 Cancelar Tratamiento", key=f"stop_{t.id}"):
                    del db_usuario["ciclos_activos"][t.id]
                    guardar_datos_completos(st.session_state.db_global)
                    st.rerun()
                if col_restart.button("🔄 Reiniciar Protocolo", key=f"res_clinic_{t.id}"):
                    db_usuario["ciclos_activos"][t.id] = {"fecha_inicio": datetime.date.today().isoformat(), "activo": True, "modo": "fases"}
                    guardar_datos_completos(st.session_state.db_global)
                    st.rerun()
            else:
                c2.button("🚀 Iniciar", key=f"start_clinic_{t.id}", type="primary", on_click=lambda id=t.id: 
                          db_usuario.setdefault("ciclos_activos", {}).update({id: {"fecha_inicio": datetime.date.today().isoformat(), "activo": True, "modo": "fases"}}) 
                          or guardar_datos_completos(st.session_state.db_global))

# ==========================================
# PANTALLA 2: PANEL DIARIO
# ==========================================
elif menu_navegacion == "📅 Panel Diario":
    
    # FUNCIONES LOCALES
    def analizar_bloqueos(tratamiento, momento_elegido, historial_usuario, tratamientos_hoy, fecha_actual_str):
        if momento_elegido in tratamiento.momentos_prohibidos:
            return True, f"⛔ HORARIO PROHIBIDO: '{tratamiento.nombre}' no apto en '{momento_elegido}'."
        
        dias_hechos = 0
        fecha_dt = datetime.date.fromisoformat(fecha_actual_str)
        for i in range(7):
            f_check = (fecha_dt - timedelta(days=i)).isoformat()
            if f_check in historial_usuario and tratamiento.id in historial_usuario[f_check]:
                dias_hechos += 1
        
        hoy_hecho = (fecha_actual_str in historial_usuario and tratamiento.id in historial_usuario[fecha_actual_str])
        if not hoy_hecho and dias_hechos >= tratamiento.max_semanal:
            return True, f"⛔ LÍMITE SEMANAL ({tratamiento.max_semanal}/sem). Descansa hoy."

        ids_hoy = list(tratamientos_hoy.keys())
        if tratamiento.id == "brain" and "sleep" in ids_hoy: return True, "⛔ CHOQUE: Ya hay Sueño. No cerebro."
        if tratamiento.id == "sleep" and "brain" in ids_hoy: return True, "⛔ CHOQUE: Ya hay Cerebro. No sueño."
        
        return False, ""

    def check_cross_compatibility(nuevo_id, lista_ids_actuales):
        incompatibles = {"brain": ["sleep"], "sleep": ["brain"]}
        if nuevo_id in incompatibles:
            for proh in incompatibles[nuevo_id]:
                if proh in lista_ids_actuales: return True, proh, "Incompatibles."
        return False, None, None

    st.title("📅 Panel Diario")
    c_f, c_r = st.columns([2,1])
    fecha_seleccionada = c_f.date_input("Fecha", datetime.date.today())
    fecha_str = fecha_seleccionada.isoformat()
    
    # SELECCIÓN
    tags_dia = set()
    ids_seleccionados_libre = []
    
    if clave_usuario == "usuario_rutina":
        entreno = db_usuario.get("meta_diaria", {}).get(fecha_str, [])
        opciones = {"Descanso": [], "Cardio": ["Active"], "FULLBODY": ["Upper", "Active"], "TORSO": ["Upper", "Active"], "PREVENTIVO": ["Active"]}
        sel = st.multiselect("Rutina hoy:", list(opciones.keys()), default=[x for x in entreno if x in opciones])
        if sel: 
            for r in sel: tags_dia.update(opciones[r])
        if sel != entreno:
            if "meta_diaria" not in db_usuario: db_usuario["meta_diaria"] = {}
            db_usuario["meta_diaria"][fecha_str] = sel
            guardar_datos_completos(st.session_state.db_global)
            st.rerun()
    else:
        ids_guardados = db_usuario.get("meta_diaria", {}).get(fecha_str, [])
        mapa_n = {t.nombre: t.id for t in lista_tratamientos}
        mapa_i = {t.id: t.nombre for t in lista_tratamientos}
        
        sel_nombres = st.multiselect("Tratamientos hoy:", list(mapa_n.keys()), 
                                     default=[mapa_i[i] for i in ids_guardados if i in mapa_i])
        
        nuevos_ids = [mapa_n[n] for n in sel_nombres]
        
        agregados = set(nuevos_ids) - set(ids_guardados)
        if agregados:
            for nid in agregados:
                bad, rival, mot = check_cross_compatibility(nid, ids_guardados)
                if bad:
                    st.error(f"⛔ Conflicto entre {mapa_i[nid]} y {mapa_i[rival]}.")
                    c1, c2 = st.columns(2)
                    if c1.button(f"Mantener {mapa_i[rival]}"): st.rerun()
                    if c2.button(f"Cambiar a {mapa_i[nid]}"):
                        final = [x for x in ids_guardados if x != rival] + [nid]
                        if "meta_diaria" not in db_usuario: db_usuario["meta_diaria"] = {}
                        db_usuario["meta_diaria"][fecha_str] = final
                        guardar_datos_completos(st.session_state.db_global)
                        st.rerun()
                    st.stop()
        
        if set(nuevos_ids) != set(ids_guardados):
            if "meta_diaria" not in db_usuario: db_usuario["meta_diaria"] = {}
            db_usuario["meta_diaria"][fecha_str] = nuevos_ids
            guardar_datos_completos(st.session_state.db_global)
            st.rerun()
        ids_seleccionados_libre = ids_guardados

    st.divider()
    
    # RENDERIZADO
    registros_dia = db_usuario["historial"].get(fecha_str, {})
    descartados = db_usuario.get("descartados", {}).get(fecha_str, [])
    
    grupos = {"PRE": [], "POST": [], "MORNING": [], "NIGHT": [], "FLEX": [], "COMPLETED": [], "HIDDEN": [], "DISCARDED": []}
    mapa_vis = {"🏋️ Antes de Entrenar": "PRE", "🧘 Después de Entrenar": "POST", "🌞 Mañana": "MORNING", "🌙 Noche": "NIGHT"}

    for t in lista_tratamientos:
        aplica = False
        if clave_usuario == "usuario_rutina":
            if t.tipo == "PERMANENTE": aplica = True
            elif t.tipo == "LESION":
                ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
                if ciclo and ciclo['activo']: aplica = True
            elif t.tipo == "GRASA" and "Active" in tags_dia: aplica = True
            elif t.tipo == "MUSCULAR" and "Upper" in tags_dia: aplica = True
        else:
            if t.id in ids_seleccionados_libre: aplica = True
            elif len(registros_dia.get(t.id, [])) > 0: aplica = True
        
        hechos = len(registros_dia.get(t.id, []))
        if t.id in descartados: grupos["DISCARDED"].append(t)
        elif not aplica: grupos["HIDDEN"].append(t)
        elif hechos >= t.max_diario: grupos["COMPLETED"].append(t)
        else:
            g = t.default_visual_group
            rad_key = f"rad_{t.id}_{clave_usuario}"
            if rad_key in st.session_state and st.session_state[rad_key] in mapa_vis:
                g = mapa_vis[st.session_state[rad_key]]
            elif hechos > 0:
                last = registros_dia[t.id][-1]['detalle']
                for k, v in mapa_vis.items():
                    if k in last: g = v
            if g in grupos: grupos[g].append(t)
            else: grupos["FLEX"].append(t)

    def render_card(t, modo="normal"):
        hechos = len(registros_dia.get(t.id, []))
        icon = "❌" if modo=="discarded" else ("✅" if hechos>=t.max_diario else "⬜")
        
        info_extra = ""
        if t.tipo == "LESION":
            ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
            if ciclo and ciclo['activo']:
                dias = (datetime.date.fromisoformat(fecha_str) - datetime.date.fromisoformat(ciclo['fecha_inicio'])).days
                info_extra = f" (Día {dias})"
        
        with st.expander(f"{icon} {t.nombre} ({hechos}/{t.max_diario}){info_extra}"):
            if modo=="discarded":
                if st.button("Recuperar", key=f"rec_{t.id}"):
                    db_usuario["descartados"][fecha_str].remove(t.id)
                    guardar_datos_completos(st.session_state.db_global)
                    st.rerun()
                return

            if modo!="readonly":
                st.success(f"💡 Mejor: {t.momento_ideal_txt}")
                c1, c2 = st.columns(2)
                with c1: 
                    st.markdown("**Antes:**")
                    for x in t.tips_antes: st.caption(f"• {x}")
                with c2:
                    st.markdown("**Después:**")
                    for x in t.tips_despues: st.caption(f"• {x}")
                if t.incompatibilidades: st.error(f"⚠️ {t.incompatibilidades}")

            if hechos > 0:
                st.markdown("---")
                for i, r in enumerate(registros_dia.get(t.id, [])):
                    c_t, c_d = st.columns([5,1])
                    c_t.info(f"✅ {r['hora']} ({r['detalle']})")
                    if c_d.button("🗑️", key=f"d_{t.id}_{i}"):
                        registros_dia[t.id].pop(i)
                        if not registros_dia[t.id]: del registros_dia[t.id]
                        guardar_datos_completos(st.session_state.db_global)
                        st.rerun()

            if modo=="normal" and hechos < t.max_diario:
                st.markdown("---")
                opts = ["🏋️ Antes de Entrenar", "🧘 Después de Entrenar", "🌞 Mañana", "⛅ Tarde", "🌙 Noche"]
                valid = [o for o in opts if o not in t.momentos_prohibidos]
                
                sel = st.radio("Momento:", valid, key=f"rad_{t.id}_{clave_usuario}")
                
                bloq, mot = analizar_bloqueos(t, sel, db_usuario["historial"], registros_dia, fecha_str)
                
                c_go, c_no = st.columns([3,1])
                with c_go:
                    if bloq:
                        st.error(mot)
                        st.button("🚫 Bloqueado", disabled=True, key=f"bx_{t.id}")
                    else:
                        if st.button(f"Registrar", key=f"go_{t.id}"):
                            now = datetime.datetime.now().strftime('%H:%M')
                            if fecha_str not in db_usuario["historial"]: db_usuario["historial"][fecha_str] = {}
                            if t.id not in db_usuario["historial"][fecha_str]: db_usuario["historial"][fecha_str][t.id] = []
                            db_usuario["historial"][fecha_str][t.id].append({"hora": now, "detalle": sel})
                            guardar_datos_completos(st.session_state.db_global)
                            st.rerun()
                with c_no:
                    if st.button("Omitir", key=f"om_{t.id}"):
                        if "descartados" not in db_usuario: db_usuario["descartados"] = {}
                        if fecha_str not in db_usuario["descartados"]: db_usuario["descartados"][fecha_str] = []
                        db_usuario["descartados"][fecha_str].append(t.id)
                        guardar_datos_completos(st.session_state.db_global)
                        st.rerun()

        # Botones de inicio rápido para Lesiones en panel diario (solo si no activos)
        if t.tipo == "LESION":
            ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
            if not (ciclo and ciclo.get('activo')):
                if st.button("🚀 Iniciar Tratamiento", key=f"fast_start_{t.id}"):
                    if "ciclos_activos" not in db_usuario: db_usuario["ciclos_activos"] = {}
                    db_usuario["ciclos_activos"][t.id] = {"fecha_inicio": fecha_str, "activo": True, "modo": "fases"}
                    guardar_datos_completos(st.session_state.db_global)
                    st.rerun()

    # LOOP VISUAL
    cats = ["MORNING", "PRE", "POST", "NIGHT", "FLEX"]
    for c in cats:
        if grupos[c]:
            st.subheader(c)
            for t in grupos[c]: render_card(t)
    
    if grupos["COMPLETED"]:
        st.markdown("### ✅ Completados")
        for t in grupos["COMPLETED"]: render_card(t, "readonly")
        
    if grupos["DISCARDED"]:
        st.markdown("### ❌ Descartados")
        for t in grupos["DISCARDED"]: render_card(t, "discarded")
        
    if grupos["HIDDEN"] and clave_usuario == "usuario_rutina":
        with st.expander("Inactivos"):
            for t in grupos["HIDDEN"]: st.write(t.nombre)
