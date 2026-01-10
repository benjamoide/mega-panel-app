import streamlit as st
import datetime
from datetime import timedelta
import json
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Mega Panel AI",
    page_icon="🛡️",
    layout="centered"
)

# --- GESTIÓN DE SESIÓN Y LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user_name' not in st.session_state:
    st.session_state.current_user_name = None
if 'current_user_role' not in st.session_state:
    st.session_state.current_user_role = None # 'usuario_rutina' o 'usuario_libre'

def login():
    st.title("🔐 Acceso Seguro")
    st.markdown("Selecciona tu perfil para cargar tu configuración personalizada.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        usuario = st.selectbox("Usuario", ["Seleccionar...", "Benja", "Eva"])
        password = st.text_input("Contraseña", type="password")
        
        if st.button("Entrar", use_container_width=True):
            if usuario == "Seleccionar...":
                st.error("Por favor selecciona un usuario.")
            else:
                # Lógica de asignación de roles
                st.session_state.logged_in = True
                st.session_state.current_user_name = usuario
                
                if usuario == "Benja":
                    st.session_state.current_user_role = "usuario_rutina"
                elif usuario == "Eva":
                    st.session_state.current_user_role = "usuario_libre"
                
                st.rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.current_user_name = None
    st.session_state.current_user_role = None
    st.rerun()

# SI NO ESTÁ LOGUEADO, MOSTRAR LOGIN Y DETENER EL RESTO
if not st.session_state.logged_in:
    login()
    st.stop()

# --- SI PASA EL LOGIN, CARGAMOS EL RESTO DE LA APP ---

# SIDEBAR: DATOS DEL USUARIO Y LOGOUT
with st.sidebar:
    st.write(f"Hola, **{st.session_state.current_user_name}** 👋")
    st.caption(f"Perfil: {st.session_state.current_user_role}")
    if st.button("🔒 Cerrar Sesión"):
        logout()

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
        # --- REJUVENECIMIENTO FACIAL ---
        Tratamiento("face_rejuv", "Rejuvenecimiento Facial", "Cara/Cuello", "RED + NIR", "50%", "30-50 cm", 10, 1, 5, "PERMANENTE", ['All'], "FLEX", "Cualquier hora (Piel Limpia)",
                    momentos_prohibidos=["🏋️ Antes de Entrenar"],
                    tips_antes=["🧼 DOBLE LIMPIEZA.", "🕶️ GAFAS OBLIGATORIAS.", "🧴 No Retinol."],
                    tips_despues=["🧴 Serum hidratante.", "❌ No sol directo."])
        .set_incompatibilidades("Melasma, Fotosensibilidad."),

        # --- GRASA ---
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

        # --- LESIONES (Con Fases) ---
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
        
        # --- MÚSCULO ---
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
            # Asegurar estructura
            for user in ["usuario_rutina", "usuario_libre"]:
                if user not in datos: datos[user] = {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}
            return datos
    except:
        return {"usuario_rutina": {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}, 
                "usuario_libre": {"historial": {}, "meta_diaria": {}, "ciclos_activos": {}, "descartados": {}}}

def guardar_datos_completos(datos):
    with open(ARCHIVO_DATOS, 'w') as f:
        json.dump(datos, f, indent=4)

# --- VALIDACIONES ESTRICTAS ---
def analizar_bloqueos(tratamiento, momento_elegido, historial_usuario, tratamientos_hoy, fecha_actual_str):
    # 1. BLOQUEO HORARIO
    if momento_elegido in tratamiento.momentos_prohibidos:
        return True, f"⛔ HORARIO PROHIBIDO: '{tratamiento.nombre}' no se puede hacer en '{momento_elegido}'."

    # 2. BLOQUEO FRECUENCIA (Últimos 7 días)
    dias_hechos_semana = 0
    fecha_dt = datetime.date.fromisoformat(fecha_actual_str)
    for i in range(7):
        f_check = (fecha_dt - timedelta(days=i)).isoformat()
        if f_check in historial_usuario and tratamiento.id in historial_usuario[f_check]:
            dias_hechos_semana += 1
    
    hoy_hecho = (fecha_actual_str in historial_usuario and tratamiento.id in historial_usuario[fecha_actual_str])
    if not hoy_hecho and dias_hechos_semana >= tratamiento.max_semanal:
        return True, f"⛔ LÍMITE SEMANAL ALCANZADO ({tratamiento.max_semanal} días). Toca descanso."

    # 3. BLOQUEO CHOQUES BIOLÓGICOS
    ids_hoy = list(tratamientos_hoy.keys())
    if tratamiento.id == "brain" and "sleep" in ids_hoy:
        return True, "⛔ CHOQUE: Ya hiciste 'Sueño'. No actives cerebro."
    if tratamiento.id == "sleep" and "brain" in ids_hoy:
        return True, "⛔ CHOQUE: Ya hiciste 'Cerebro'. No induzcas sueño profundo."

    return False, ""

def calcular_progreso_fase(tratamiento, ciclo_info, historial_completo, id_tratamiento):
    if not ciclo_info or not ciclo_info.get('activo'): return None
    if ciclo_info.get('modo') == 'mantenimiento': return "🛠️ Mantenimiento (Sin fases)"

    fecha_inicio = datetime.date.fromisoformat(ciclo_info['fecha_inicio'])
    hoy = datetime.date.today()
    dias_transcurridos = (hoy - fecha_inicio).days
    
    sesiones_totales = 0
    for fecha_reg_str, tratamientos_dia in historial_completo.items():
        if datetime.date.fromisoformat(fecha_reg_str) >= fecha_inicio and id_tratamiento in tratamientos_dia:
            sesiones_totales += len(tratamientos_dia[id_tratamiento])

    fase_actual_obj = None
    for idx, fase in enumerate(tratamiento.fases_config):
        if dias_transcurridos <= fase['dias_fin']:
            fase_actual_obj = fase
            break
    
    if not fase_actual_obj: return "🏁 Ciclo Completado."
    return f"📍 {fase_actual_obj['nombre']} | Día {dias_transcurridos}/{fase_actual_obj['dias_fin']} | Sesiones: {sesiones_totales}"

# --- DETECCIÓN DE CONFLICTOS AL AÑADIR (Solo modo Libre) ---
def check_cross_compatibility(nuevo_id, lista_ids_actuales):
    incompatibles = {"brain": ["sleep"], "sleep": ["brain"]}
    if nuevo_id in incompatibles:
        for prohibido in incompatibles[nuevo_id]:
            if prohibido in lista_ids_actuales:
                return True, prohibido, "Incompatibles: Uno activa y otro relaja."
    return False, None, None


# --- APP START ---
st.title(f"🧠 Mega Panel AI")

if 'db_global' not in st.session_state:
    st.session_state.db_global = cargar_datos_completos()

# VARIABLES DE CONTEXTO SEGÚN LOGIN
clave_usuario = st.session_state.current_user_role
db_usuario = st.session_state.db_global[clave_usuario]
lista_tratamientos = obtener_catalogo()

c_fecha, c_resumen = st.columns([2, 1])
with c_fecha:
    fecha_seleccionada = st.date_input("📅 Fecha", datetime.date.today())
    fecha_str = fecha_seleccionada.isoformat()

# --- SELECCIÓN ---
tags_dia = set()
ids_seleccionados_libre = []

if clave_usuario == "usuario_rutina":
    # MODO RUTINA (BENJA)
    entreno = db_usuario.get("meta_diaria", {}).get(fecha_str, [])
    # Aquí puedes restaurar tu mapeo complejo del Excel si lo deseas
    opciones = {"Descanso": [], "Cardio": ["Active"], "FULLBODY": ["Upper", "Active"], "TORSO": ["Upper", "Active"], "PREVENTIVO": ["Active"]}
    noms = list(opciones.keys())
    # Simplificación para el ejemplo, pero aquí conectaría tu lógica original
    sel = st.multiselect("Rutina:", noms, default=[x for x in entreno if x in noms])
    if sel: 
        for r in sel: tags_dia.update(opciones[r])
    if sel != entreno:
        db_usuario["meta_diaria"] = db_usuario.get("meta_diaria", {})
        db_usuario["meta_diaria"][fecha_str] = sel
        guardar_datos_completos(st.session_state.db_global)
        st.rerun()

else:
    # MODO LIBRE (EVA)
    st.info("🔓 Modo Libre: Elige tratamientos.")
    ids_guardados = db_usuario.get("meta_diaria", {}).get(fecha_str, [])
    mapa_nombres = {t.nombre: t.id for t in lista_tratamientos}
    mapa_ids = {t.id: t.nombre for t in lista_tratamientos}
    
    sel_nombres = st.multiselect("Tratamientos hoy:", list(mapa_nombres.keys()), 
                                 default=[mapa_ids[i] for i in ids_guardados if i in mapa_ids],
                                 key="multi_libre")
    
    nuevos_ids = [mapa_nombres[n] for n in sel_nombres]
    
    # Check conflictos al añadir
    agregados = set(nuevos_ids) - set(ids_guardados)
    if agregados:
        for nid in agregados:
            conflicto, rival, mot = check_cross_compatibility(nid, ids_guardados)
            if conflicto:
                st.error(f"⛔ Choque entre {mapa_ids[nid]} y {mapa_ids[rival]}. {mot}")
                c1, c2 = st.columns(2)
                if c1.button(f"Quedarse con {mapa_ids[rival]}"): st.rerun()
                if c2.button(f"Cambiar a {mapa_ids[nid]}"):
                    final = [x for x in ids_guardados if x != rival] + [nid]
                    db_usuario["meta_diaria"] = db_usuario.get("meta_diaria", {})
                    db_usuario["meta_diaria"][fecha_str] = final
                    guardar_datos_completos(st.session_state.db_global)
                    st.rerun()
                st.stop()
    
    if set(nuevos_ids) != set(ids_guardados):
        db_usuario["meta_diaria"] = db_usuario.get("meta_diaria", {})
        db_usuario["meta_diaria"][fecha_str] = nuevos_ids
        guardar_datos_completos(st.session_state.db_global)
        st.rerun()
    ids_seleccionados_libre = ids_guardados

st.divider()

# --- MOTOR VISUAL ---
registros_dia = db_usuario["historial"].get(fecha_str, {})
descartados = db_usuario.get("descartados", {}).get(fecha_str, [])

grupos = {"PRE": [], "POST": [], "MORNING": [], "NIGHT": [], "FLEX": [], "COMPLETED": [], "HIDDEN": [], "DISCARDED": []}
mapa_momento = {"🏋️ Antes de Entrenar": "PRE", "🧘 Después de Entrenar": "POST", "🌞 Mañana": "MORNING", "🌙 Noche": "NIGHT"}

for t in lista_tratamientos:
    aplica = False
    es_ciclo = False
    if clave_usuario == "usuario_rutina":
        if t.tipo == "PERMANENTE": aplica = True
        elif t.tipo == "LESION":
            ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
            if ciclo and ciclo['activo']: aplica = True; es_ciclo = True
        elif t.tipo == "GRASA" and "Active" in tags_dia: aplica = True
        elif t.tipo == "MUSCULAR" and "Upper" in tags_dia: aplica = True
    else:
        if t.id in ids_seleccionados_libre: 
            aplica = True
            if t.tipo == "LESION":
                 ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
                 if ciclo and ciclo['activo']: es_ciclo = True
        elif len(registros_dia.get(t.id, [])) > 0: aplica = True # Mantener si ya tiene historial

    hechos = len(registros_dia.get(t.id, []))
    if t.id in descartados: grupos["DISCARDED"].append((t, es_ciclo))
    elif not aplica: grupos["HIDDEN"].append((t, False))
    elif hechos >= t.max_diario: grupos["COMPLETED"].append((t, es_ciclo))
    else:
        grp = t.default_visual_group
        rad_key = f"rad_{t.id}_{clave_usuario}"
        if rad_key in st.session_state and st.session_state[rad_key] in mapa_momento:
            grp = mapa_momento[st.session_state[rad_key]]
        elif hechos > 0:
            last = registros_dia[t.id][-1]['detalle']
            for k, v in mapa_momento.items(): 
                if k in last: grp = v
        if grp in grupos: grupos[grp].append((t, es_ciclo))
        else: grupos["FLEX"].append((t, es_ciclo))

# --- RENDERIZADOR ---
def render(t, es_ciclo, modo="normal"):
    txt_fase = ""
    if t.tipo == "LESION" and es_ciclo:
        ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
        txt_fase = calcular_progreso_fase(t, ciclo, db_usuario["historial"], t.id)
    
    hechos = len(registros_dia.get(t.id, []))
    icono = "❌" if modo=="discarded" else ("✅" if hechos>=t.max_diario else "⬜")
    
    with st.expander(f"{icono} {t.nombre} ({hechos}/{t.max_diario})"):
        if txt_fase: st.info(txt_fase)
        
        if modo == "discarded":
            if st.button("↩️ Recuperar", key=f"rec_{t.id}"):
                db_usuario["descartados"][fecha_str].remove(t.id)
                guardar_datos_completos(st.session_state.db_global)
                st.rerun()
            return
            
        if modo != "readonly":
            st.caption(f"📍 Ideal: {t.momento_ideal_txt}")
            c1, c2 = st.columns(2)
            with c1: 
                st.markdown("**Antes:**")
                for x in t.tips_antes: st.caption(f"- {x}")
            with c2: 
                st.markdown("**Después:**")
                for x in t.tips_despues: st.caption(f"- {x}")
            if t.incompatibilidades: st.warning(f"⚠️ {t.incompatibilidades}")

        if hechos > 0:
            st.markdown("---")
            for i, r in enumerate(registros_dia.get(t.id, [])):
                c_txt, c_del = st.columns([5,1])
                c_txt.success(f"✅ {r['hora']} - {r['detalle']}")
                if c_del.button("🗑️", key=f"d_{t.id}_{i}"):
                    registros_dia[t.id].pop(i)
                    if not registros_dia[t.id]: del registros_dia[t.id]
                    guardar_datos_completos(st.session_state.db_global)
                    st.rerun()

        if modo == "normal" and hechos < t.max_diario:
            st.markdown("---")
            # FILTRAR MOMENTOS PROHIBIDOS
            all_opts = ["🏋️ Antes de Entrenar", "🧘 Después de Entrenar", "🌞 Mañana", "⛅ Tarde", "🌙 Noche"]
            valid_opts = [o for o in all_opts if o not in t.momentos_prohibidos]
            
            sel = st.radio("Momento:", valid_opts, key=f"rad_{t.id}_{clave_usuario}")
            
            # CHECK BLOQUEOS
            bloqueado, motivo = analizar_bloqueos(t, sel, db_usuario["historial"], registros_dia, fecha_str)
            
            c_reg, c_omit = st.columns([3, 1])
            with c_reg:
                if bloqueado:
                    st.error(motivo)
                    st.button("🚫 Bloqueado", disabled=True, key=f"no_{t.id}")
                else:
                    if st.button(f"Registrar ({hechos+1})", key=f"go_{t.id}"):
                        now = datetime.datetime.now().strftime('%H:%M')
                        if fecha_str not in db_usuario["historial"]: db_usuario["historial"][fecha_str] = {}
                        if t.id not in db_usuario["historial"][fecha_str]: db_usuario["historial"][fecha_str][t.id] = []
                        db_usuario["historial"][fecha_str][t.id].append({"hora": now, "detalle": sel})
                        guardar_datos_completos(st.session_state.db_global)
                        st.rerun()
            with c_omit:
                if st.button("🚫 Omitir", key=f"om_{t.id}"):
                    if "descartados" not in db_usuario: db_usuario["descartados"] = {}
                    if fecha_str not in db_usuario["descartados"]: db_usuario["descartados"][fecha_str] = []
                    db_usuario["descartados"][fecha_str].append(t.id)
                    guardar_datos_completos(st.session_state.db_global)
                    st.rerun()

        if t.tipo == "LESION":
            if not es_ciclo:
                c_ini, c_mant = st.columns(2)
                if c_ini.button("🚀 Iniciar Protocolo", key=f"ini_{t.id}"):
                    if "ciclos_activos" not in db_usuario: db_usuario["ciclos_activos"] = {}
                    db_usuario["ciclos_activos"][t.id] = {"fecha_inicio": fecha_str, "activo": True, "modo": "fases"}
                    guardar_datos_completos(st.session_state.db_global)
                    st.rerun()
                if c_mant.button("🛠️ Mantenimiento", key=f"man_{t.id}"):
                    if "ciclos_activos" not in db_usuario: db_usuario["ciclos_activos"] = {}
                    db_usuario["ciclos_activos"][t.id] = {"fecha_inicio": fecha_str, "activo": True, "modo": "mantenimiento"}
                    guardar_datos_completos(st.session_state.db_global)
                    st.rerun()
            else:
                 if st.button("🔄 Reiniciar", key=f"res_{t.id}"):
                     del db_usuario["ciclos_activos"][t.id]
                     guardar_datos_completos(st.session_state.db_global)
                     st.rerun()

# --- RENDERIZAR SECCIONES ---
cats = ["MORNING", "PRE", "POST", "NIGHT", "FLEX"]
for c in cats:
    if grupos[c]:
        st.subheader(c)
        for tr, cy in grupos[c]: render(tr, cy)

if grupos["COMPLETED"]:
    st.markdown("### ✅ Hecho")
    for tr, cy in grupos["COMPLETED"]: render(tr, cy, "readonly")
    
if grupos["DISCARDED"]:
    st.markdown("### ❌ Descartado")
    for tr, cy in grupos["DISCARDED"]: render(tr, cy, "discarded")

if grupos["HIDDEN"]:
    st.markdown("---")
    with st.expander("Inactivos"):
        for tr, _ in grupos["HIDDEN"]: st.write(tr.nombre)
