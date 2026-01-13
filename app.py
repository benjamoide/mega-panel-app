import streamlit as st
import datetime
from datetime import timedelta
import json
import os
import pandas as pd
import uuid

# --- INTEGRACIÓN OPENAI ---
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Mega Panel AI",
    page_icon="🧬",
    layout="centered"
)

# --- ARCHIVO DE DATOS ---
ARCHIVO_DATOS = 'historial_mega_panel_pro.json'

# ==============================================================================
# 1. CONSTANTES, RUTINAS Y CONFIGURACIÓN
# ==============================================================================

RUTINA_SEMANAL = {
    "0": ["FULLBODY I"],           # Lunes
    "1": ["TORSO I"],              # Martes
    "2": ["FULLBODY II"],          # Miércoles
    "3": ["TORSO II / CIRCUITO"],  # Jueves
    "4": ["PREVENTIVO I"],         # Viernes
    "5": ["PREVENTIVO II"],        # Sábado
    "6": ["Descanso Total"]        # Domingo
}

CARDIO_DEFAULTS_BY_DAY = {
    "0": {"actividad": "Remo Ergómetro", "tiempo": 8, "ritmo": "Intenso"},
    "2": {"actividad": "Cinta Inclinada", "tiempo": 20, "velocidad": 6.5, "inclinacion": 4},
    "5": {"actividad": "Cinta Inclinada", "tiempo": 15, "velocidad": 6.5, "inclinacion": 4}
}

GENERIC_CARDIO_PARAMS = {
    "Remo Ergómetro": {"tiempo": 8, "ritmo": "Intenso"},
    "Cinta Inclinada": {"tiempo": 15, "velocidad": 6.5, "inclinacion": 4},
    "Elíptica": {"tiempo": 15, "velocidad": 6.5},
    "Andar": {"tiempo": 15},
    "Andar (Pasos)": {"pasos": 10000},
    "Descanso Cardio": {}
}

TAGS_ACTIVIDADES = {
    "FULLBODY I": ["Upper", "Lower", "Active"], 
    "TORSO I": ["Upper", "Active"],
    "PREVENTIVO I": ["Active"], 
    "FULLBODY II": ["Upper", "Lower", "Active"],
    "TORSO + CIRCUITO": ["Upper", "Active", "Cardio"], 
    "PREVENTIVO II": ["Active"],
    "Descanso Total": [],
    
    "Remo Ergómetro": ["Active", "Cardio", "Upper", "Lower"],
    "Cinta Inclinada": ["Active", "Cardio", "Lower"],
    "Elíptica": ["Active", "Cardio", "Lower"],
    "Andar": ["Active", "Lower"],
    "Andar (Pasos)": ["Active", "Lower"],
    "Descanso Cardio": []
}

# ==============================================================================
# 2. DEFINICIÓN MAESTRA DE PATOLOGÍAS (CATÁLOGO EXTENDIDO)
# ==============================================================================
DB_TRATAMIENTOS_BASE = {
    "Codo": {
        "Epicondilitis (Tenista)": {
            "ondas": "660+850",
            "energia": "660nm: 50% | 850nm: 100%",
            "hz": "50Hz (Dolor)",
            "dist": "Contacto",
            "dur": 10,
            "tips_ant": ["Piel limpia"],
            "tips_des": ["No pinza con dedos", "Hielo si dolor"]
        },
        "Epitrocleitis (Golfista)": {
            "ondas": "660+850",
            "energia": "660nm: 50% | 850nm: 100%",
            "hz": "50Hz (Dolor)",
            "dist": "Contacto",
            "dur": 10,
            "tips_ant": ["Piel limpia"],
            "tips_des": ["Estirar flexores"]
        },
        "Calcificación": {
            "ondas": "850nm",
            "energia": "660nm: 0% | 850nm: 100%",
            "hz": "50Hz (Analgesia)",
            "dist": "Contacto",
            "dur": 12,
            "tips_ant": ["Calor previo"],
            "tips_des": ["Movilidad suave"]
        },
        "Bursitis (Apoyo)": {
            "ondas": "660+850",
            "energia": "660nm: 50% | 850nm: 100%",
            "hz": "10Hz (Anti-inflamatorio)",
            "dist": "5cm",
            "dur": 10,
            "tips_ant": ["Zona limpia"],
            "tips_des": ["No apoyar codo"]
        }
    },
    "Espalda": {
        "Cervicalgia (Cuello)": {
            "ondas": "660+850",
            "energia": "660nm: 50% | 850nm: 100%",
            "hz": "50Hz (Dolor)",
            "dist": "10cm",
            "dur": 15,
            "tips_ant": ["Sin collar"],
            "tips_des": ["Movilidad suave"]
        },
        "Dorsalgia (Alta)": {
            "ondas": "660+850",
            "energia": "660nm: 50% | 850nm: 100%",
            "hz": "50Hz",
            "dist": "15cm",
            "dur": 15,
            "tips_ant": ["Postura recta"],
            "tips_des": ["Estirar pecho"]
        },
        "Lumbalgia (Baja)": {
            "ondas": "660+850",
            "energia": "660nm: 50% | 850nm: 100%",
            "hz": "50Hz (Dolor)",
            "dist": "10cm",
            "dur": 20,
            "tips_ant": ["Calor previo"],
            "tips_des": ["No cargar peso"]
        }
    },
    "Antebrazo": {
        "Sobrecarga": {
            "ondas": "660+850",
            "energia": "660nm: 80% | 850nm: 80%",
            "hz": "10Hz (Relajación)",
            "dist": "15cm",
            "dur": 12,
            "tips_ant": ["Quitar sudor"],
            "tips_des": ["Estirar", "Calor"]
        },
        "Tendinitis": {
            "ondas": "660+850",
            "energia": "660nm: 50% | 850nm: 100%",
            "hz": "50Hz (Dolor)",
            "dist": "10cm",
            "dur": 10,
            "tips_ant": ["Quitar reloj"],
            "tips_des": ["Reposo"]
        }
    },
    "Muñeca": {
        "Túnel Carpiano": {
            "ondas": "660+850",
            "energia": "660nm: 50% | 850nm: 100%",
            "hz": "10Hz (Nervio)",
            "dist": "5cm",
            "dur": 10,
            "tips_ant": ["Palma abierta"],
            "tips_des": ["Movilidad"]
        },
        "Articular": {
            "ondas": "660+850",
            "energia": "660nm: 50% | 850nm: 100%",
            "hz": "50Hz",
            "dist": "5cm",
            "dur": 10,
            "tips_ant": ["Sin muñequera"],
            "tips_des": ["Hielo"]
        }
    },
    "Pierna": {
        "Cintilla Iliotibial": {
            "ondas": "660+850",
            "energia": "660nm: 50% | 850nm: 100%",
            "hz": "50Hz (Dolor)",
            "dist": "Contacto",
            "dur": 12,
            "tips_ant": ["Piel limpia"],
            "tips_des": ["Estirar TFL"]
        },
        "Sobrecarga Femoral": {
            "ondas": "660+850",
            "energia": "660nm: 80% | 850nm: 100%",
            "hz": "10Hz (Recuperación)",
            "dist": "10cm",
            "dur": 15,
            "tips_ant": ["Quitar sudor"],
            "tips_des": ["Estirar"]
        }
    },
    "Pie": {
        "Plantar (Fascitis)": {
            "ondas": "660+850",
            "energia": "660nm: 50% | 850nm: 100%",
            "hz": "50Hz",
            "dist": "5cm",
            "dur": 10,
            "tips_ant": ["Sin calcetín"],
            "tips_des": ["Rodar pelota"]
        },
        "Dorsal (Esguince)": {
            "ondas": "660+850",
            "energia": "660nm: 50% | 850nm: 100%",
            "hz": "10Hz",
            "dist": "10cm",
            "dur": 10,
            "tips_ant": ["Piel limpia"],
            "tips_des": ["Movilidad"]
        }
    },
    "Hombro": {
        "Tendinitis": {
            "ondas": "660+850",
            "energia": "660nm: 50% | 850nm: 100%",
            "hz": "10-40Hz",
            "dist": "15cm",
            "dur": 10,
            "tips_ant": ["Sin ropa"],
            "tips_des": ["Péndulos"]
        }
    },
    "Rodilla": {
        "General": {
            "ondas": "660+850",
            "energia": "660nm: 50% | 850nm: 100%",
            "hz": "10Hz",
            "dist": "15cm",
            "dur": 10,
            "tips_ant": ["No hielo antes"],
            "tips_des": ["Movilidad"]
        }
    },
    "Piel": {
        "Cicatrices": {
            "ondas": "630+660",
            "energia": "660nm: 100% | 850nm: 20%",
            "hz": "CW",
            "dist": "10cm",
            "dur": 10,
            "tips_ant": ["Limpio"],
            "tips_des": ["Rosa Mosqueta"]
        },
        "Acné": {
            "ondas": "630+660",
            "energia": "660nm: 80% | 850nm: 0%",
            "hz": "CW",
            "dist": "15cm",
            "dur": 8,
            "tips_ant": ["Limpio"],
            "tips_des": ["Hidratar"]
        },
        "Quemaduras": {
            "ondas": "630+660",
            "energia": "660nm: 50% | 850nm: 0%",
            "hz": "CW",
            "dist": "20cm",
            "dur": 5,
            "tips_ant": ["Sin cremas"],
            "tips_des": ["Aloe Vera"]
        }
    },
    "Sistémico": {
        "Circulación": {
            "ondas": "660+850",
            "energia": "100% | 100%",
            "hz": "CW",
            "dist": "30cm",
            "dur": 20,
            "tips_ant": ["Beber agua"],
            "tips_des": ["Caminar"]
        },
        "Energía": {
            "ondas": "660+850",
            "energia": "100% | 100%",
            "hz": "CW",
            "dist": "20cm",
            "dur": 10,
            "tips_ant": ["Mañana"],
            "tips_des": ["Actividad"]
        }
    },
    "Cabeza": {
        "Migraña": {
            "ondas": "850nm",
            "energia": "660nm: 0% | 850nm: 50%",
            "hz": "10Hz (Alfa)",
            "dist": "Contacto Nuca",
            "dur": 10,
            "tips_ant": ["Oscuridad"],
            "tips_des": ["Reposo"]
        },
        "Salud Cerebral": {
            "ondas": "810nm",
            "energia": "0% | 100%",
            "hz": "40Hz (Gamma)",
            "dist": "30cm",
            "dur": 10,
            "tips_ant": ["Gafas"],
            "tips_des": ["Tarea cognitiva"]
        }
    },
    "Grasa/Estética": {
        "Grasa Localizada": {
            "ondas": "660+850",
            "energia": "100% | 100%",
            "hz": "CW",
            "dist": "10cm",
            "dur": 10,
            "tips_ant": ["Beber agua"],
            "tips_des": ["Ejercicio"],
            "visual_group": "PRE",
            "req_tags": ["Active"]
        },
        "Facial": {
            "ondas": "630nm",
            "energia": "100% | 0%",
            "hz": "CW",
            "dist": "30cm",
            "dur": 10,
            "tips_ant": ["Gafas"],
            "tips_des": ["Serum"],
            "visual_group": "FLEX"
        }
    },
    "Permanente": {
        "Testosterona": {
            "ondas": "660+850",
            "energia": "100% | 100%",
            "hz": "CW",
            "dist": "15cm",
            "dur": 5,
            "tips_ant": ["Piel limpia"],
            "tips_des": ["Ducha fría"],
            "visual_group": "MORNING"
        },
        "Sueño": {
            "ondas": "630nm",
            "energia": "20% | 0%",
            "hz": "CW",
            "dist": "50cm",
            "dur": 15,
            "tips_ant": ["Oscuridad"],
            "tips_des": ["Dormir"],
            "visual_group": "NIGHT"
        }
    }
}

# ==============================================================================
# 3. CLASES Y MODELO DE DATOS
# ==============================================================================
class Tratamiento:
    def __init__(self, id_t, nombre, zona, ondas_txt, config_energia, herzios, distancia, duracion, max_diario, max_semanal, tipo, tags_entreno, default_visual_group, momento_ideal_txt, momentos_prohibidos, tips_antes, tips_despues, incompatible_with=None, fases_config=None, es_custom=False):
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
        self.es_custom = es_custom

    def set_incompatibilidades(self, texto):
        self.incompatibilidades = texto
        return self

# --- GENERADOR DE CATÁLOGO ---
def obtener_catalogo(tratamientos_custom=[]):
    fases_lesion = [{"nombre": "🔥 Fase 1: Inflamatoria", "dias_fin": 7}, {"nombre": "🛠️ Fase 2: Proliferación", "dias_fin": 21}, {"nombre": "🧱 Fase 3: Remodelación", "dias_fin": 60}]
    catalogo = []
    
    # 1. Base Local (Dinámicos)
    for zona, patologias in DB_TRATAMIENTOS_BASE.items():
        if zona in ["Grasa/Estética", "Permanente"]: continue
        for patologia, specs in patologias.items():
            if zona in ["Espalda", "Sistémico", "Cabeza", "Piel"]:
                id_t = "".join(c for c in f"{zona[:3]}_{patologia[:3]}".lower() if c.isalnum() or c=="_")
                catalogo.append(Tratamiento(
                    id_t, f"{zona} - {patologia}", zona, specs["ondas"], specs["energia"], specs["hz"], specs["dist"], specs["dur"], 
                    1, 7, "LESION", ['All'], "FLEX", "Flexible", [], specs["tips_ant"], specs["tips_des"], fases_config=fases_lesion
                ))
            else:
                for lado_code, lado_nom in [("d", "Dcho"), ("i", "Izq")]:
                    base_id = f"{zona.lower()[:4]}_{patologia.lower()[:4]}_{lado_code}"
                    id_t = "".join(c for c in base_id if c.isalnum() or c == "_")
                    nombre = f"{zona} {lado_nom} ({patologia})"
                    catalogo.append(Tratamiento(
                        id_t, nombre, zona, specs["ondas"], specs["energia"], specs["hz"], specs["dist"], specs["dur"], 
                        1, 7, "LESION", ['All'], "FLEX", "Flexible", [], specs["tips_ant"], specs["tips_des"], fases_config=fases_lesion
                    ))

    # 2. Estáticos
    s = DB_TRATAMIENTOS_BASE["Grasa/Estética"]["Grasa Localizada"]
    catalogo.append(Tratamiento("fat_front", "Grasa Abdomen (Frontal)", "Abdomen", s["ondas"], s["energia"], s["hz"], s["dist"], s["dur"], 1, 7, "GRASA", s["req_tags"], s["visual_group"], "Pre-Entreno", ["🌙 Noche", "🚿 Post-Entreno / Mañana"], s["tips_ant"], s["tips_des"]))
    catalogo.append(Tratamiento("fat_d", "Grasa Abdomen (Flanco D)", "Abdomen", s["ondas"], s["energia"], s["hz"], s["dist"], s["dur"], 1, 7, "GRASA", s["req_tags"], s["visual_group"], "Pre-Entreno", ["🌙 Noche", "🚿 Post-Entreno / Mañana"], s["tips_ant"], s["tips_des"]))
    catalogo.append(Tratamiento("fat_i", "Grasa Abdomen (Flanco I)", "Abdomen", s["ondas"], s["energia"], s["hz"], s["dist"], s["dur"], 1, 7, "GRASA", s["req_tags"], s["visual_group"], "Pre-Entreno", ["🌙 Noche", "🚿 Post-Entreno / Mañana"], s["tips_ant"], s["tips_des"]))
    catalogo.append(Tratamiento("fat_glutes", "Grasa Glúteos", "Glúteos", s["ondas"], s["energia"], s["hz"], s["dist"], s["dur"], 1, 7, "GRASA", ["Active", "Lower"], s["visual_group"], "Pre-Entreno", ["🌙 Noche", "🚿 Post-Entreno / Mañana"], s["tips_ant"], s["tips_des"]))
    
    f = DB_TRATAMIENTOS_BASE["Grasa/Estética"]["Facial"]
    catalogo.append(Tratamiento("face", "Facial Rejuv", "Cara", f["ondas"], f["energia"], f["hz"], f["dist"], f["dur"], 1, 7, "PERMANENTE", ['All'], f["visual_group"], f["momento_txt"], ["🏋️ Entrenamiento (Pre)"], f["tips_ant"], f["tips_des"]))
    
    for k, v in DB_TRATAMIENTOS_BASE["Permanente"].items():
        id_t = k.lower()
        catalogo.append(Tratamiento(id_t, k, "Cuerpo", v["ondas"], v["energia"], v["hz"], v["dist"], v["dur"], 1, 7, "PERMANENTE", ['All'], v["visual_group"], v.get("momento_txt","FLEX"), [], v["tips_ant"], v["tips_des"]))

    # 3. Custom AI
    for c in tratamientos_custom:
        catalogo.append(Tratamiento(
            c['id'], c['nombre'], c['zona'], c['ondas'], c['energia'], c['hz'], c['dist'], c['dur'], 
            1, 7, c['tipo'], ['All'], "FLEX", "Según AI", [], c['tips_ant'], c['tips_des'], fases_config=c['fases'], es_custom=True
        ))

    return catalogo

# ==============================================================================
# 4. GESTIÓN DE DATOS Y PERSISTENCIA
# ==============================================================================
def cargar_datos_completos():
    default_db = {
        "configuracion_rutina": {"semana": RUTINA_SEMANAL, "tags": TAGS_ACTIVIDADES},
        "usuario_rutina": {"historial": {}, "meta_diaria": {}, "meta_cardio": {}, "ciclos_activos": {}, "descartados": {}, "planificados_adhoc": {}, "tratamientos_custom": []}, 
        "usuario_libre": {"historial": {}, "meta_diaria": {}, "meta_cardio": {}, "ciclos_activos": {}, "descartados": {}, "planificados_adhoc": {}, "tratamientos_custom": []}
    }
    if not os.path.exists(ARCHIVO_DATOS): return default_db
    try:
        with open(ARCHIVO_DATOS, 'r') as f:
            datos = json.load(f)
            if "configuracion_rutina" not in datos: datos["configuracion_rutina"] = default_db["configuracion_rutina"]
            for user in ["usuario_rutina", "usuario_libre"]:
                if user not in datos: datos[user] = default_db[user]
                if "meta_cardio" not in datos[user]: datos[user]["meta_cardio"] = {}
                if "planificados_adhoc" not in datos[user]: datos[user]["planificados_adhoc"] = {}
                if "tratamientos_custom" not in datos[user]: datos[user]["tratamientos_custom"] = []
            return datos
    except: return default_db

def guardar_datos_completos(datos):
    with open(ARCHIVO_DATOS, 'w') as f:
        json.dump(datos, f, indent=4)

def obtener_rutina_completa(fecha_obj, db_global, db_usuario):
    fecha_iso = fecha_obj.isoformat()
    dia_str = str(fecha_obj.weekday())
    rutina_manual = db_usuario.get("meta_diaria", {}).get(fecha_iso, None)
    config_semana = db_global.get("configuracion_rutina", {}).get("semana", RUTINA_SEMANAL)
    config_tags = db_global.get("configuracion_rutina", {}).get("tags", TAGS_ACTIVIDADES)
    rutina_fuerza = rutina_manual if rutina_manual is not None else config_semana.get(dia_str, [])
    es_manual_f = (rutina_manual is not None)
    cardio_manual = db_usuario.get("meta_cardio", {}).get(fecha_iso, None)
    if cardio_manual:
        rutina_cardio = cardio_manual; es_manual_c = True
    else:
        rutina_cardio = CARDIO_DEFAULTS_BY_DAY.get(dia_str, {"actividad": "Descanso Cardio"})
        es_manual_c = False
    tags = set(['All'])
    for r in rutina_fuerza:
        if r in config_tags: tags.update(config_tags[r])
    act = rutina_cardio.get("actividad", "Descanso Cardio")
    if act in TAGS_ACTIVIDADES: tags.update(TAGS_ACTIVIDADES[act])
    return rutina_fuerza, rutina_cardio, tags, es_manual_f, es_manual_c, list(config_tags.keys())

def procesar_excel_rutina(uploaded_file):
    try:
        df_sem = pd.read_excel(uploaded_file, sheet_name='Semana')
        mapa = {"lunes":"0", "martes":"1", "miércoles":"2", "miercoles":"2", "jueves":"3", "viernes":"4", "sábado":"5", "sabado":"5", "domingo":"6"}
        nueva_semana = {}
        for _, row in df_sem.iterrows():
            d = str(row.iloc[0]).lower().strip()
            if d in mapa: nueva_semana[mapa[d]] = [x.strip() for x in str(row.iloc[1]).split(',')]
        df_tags = pd.read_excel(uploaded_file, sheet_name='Tags')
        nuevos_tags = {}
        for _, row in df_tags.iterrows():
            t = str(row.iloc[1])
            nuevos_tags[str(row.iloc[0]).strip()] = [x.strip() for x in t.split(',')] if not pd.isna(t) else []
        return {"semana": nueva_semana, "tags": nuevos_tags}
    except: return None

# --- 5. LÓGICA AI ---
def consultar_ia(dolencia, api_key):
    if not api_key: return None
    client = OpenAI(api_key=api_key)
    prompt = f"""
    Actúa como experto en Fotobiomodulación. Usuario con: "{dolencia}".
    Genera JSON con:
    - nombre: Título corto
    - zona: Parte cuerpo
    - ondas: "660+850", "850nm" o "630nm"
    - energia: Dimmer (ej. "660nm: 50% | 850nm: 100%")
    - hz: Frecuencia (CW, 10Hz, 40Hz, 50Hz) y motivo
    - dist: Distancia cm
    - dur: Minutos (int)
    - tips_ant: 2 consejos antes
    - tips_des: 2 consejos después
    - es_lesion: true/false
    - tipo: "LESION", "MUSCULAR" o "PERMANENTE"
    Responde SOLO JSON.
    """
    try:
        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.3)
        return json.loads(response.choices[0].message.content.replace("```json", "").replace("```", ""))
    except: return None

# --- 6. HELPERS VISUALES ---
def mostrar_definiciones_ondas():
    with st.expander("ℹ️ Guía Técnica (nm/Hz)"):
        st.markdown("""**🔴 630nm / 660nm:** Piel (Regeneración) | **🟣 810nm / 850nm:** Profundidad (Inflamación)\n**⚡ CW:** Dosis Alta | **10Hz:** Recup. Muscular | **40Hz:** Cerebro | **50Hz:** Dolor Agudo""")

def mostrar_ficha_tecnica(t, lista_completa):
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"**Zona:** {t.zona}\n**Intensidad:** {t.config_energia}")
    with c2: st.markdown(f"**Hz:** {t.herzios}\n**Tiempo:** {t.duracion} min ({t.distancia})")
    st.markdown("---")
    if t.momentos_prohibidos: st.write(f"⏰ **No usar:** {', '.join(t.momentos_prohibidos)}")
    if t.tags_entreno != ['All']: st.write(f"🏋️ **Req:** {', '.join(t.tags_entreno)}")
    if t.incompatible_with:
        mapa = {tr.id: tr.nombre for tr in lista_completa}
        nombres = [mapa.get(x, x) for x in t.incompatible_with]
        st.write(f"⚔️ **Incompatible:** {', '.join(nombres)}")
    c_a, c_d = st.columns(2)
    with c_a: 
        st.markdown("**Antes:**")
        for tip in t.tips_antes: st.caption(f"• {tip}")
    with c_d:
        st.markdown("**Después:**")
        for tip in t.tips_despues: st.caption(f"• {tip}")

def analizar_bloqueos(tratamiento, momento, historial, registros_hoy, fecha_str, tags_dia, clave_usuario):
    if clave_usuario == "usuario_rutina":
        if 'Active' in tratamiento.tags_entreno and 'Active' not in tags_dia: return True, "⚠️ FALTA ACTIVIDAD"
    if momento in tratamiento.momentos_prohibidos: return True, "⛔ HORARIO PROHIBIDO"
    dias_hechos = 0
    fecha_dt = datetime.date.fromisoformat(fecha_str)
    for i in range(7):
        f = (fecha_dt - timedelta(days=i)).isoformat()
        if f in historial and tratamiento.id in historial[f]: dias_hechos += 1
    hecho_hoy = (fecha_str in historial and tratamiento.id in historial[fecha_str])
    if not hecho_hoy and dias_hechos >= tratamiento.max_semanal: return True, "⛔ MAX SEMANAL"
    for inc in tratamiento.incompatible_with:
        if inc in registros_hoy: return True, "⛔ INCOMPATIBLE"
    return False, ""

def obtener_tratamientos_presentes(fecha_str, db_usuario, lista_tratamientos):
    presentes = set()
    presentes.update(db_usuario["historial"].get(fecha_str, {}).keys())
    presentes.update(db_usuario["planificados_adhoc"].get(fecha_str, {}).keys())
    for t in lista_tratamientos:
        ciclo = db_usuario["ciclos_activos"].get(t.id)
        if ciclo and ciclo.get('activo') and ciclo.get('estado') == 'activo': presentes.add(t.id)
    return presentes

# ==============================================================================
# 7. RENDERIZADO DIARIO (CORE)
# ==============================================================================
def renderizar_dia(fecha_obj):
    fecha_str = fecha_obj.isoformat()
    rutina_fuerza, rutina_cardio, tags_dia, man_f, man_c, todas_rutinas = obtener_rutina_completa(fecha_obj, st.session_state.db_global, db_usuario)
    ids_seleccionados_libre = []

    # A. RUTINAS
    if clave_usuario == "usuario_rutina":
        c_f, c_c = st.columns(2)
        with c_f:
            st.markdown(f"**🏋️ Fuerza** ({'Manual' if man_f else 'Auto'})")
            opts_f = [k for k in todas_rutinas if "Remo" not in k and "Cinta" not in k and "Elíptica" not in k and "Andar" not in k]
            sel_f = st.multiselect("Rutina:", opts_f, default=[x for x in rutina_fuerza if x in opts_f], key=f"sf_{fecha_str}", label_visibility="collapsed")
            if set(sel_f) != set(rutina_fuerza):
                if "meta_diaria" not in db_usuario: db_usuario["meta_diaria"] = {}
                db_usuario["meta_diaria"][fecha_str] = sel_f
                guardar_datos_completos(st.session_state.db_global); st.rerun()
        with c_c:
            st.markdown(f"**🏃 Cardio** ({'Manual' if man_c else 'Auto'})")
            opts_c = ["Descanso Cardio"] + [k for k in GENERIC_CARDIO_PARAMS.keys() if k != "Descanso Cardio"]
            sel_c = st.selectbox("Actividad:", opts_c, index=opts_c.index(rutina_cardio.get("actividad", "Descanso Cardio")), key=f"sc_{fecha_str}", label_visibility="collapsed")
            params = rutina_cardio.copy(); params["actividad"] = sel_c
            if sel_c != "Descanso Cardio":
                c_p1, c_p2 = st.columns(2)
                if "tiempo" in GENERIC_CARDIO_PARAMS.get(sel_c, {}): params["tiempo"] = c_p1.number_input("Min:", value=params.get("tiempo", 15), key=f"t_{fecha_str}")
                if "velocidad" in GENERIC_CARDIO_PARAMS.get(sel_c, {}): params["velocidad"] = c_p2.number_input("Km/h:", value=params.get("velocidad", 6.5), key=f"v_{fecha_str}")
                if "inclinacion" in GENERIC_CARDIO_PARAMS.get(sel_c, {}): params["inclinacion"] = c_p1.number_input("Inc %:", value=params.get("inclinacion", 0), key=f"i_{fecha_str}")
                if "pasos" in GENERIC_CARDIO_PARAMS.get(sel_c, {}): params["pasos"] = c_p1.number_input("Pasos:", value=params.get("pasos", 10000), key=f"p_{fecha_str}")
            if params != rutina_cardio:
                if "meta_cardio" not in db_usuario: db_usuario["meta_cardio"] = {}
                db_usuario["meta_cardio"][fecha_str] = params
                guardar_datos_completos(st.session_state.db_global); st.rerun()
        
        key_conf = f"conf_{fecha_str}"
        if key_conf not in st.session_state: st.session_state[key_conf] = False
        if not st.session_state[key_conf]:
            if st.button("✅ Confirmar Rutina del Día", key=f"btn_c_{fecha_str}"):
                st.session_state[key_conf] = True; st.rerun()
        else:
            st.success("Rutina Confirmada")
    else:
        ids = db_usuario.get("meta_diaria", {}).get(fecha_str, [])
        mapa_n = {t.nombre: t.id for t in lista_tratamientos}
        mapa_i = {t.id: t.nombre for t in lista_tratamientos}
        sel = st.multiselect("Tratamientos:", list(mapa_n.keys()), default=[mapa_i[i] for i in ids if i in mapa_i], key=f"ml_{fecha_str}")
        if set([mapa_n[n] for n in sel]) != set(ids):
            if "meta_diaria" not in db_usuario: db_usuario["meta_diaria"] = {}
            db_usuario["meta_diaria"][fecha_str] = [mapa_n[n] for n in sel]
            guardar_datos_completos(st.session_state.db_global); st.rerun()
        ids_seleccionados_libre = ids
        st.session_state[f"conf_{fecha_str}"] = True

    st.divider()
    adhoc_hoy = db_usuario.get("planificados_adhoc", {}).get(fecha_str, {})
    presentes_hoy = obtener_tratamientos_presentes(fecha_str, db_usuario, lista_tratamientos)
    registros_dia = db_usuario["historial"].get(fecha_str, {})
    
    # B. AÑADIR TRATAMIENTO ADICIONAL (SELECTOR INTELIGENTE)
    if clave_usuario == "usuario_rutina" and st.session_state.get(f"conf_{fecha_str}", False):
        with st.expander("➕ Añadir Tratamiento Adicional"):
            compatibles = []
            # Llenamos la lista con todos los compatibles (sin filtrar planificados para permitir borrado)
            for t in lista_tratamientos:
                compatible_tag = False
                if 'All' in t.tags_entreno or any(tag in tags_dia for tag in t.tags_entreno): compatible_tag = True
                if compatible_tag: compatibles.append(t)
            
            compatibles.sort(key=lambda x: x.nombre)
            mapa_comp = {t.nombre: t for t in compatibles}
            sel_add = st.selectbox("Elegir:", ["--"] + list(mapa_comp.keys()), key=f"sad_{fecha_str}")
            
            if sel_add != "--":
                t_obj = mapa_comp[sel_add]
                # Selector Bidireccional
                esta_planificado = t_obj.id in adhoc_hoy
                
                if esta_planificado:
                    st.warning(f"⚠️ {t_obj.nombre} ya está planificado.")
                    if st.button("🗑️ Descartar del Plan", key=f"del_plan_{fecha_str}"):
                        del db_usuario["planificados_adhoc"][fecha_str][t_obj.id]
                        guardar_datos_completos(st.session_state.db_global); st.rerun()
                else:
                    st.caption(f"💡 {t_obj.momento_ideal_txt}")
                    opts = ["🏋️ Entrenamiento (Pre)", "🚿 Post-Entreno / Mañana", "⛅ Tarde", "🌙 Noche"]
                    valid = [o for o in opts if o not in t_obj.momentos_prohibidos]
                    mom = st.selectbox("Momento:", valid, key=f"mad_{fecha_str}")
                    
                    bloq, mot = analizar_bloqueos(t_obj, mom, db_usuario["historial"], {}, fecha_str, tags_dia, clave_usuario)
                    for pid in presentes_hoy:
                        if pid in t_obj.incompatible_with: bloq=True; mot=f"Incompatible con {pid}"
                        t_pres = next((tp for tp in lista_tratamientos if tp.id == pid), None)
                        if t_pres and t_obj.id in t_pres.incompatible_with: bloq=True; mot=f"Incompatible con {pid}"
                    
                    if bloq: st.error(mot)
                    else:
                        c_pl, c_reg = st.columns(2)
                        if c_pl.button("📅 Planificar", key=f"pl_{fecha_str}"):
                            if "planificados_adhoc" not in db_usuario: db_usuario["planificados_adhoc"] = {}
                            if fecha_str not in db_usuario["planificados_adhoc"]: db_usuario["planificados_adhoc"][fecha_str] = {}
                            db_usuario["planificados_adhoc"][fecha_str][t_obj.id] = mom
                            guardar_datos_completos(st.session_state.db_global); st.rerun()
                        if c_reg.button("✅ Registrar Ya", key=f"bdir_{fecha_str}"):
                            now = datetime.datetime.now().strftime('%H:%M')
                            if fecha_str not in db_usuario["historial"]: db_usuario["historial"][fecha_str] = {}
                            if t_obj.id not in db_usuario["historial"][fecha_str]: db_usuario["historial"][fecha_str][t_obj.id] = []
                            db_usuario["historial"][fecha_str][t_obj.id].append({"hora": now, "detalle": mom})
                            # También marcamos como planificado
                            if "planificados_adhoc" not in db_usuario: db_usuario["planificados_adhoc"] = {}
                            if fecha_str not in db_usuario["planificados_adhoc"]: db_usuario["planificados_adhoc"][fecha_str] = {}
                            db_usuario["planificados_adhoc"][fecha_str][t_obj.id] = mom
                            guardar_datos_completos(st.session_state.db_global); st.rerun()

    descartados = db_usuario.get("descartados", {}).get(fecha_str, [])
    lista_mostrar = []
    for t in lista_tratamientos:
        mostrar = False; origen = ""
        ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
        if ciclo and ciclo.get('activo') and ciclo.get('estado') == 'activo': mostrar = True; origen = "clinica"
        if t.id in adhoc_hoy: mostrar = True; origen = "adhoc"
        if clave_usuario != "usuario_rutina" and t.id in ids_seleccionados_libre: mostrar = True
        if mostrar: lista_mostrar.append((t, origen))

    # --- BOTÓN REGISTRAR TODO ---
    if lista_mostrar and st.button("⚡ Registrar Todos los Tratamientos del Día", key=f"all_{fecha_str}"):
        now = datetime.datetime.now().strftime('%H:%M')
        if fecha_str not in db_usuario["historial"]: db_usuario["historial"][fecha_str] = {}
        for t, origen in lista_mostrar:
            rad_key = f"rad_{t.id}_{fecha_str}"
            momento_final = st.session_state.get(rad_key)
            if not momento_final and origen == "adhoc": momento_final = adhoc_hoy.get(t.id)
            if not momento_final:
                opts = ["🏋️ Entrenamiento (Pre)", "🚿 Post-Entreno / Mañana", "⛅ Tarde", "🌙 Noche"]
                valid_opts = [o for o in opts if o not in t.momentos_prohibidos]
                mapa_inv = {"PRE": "🏋️ Entrenamiento (Pre)", "POST": "🚿 Post-Entreno / Mañana", "NIGHT": "🌙 Noche", "MORNING": "🌞 Mañana"}
                pref = mapa_inv.get(t.default_visual_group)
                if pref and pref in valid_opts: momento_final = pref
                elif valid_opts: momento_final = valid_opts[0] # FALLBACK CLAVE PARA FLEX
            
            bloq, _ = analizar_bloqueos(t, momento_final, db_usuario["historial"], registros_dia, fecha_str, tags_dia, clave_usuario)
            if origen in ["adhoc", "clinica"]: bloq = False 
            
            if not bloq and momento_final:
                if t.id not in db_usuario["historial"][fecha_str] or not db_usuario["historial"][fecha_str][t.id]:
                    if t.id not in db_usuario["historial"][fecha_str]: db_usuario["historial"][fecha_str][t.id] = []
                    db_usuario["historial"][fecha_str][t.id].append({"hora": now, "detalle": momento_final})
        guardar_datos_completos(st.session_state.db_global); st.rerun()

    grupos = {"PRE": [], "POST": [], "MORNING": [], "NIGHT": [], "FLEX": [], "COMPLETED": [], "DISCARDED": [], "HIDDEN": []}
    mapa_vis = {"🏋️ Entrenamiento (Pre)": "PRE", "🚿 Post-Entreno / Mañana": "POST", "🌞 Mañana": "MORNING", "🌙 Noche": "NIGHT"}

    for t, origen in lista_mostrar:
        hechos = len(registros_dia.get(t.id, []))
        if t.id in descartados: grupos["DISCARDED"].append((t, origen))
        elif hechos >= t.max_diario: grupos["COMPLETED"].append((t, origen))
        else:
            g = t.default_visual_group
            rad_key = f"rad_{t.id}_{fecha_str}"
            if rad_key in st.session_state and st.session_state[rad_key] in mapa_vis: g = mapa_vis[st.session_state[rad_key]]
            elif origen == "adhoc" and adhoc_hoy.get(t.id) in mapa_vis: g = mapa_vis[adhoc_hoy[t.id]]
            if g in grupos: grupos[g].append((t, origen))
            else: grupos["FLEX"].append((t, origen))
    
    if clave_usuario == "usuario_rutina":
        for t in lista_tratamientos:
            if t.id not in ids_mostrados: grupos["HIDDEN"].append(t)

    def render_card(item):
        t, origen = item
        hechos = len(registros_dia.get(t.id, []))
        icon = "❌" if t.id in descartados else ("✅" if hechos>=t.max_diario else "⬜")
        info_ex = f" [CLÍNICA] (Día {(fecha_obj - datetime.date.fromisoformat(db_usuario['ciclos_activos'][t.id]['fecha_inicio'])).days})" if origen == "clinica" else (" [PUNTUAL]" if origen == "adhoc" else "")
        head_xtra = f" | {registros_dia[t.id][-1]['detalle']}" if hechos >= t.max_diario else ""

        with st.expander(f"{icon} {t.nombre} ({hechos}/{t.max_diario}){info_ex}{head_xtra}"):
            if t.id in descartados:
                if st.button("Recuperar", key=f"rec_{t.id}_{fecha_str}"):
                    db_usuario["descartados"][fecha_str].remove(t.id)
                    guardar_datos_completos(st.session_state.db_global); st.rerun()
                return
            if hechos >= t.max_diario:
                if st.button("❌ Deshacer", key=f"undo_{t.id}_{fecha_str}"):
                    del db_usuario["historial"][fecha_str][t.id]
                    guardar_datos_completos(st.session_state.db_global); st.rerun()
                return

            st.success(f"💡 {t.momento_ideal_txt}")
            mostrar_ficha_tecnica(t, lista_tratamientos)
            
            opts = ["🏋️ Entrenamiento (Pre)", "🚿 Post-Entreno / Mañana", "⛅ Tarde", "🌙 Noche"]
            valid = [o for o in opts if o not in t.momentos_prohibidos]
            idx_def = valid.index(adhoc_hoy[t.id]) if origen == "adhoc" and adhoc_hoy.get(t.id) in valid else 0
            sel = st.radio("Momento:", valid, index=idx_def, key=f"rad_{t.id}_{fecha_str}")
            
            c1, c2, c3 = st.columns([2,1,1])
            bloq, mot = analizar_bloqueos(t, sel, db_usuario["historial"], registros_dia, fecha_str, tags_dia, clave_usuario)
            if bloq: c1.warning(mot)
            if c1.button("Registrar", key=f"go_{t.id}_{fecha_str}", disabled=bloq):
                now = datetime.datetime.now().strftime('%H:%M')
                if fecha_str not in db_usuario["historial"]: db_usuario["historial"][fecha_str] = {}
                if t.id not in db_usuario["historial"][fecha_str]: db_usuario["historial"][fecha_str][t.id] = []
                db_usuario["historial"][fecha_str][t.id].append({"hora": now, "detalle": sel})
                guardar_datos_completos(st.session_state.db_global); st.rerun()
            if c2.button("Omitir", key=f"om_{t.id}_{fecha_str}"):
                if "descartados" not in db_usuario: db_usuario["descartados"] = {}
                if fecha_str not in db_usuario["descartados"]: db_usuario["descartados"][fecha_str] = []
                db_usuario["descartados"][fecha_str].append(t.id)
                if origen == "adhoc": del db_usuario["planificados_adhoc"][fecha_str][t.id]
                guardar_datos_completos(st.session_state.db_global); st.rerun()
            if origen == "clinica" and c3.button("⏭️ Saltar", key=f"sk_{t.id}_{fecha_str}"):
                c = db_usuario["ciclos_activos"][t.id]
                if 'dias_saltados' not in c: c['dias_saltados'] = []
                c['dias_saltados'].append(fecha_str)
                if "descartados" not in db_usuario: db_usuario["descartados"] = {}
                if fecha_str not in db_usuario["descartados"]: db_usuario["descartados"][fecha_str] = []
                db_usuario["descartados"][fecha_str].append(t.id)
                guardar_datos_completos(st.session_state.db_global); st.rerun()
            elif origen == "adhoc" and c3.button("🗑️ Quitar", key=f"del_{t.id}_{fecha_str}"):
                del db_usuario["planificados_adhoc"][fecha_str][t.id]
                guardar_datos_completos(st.session_state.db_global); st.rerun()

    for g in ["MORNING", "PRE", "POST", "NIGHT", "FLEX"]:
        if grupos[g]:
            st.subheader(g)
            for item in grupos[g]: render_card(item)
    for g in ["COMPLETED", "DISCARDED"]:
        if grupos[g]:
            st.markdown(f"### {('✅ Completados' if g=='COMPLETED' else '❌ Descartados')}")
            for item in grupos[g]: render_card(item)
    if grupos["HIDDEN"] and clave_usuario == "usuario_rutina":
        with st.expander("Inactivos / Ocultos Hoy"):
            for t in grupos["HIDDEN"]: 
                with st.expander(f"{t.nombre}"): mostrar_ficha_tecnica(t, lista_tratamientos)

elif menu_navegacion == "🔍 Buscador AI":
    st.title("🔍 Buscador & Generador AI")
    if not HAS_OPENAI: st.warning("Instala 'openai' para usar esto."); st.stop()
    if 'api_key_val' not in st.session_state: st.session_state.api_key_val = ""
    api_key = st.text_input("🔑 OpenAI API Key", type="password", value=st.session_state.api_key_val)
    if api_key: st.session_state.api_key_val = api_key
    
    query = st.text_input("Describe tu dolencia...")
    if st.button("Consultar AI") and query and api_key:
        with st.spinner("Analizando con IA..."):
            res = consultar_ia(query, api_key)
            if res:
                st.success(f"Protocolo: {res['nombre']}")
                st.json(res)
                c1, c2 = st.columns(2)
                if c1.button("📅 Añadir a Hoy"):
                    id_new = str(uuid.uuid4())[:8]
                    res['id'] = id_new
                    res['tipo'] = 'LESION'
                    res['fases'] = [{"nombre": "Estándar", "dias_fin": 30}]
                    db_usuario["tratamientos_custom"].append(res)
                    hoy = datetime.date.today().isoformat()
                    if "planificados_adhoc" not in db_usuario: db_usuario["planificados_adhoc"] = {}
                    if hoy not in db_usuario["planificados_adhoc"]: db_usuario["planificados_adhoc"][hoy] = {}
                    db_usuario["planificados_adhoc"][hoy][id_new] = "FLEX"
                    guardar_datos_completos(st.session_state.db_global); st.success("Añadido"); st.rerun()
                if c2.button("🚑 Empezar Clínica"):
                    id_new = str(uuid.uuid4())[:8]
                    res['id'] = id_new
                    res['tipo'] = 'LESION'
                    res['fases'] = [{"nombre": "Estándar", "dias_fin": 30}]
                    db_usuario["tratamientos_custom"].append(res)
                    if "ciclos_activos" not in db_usuario: db_usuario["ciclos_activos"] = {}
                    db_usuario["ciclos_activos"][id_new] = {"fecha_inicio": datetime.date.today().isoformat(), "activo": True, "modo": "fases", "estado": "activo", "dias_saltados": []}
                    guardar_datos_completos(st.session_state.db_global); st.success("Iniciado"); st.rerun()

elif menu_navegacion == "📊 Historial":
    st.title("📊 Historial")
    vista = st.radio("Vista:", ["Semana", "Mes", "Año"], horizontal=True)
    hist = db_usuario.get("historial", {})
    t_usados = set([k for r in hist.values() for k in r.keys()])
    mapa = {t.id: t.nombre for t in lista_tratamientos}
    
    if vista == "Semana":
        d_ref = st.date_input("Semana:", datetime.date.today())
        start = d_ref - timedelta(days=d_ref.weekday())
        days = [start + timedelta(days=i) for i in range(7)]
        data = []
        for tid in t_usados:
            row = {"Tratamiento": mapa.get(tid, tid), "Total": 0}
            for i, d in enumerate(days):
                c = len(hist.get(d.isoformat(), {}).get(tid, []))
                row[["Lun","Mar","Mie","Jue","Vie","Sab","Dom"][i]] = "✅" * c
                row["Total"] += c
            if row["Total"] > 0: data.append(row)
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    elif vista == "Mes":
        d_ref = st.date_input("Mes:", datetime.date.today())
        m_str = d_ref.strftime("%Y-%m")
        counts = {}
        for f, r in hist.items():
            if f.startswith(m_str):
                for tid, l in r.items(): counts[mapa.get(tid, tid)] = counts.get(mapa.get(tid, tid), 0) + len(l)
        if counts: st.bar_chart(pd.DataFrame(list(counts.items()), columns=["T", "N"]).set_index("T"))
    elif vista == "Año":
        y_ref = st.number_input("Año:", value=datetime.date.today().year)
        y_str = str(y_ref)
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        data = []
        for tid in t_usados:
            row = {"T": mapa.get(tid, tid)}
            tot = 0
            for i in range(1, 13):
                m_key = f"{y_str}-{i:02d}"
                c = 0
                for f, r in hist.items():
                    if f.startswith(m_key): c += len(r.get(tid, []))
                row[meses[i-1]] = c
                tot += c
            if tot > 0: data.append(row)
        st.dataframe(pd.DataFrame(data), use_container_width=True)
