import streamlit as st
import datetime
from datetime import timedelta
import json
import os
import pandas as pd
import uuid

# --- INTEGRACIÓN GOOGLE GEMINI ---
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

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
    "0": ["FULLBODY I"],            # Lunes
    "1": ["TORSO I"],               # Martes
    "2": ["FULLBODY II"],           # Miércoles
    "3": ["TORSO II / CIRCUITO"],   # Jueves
    "4": ["PREVENTIVO I"],          # Viernes
    "5": ["PREVENTIVO II"],         # Sábado
    "6": ["Descanso Total"]         # Domingo
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

# Zonas que generan variantes Derecha/Izquierda automáticamente
ZONAS_SIMETRICAS = ["Codo", "Antebrazo", "Muñeca", "Pierna", "Pie", "Hombro", "Rodilla", "Tobillo", "Brazo", "Mano", "Cadera"]

# ==============================================================================
# 2. DEFINICIÓN MAESTRA BASE (CATÁLOGO COMPLETO)
# ==============================================================================
DB_TRATAMIENTOS_BASE = {
    "Codo": {
        "Epicondilitis (Tenista)": {
            "ondas": "660+850", "energia": "660nm: 50% | 850nm: 100%", 
            "hz": "50Hz (Dolor)", "dist": "Contacto", "dur": 10,
            "frecuencias": [(660, 50), (850, 100)],
            "descripcion": "Reduce inflamación en tendón extensor y alivia dolor agudo.",
            "sintomas": "Dolor en la cara externa del codo al agarrar o girar.",
            "posicion": "Sentado, brazo en mesa. Panel lateral tocando zona externa.",
            "tips_ant": ["Piel limpia"], "tips_des": ["No pinza con dedos", "Hielo si dolor"]
        },
        "Epitrocleitis (Golfista)": {
            "ondas": "660+850", "energia": "660nm: 50% | 850nm: 100%", 
            "hz": "50Hz (Dolor)", "dist": "Contacto", "dur": 10,
            "frecuencias": [(660, 50), (850, 100)],
            "descripcion": "Regeneración para la cara interna del codo.",
            "sintomas": "Dolor interno al flexionar muñeca.",
            "posicion": "Brazo en mesa, palma arriba. Panel en cara interna.",
            "tips_ant": ["Piel limpia"], "tips_des": ["Estirar flexores"]
        },
        "Calcificación": {
            "ondas": "850nm", "energia": "660nm: 0% | 850nm: 100%", 
            "hz": "50Hz (Analgesia)", "dist": "Contacto", "dur": 12,
            "frecuencias": [(660, 0), (850, 100)],
            "descripcion": "Infrarrojo profundo para estimular reabsorción de calcio.",
            "sintomas": "Dolor punzante y limitación de movimiento.",
            "posicion": "Panel en contacto directo con la zona calcificada.",
            "tips_ant": ["Calor previo"], "tips_des": ["Movilidad suave"]
        },
        "Bursitis": {
            "ondas": "660+850", "energia": "660nm: 50% | 850nm: 100%", 
            "hz": "10Hz (Anti-inflamatorio)", "dist": "5cm", "dur": 10,
            "frecuencias": [(660, 50), (850, 100)],
            "descripcion": "Baja la inflamación de la bursa sin contacto directo.",
            "sintomas": "Hinchazón (bulto) en la punta del codo.",
            "posicion": "Panel a 5cm del bulto. NO TOCAR.",
            "tips_ant": ["Zona limpia"], "tips_des": ["No apoyar codo"]
        }
    },
    "Espalda": {
        "Cervicalgia": {
            "ondas": "660+850", "energia": "660nm: 50% | 850nm: 100%", 
            "hz": "50Hz (Dolor)", "dist": "10cm", "dur": 15,
            "frecuencias": [(660, 50), (850, 100)],
            "descripcion": "Relaja tensión cervical y mejora riego sanguíneo.",
            "sintomas": "Rigidez de cuello y trapecios.",
            "posicion": "Sentado, panel detrás del cuello.",
            "tips_ant": ["Sin collar"], "tips_des": ["Movilidad suave"]
        },
        "Dorsalgia": {
            "ondas": "660+850", "energia": "660nm: 50% | 850nm: 100%", 
            "hz": "50Hz", "dist": "15cm", "dur": 15,
            "frecuencias": [(660, 50), (850, 100)],
            "descripcion": "Para zona media-alta de la espalda y postura.",
            "sintomas": "Dolor entre omóplatos.",
            "posicion": "Sentado al revés en silla o tumbado.",
            "tips_ant": ["Postura recta"], "tips_des": ["Estirar pecho"]
        },
        "Lumbalgia": {
            "ondas": "660+850", "energia": "660nm: 50% | 850nm: 100%", 
            "hz": "50Hz (Dolor)", "dist": "10cm", "dur": 20,
            "frecuencias": [(660, 50), (850, 100)],
            "descripcion": "Penetración profunda lumbar para desinflamar discos.",
            "sintomas": "Dolor en zona baja, dificultad al enderezarse.",
            "posicion": "Tumbado boca abajo o sentado en taburete.",
            "tips_ant": ["Calor previo"], "tips_des": ["No cargar peso"]
        }
    },
    "Antebrazo": {
        "Sobrecarga": {
            "ondas": "660+850", "energia": "660nm: 80% | 850nm: 80%", 
            "hz": "10Hz (Relajación)", "dist": "15cm", "dur": 12,
            "frecuencias": [(660, 80), (850, 80)],
            "descripcion": "Relajación muscular general del antebrazo.",
            "sintomas": "Sensación de fatiga, antebrazos duros.",
            "posicion": "Antebrazo apoyado en mesa. Panel desde arriba.",
            "tips_ant": ["Quitar sudor"], "tips_des": ["Estirar", "Calor"]
        },
        "Tendinitis": {
            "ondas": "660+850", "energia": "660nm: 50% | 850nm: 100%", 
            "hz": "50Hz (Dolor)", "dist": "10cm", "dur": 10,
            "frecuencias": [(660, 50), (850, 100)],
            "descripcion": "Tratamiento anti-inflamatorio localizado.",
            "sintomas": "Dolor puntual en trayecto del tendón.",
            "posicion": "Panel apuntando directamente al punto de dolor.",
            "tips_ant": ["Quitar reloj"], "tips_des": ["Reposo"]
        }
    },
    "Muñeca": {
        "Túnel Carpiano": {
            "ondas": "660+850", "energia": "660nm: 50% | 850nm: 100%", 
            "hz": "10Hz (Nervio)", "dist": "5cm", "dur": 10,
            "frecuencias": [(660, 50), (850, 100)],
            "descripcion": "Enfocado en regeneración nerviosa y desinflamación.",
            "sintomas": "Hormigueo en dedos, dolor nocturno.",
            "posicion": "Palma arriba. Panel en base de muñeca.",
            "tips_ant": ["Palma abierta"], "tips_des": ["Movilidad"]
        },
        "Articular": {
            "ondas": "660+850", "energia": "660nm: 50% | 850nm: 100%", 
            "hz": "50Hz", "dist": "5cm", "dur": 10,
            "frecuencias": [(660, 50), (850, 100)],
            "descripcion": "Para dolor articular general y rigidez.",
            "sintomas": "Dolor difuso al mover la muñeca.",
            "posicion": "Rotar muñeca frente al panel.",
            "tips_ant": ["Sin muñequera"], "tips_des": ["Hielo"]
        }
    },
    "Pierna": {
        "Cintilla Iliotibial": {
            "ondas": "660+850", "energia": "660nm: 50% | 850nm: 100%", 
            "hz": "50Hz (Dolor)", "dist": "Contacto", "dur": 12,
            "frecuencias": [(660, 50), (850, 100)],
            "descripcion": "Reduce fricción e inflamación en fascia lata.",
            "sintomas": "Dolor lateral externo rodilla/muslo.",
            "posicion": "Tumbado de lado, panel en cara externa muslo.",
            "tips_ant": ["Piel limpia"], "tips_des": ["Estirar TFL"]
        },
        "Sobrecarga Femoral": {
            "ondas": "660+850", "energia": "660nm: 80% | 850nm: 100%", 
            "hz": "10Hz (Recuperación)", "dist": "10cm", "dur": 15,
            "frecuencias": [(660, 80), (850, 100)],
            "descripcion": "Acelera barrido de lactato y recuperación.",
            "sintomas": "Fatiga, pesadez muscular.",
            "posicion": "Panel cubriendo el grupo muscular afectado.",
            "tips_ant": ["Quitar sudor"], "tips_des": ["Estirar"]
        }
    },
    "Pie": {
        "Fascitis Plantar": {
            "ondas": "660+850", "energia": "660nm: 50% | 850nm: 100%", 
            "hz": "50Hz", "dist": "5cm", "dur": 10,
            "frecuencias": [(660, 50), (850, 100)],
            "descripcion": "Desinflamación del arco plantar.",
            "sintomas": "Dolor agudo en talón al pisar.",
            "posicion": "Sentado, panel apuntando a planta del pie.",
            "tips_ant": ["Sin calcetín"], "tips_des": ["Rodar pelota"]
        },
        "Dorsal (Esguince)": {
            "ondas": "660+850", "energia": "660nm: 50% | 850nm: 100%", 
            "hz": "10Hz (Regeneración)", "dist": "10cm", "dur": 10,
            "frecuencias": [(660, 50), (850, 100)],
            "descripcion": "Regeneración de ligamentos.",
            "sintomas": "Dolor e hinchazón tobillo/empeine.",
            "posicion": "Panel enfocado a zona hinchada.",
            "tips_ant": ["Piel limpia"], "tips_des": ["Movilidad"]
        },
        "Lateral (Metatarso)": {
            "ondas": "Todas (Mega)", "energia": "TODO 100%", 
            "hz": "50Hz (Analgesia)", "dist": "10cm", "dur": 12,
            "frecuencias": [(660, 100), (850, 100), (810, 100), (830, 100), (630, 100)],
            "descripcion": "Alivio dolor agudo en 5º metatarsiano.",
            "sintomas": "Dolor borde exterior del pie bajo dedo pequeño.",
            "posicion": "Panel de lado en suelo apuntando al lateral del pie.",
            "tips_ant": ["Pie limpio"], "tips_des": ["Movilidad dedos"]
        }
    },
    "Hombro": {
        "Tendinitis": {
            "ondas": "660+850", "energia": "660nm: 50% | 850nm: 100%", 
            "hz": "10-40Hz", "dist": "15cm", "dur": 10,
            "frecuencias": [(660, 50), (850, 100)],
            "descripcion": "Para manguito rotador inflamado.",
            "sintomas": "Dolor al levantar brazo lateralmente.",
            "posicion": "Sentado, panel lateral apuntando al deltoides.",
            "tips_ant": ["Sin ropa"], "tips_des": ["Péndulos"]
        }
    },
    "Rodilla": {
        "Dolor General": {
            "ondas": "660+850", "energia": "660nm: 50% | 850nm: 100%", 
            "hz": "10Hz", "dist": "15cm", "dur": 10,
            "frecuencias": [(660, 50), (850, 100)],
            "descripcion": "Mantenimiento articular y meniscos.",
            "sintomas": "Molestia profunda o chasquidos.",
            "posicion": "Pierna estirada, panel frontal o lateral.",
            "tips_ant": ["No hielo antes"], "tips_des": ["Movilidad"]
        }
    },
    "Piel": {
        "Cicatrices": {
            "ondas": "630+660", "energia": "660nm: 100% | 850nm: 20%", 
            "hz": "CW", "dist": "10cm", "dur": 10,
            "frecuencias": [(660, 100), (850, 20)],
            "descripcion": "Mejora textura y color de cicatrices.",
            "sintomas": "Tejido cicatricial reciente o antiguo.",
            "posicion": "Panel directo a la cicatriz.",
            "tips_ant": ["Limpio"], "tips_des": ["Rosa Mosqueta"]
        },
        "Acné": {
            "ondas": "630+660", "energia": "660nm: 80% | 850nm: 0%", 
            "hz": "CW", "dist": "15cm", "dur": 8,
            "frecuencias": [(660, 80), (850, 0)],
            "descripcion": "Reduce inflamación bacteriana y rojez.",
            "sintomas": "Brotes activos, rojez facial.",
            "posicion": "Frente al rostro (gafas puestas).",
            "tips_ant": ["Limpio"], "tips_des": ["Hidratar"]
        },
        "Quemaduras": {
            "ondas": "630+660", "energia": "660nm: 50% | 850nm: 0%", 
            "hz": "CW", "dist": "20cm", "dur": 5,
            "frecuencias": [(660, 50), (850, 0)],
            "descripcion": "Regeneración epidérmica sin calor.",
            "sintomas": "Piel roja o dañada por sol/calor.",
            "posicion": "Mayor distancia (20-30cm).",
            "tips_ant": ["Sin cremas"], "tips_des": ["Aloe Vera"]
        }
    },
    "Sistémico": {
        "Circulación": {
            "ondas": "660+850", "energia": "100% | 100%", 
            "hz": "CW", "dist": "30cm", "dur": 20,
            "frecuencias": [(660, 100), (850, 100)],
            "descripcion": "Vasodilatación general.",
            "sintomas": "Piernas cansadas, frío en extremidades.",
            "posicion": "Panel cubriendo grandes grupos musculares.",
            "tips_ant": ["Beber agua"], "tips_des": ["Caminar"]
        },
        "Energía": {
            "ondas": "660+850", "energia": "100% | 100%", 
            "hz": "CW", "dist": "20cm", "dur": 10,
            "frecuencias": [(660, 100), (850, 100)],
            "descripcion": "Estimulación mitocondrial.",
            "sintomas": "Fatiga general, falta de energía.",
            "posicion": "Panel frente al torso/pecho.",
            "tips_ant": ["Mañana"], "tips_des": ["Actividad"]
        }
    },
    "Cabeza": {
        "Migraña": {
            "ondas": "850nm", "energia": "660nm: 0% | 850nm: 50%", 
            "hz": "10Hz (Alfa)", "dist": "Contacto Nuca", "dur": 10,
            "frecuencias": [(660, 0), (850, 50)],
            "descripcion": "Relajación occipital para tensión vascular.",
            "sintomas": "Dolor pulsátil, tensión en nuca.",
            "posicion": "Panel en la nuca (NO ojos).",
            "tips_ant": ["Oscuridad"], "tips_des": ["Reposo"]
        },
        "Salud Cerebral": {
            "ondas": "810nm", "energia": "0% | 100%", 
            "hz": "40Hz (Gamma)", "dist": "30cm", "dur": 10,
            "frecuencias": [(810, 100)],
            "descripcion": "Neuroprotección y cognitiva.",
            "sintomas": "Niebla mental, prevención.",
            "posicion": "Panel a la frente/cabeza. GAFAS OBLIGATORIAS.",
            "tips_ant": ["Gafas"], "tips_des": ["Tarea cognitiva"]
        }
    },
    "Grasa/Estética": {
        "Grasa Localizada": {
            "ondas": "Todas (Mega)", "energia": "TODO AL 100%", 
            "hz": "CW (Continuo)", "dist": "20-30cm", "dur": 15,
            "frecuencias": [(660, 100), (850, 100), (810, 100), (830, 100), (630, 100)],
            "descripcion": "Lipólisis térmica máxima.",
            "sintomas": "Grasa resistente.",
            "posicion": "Directo a piel desnuda. EJERCICIO INMEDIATO.",
            "tips_ant": ["Beber agua"], "tips_des": ["Cardio 30min"],
            "visual_group": "PRE", "req_tags": ["Active"]
        },
        "Facial": {
            "ondas": "630nm", "energia": "100% | 0%", 
            "hz": "CW", "dist": "30cm", "dur": 10,
            "frecuencias": [(630, 100), (660, 50)],
            "descripcion": "Colágeno superficial.",
            "sintomas": "Arrugas finas, piel apagada.",
            "posicion": "Frente al rostro 30cm. GAFAS PUESTAS.",
            "tips_ant": ["Gafas"], "tips_des": ["Serum"],
            "visual_group": "FLEX", "momento_txt": "Cualquier hora"
        }
    },
    "Permanente": {
        "Testosterona": {
            "ondas": "660+850", "energia": "100% | 100%", 
            "hz": "CW", "dist": "15cm", "dur": 5,
            "frecuencias": [(660, 100), (850, 100)],
            "descripcion": "Estimulación mitocondrial hormonal.",
            "sintomas": "Optimización hormonal.",
            "posicion": "Directo a zona testicular.",
            "tips_ant": ["Limpio"], "tips_des": ["Ducha fría"],
            "visual_group": "MORNING"
        },
        "Sueño": {
            "ondas": "Solo ROJO", "energia": "Rojo: 30% | NIR: 0%", 
            "hz": "CW (Continuo)", "dist": ">1 Metro", "dur": 20,
            "frecuencias": [(630, 30), (660, 30), (810, 0), (830, 0), (850, 0)],
            "descripcion": "Luz ambiente tenue para melatonina.",
            "sintomas": "Insomnio, dificultad para desconectar.",
            "posicion": "Panel lejos, luz indirecta contra pared.",
            "tips_ant": ["Oscuridad"], "tips_des": ["Dormir"],
            "visual_group": "NIGHT"
        }
    }
}

# ==============================================================================
# 3. CLASES Y MODELO DE DATOS
# ==============================================================================
class Tratamiento:
    def __init__(self, id_t, nombre, zona, ondas_txt, config_energia, herzios, distancia, duracion, max_diario, max_semanal, tipo, tags_entreno, default_visual_group, momento_ideal_txt, momentos_prohibidos, tips_antes, tips_despues, incompatible_with=None, fases_config=None, es_custom=False, patologia="", lado_txt="", frecuencias=None, descripcion="", sintomas="", posicion=""):
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
        self.fases_config = fases_config if fases_config else []
        self.es_custom = es_custom
        self.patologia = patologia
        self.lado_txt = lado_txt
        self.frecuencias = frecuencias if frecuencias else []
        self.descripcion = descripcion
        self.sintomas = sintomas
        self.posicion = posicion

    def set_incompatibilidades(self, texto):
        self.incompatibilidades = texto
        return self

# --- GENERADOR DE CATÁLOGO ---
def obtener_catalogo(tratamientos_custom=[]):
    fases_lesion = [{"nombre": "🔥 Fase 1: Inflamatoria", "dias_fin": 7}, {"nombre": "🛠️ Fase 2: Proliferación", "dias_fin": 21}, {"nombre": "🧱 Fase 3: Remodelación", "dias_fin": 60}]
    catalogo = []
    ids_procesados = set()

    # 1. Custom
    for c in tratamientos_custom:
        catalogo.append(Tratamiento(
            c['id'], c['nombre'], c['zona'], c['ondas'], c['energia'], c['hz'], c['dist'], c['dur'], 
            1, 7, c['tipo'], ['All'], "FLEX", "Personalizado", [], c['tips_ant'], c['tips_des'], 
            fases_config=c.get('fases', []), es_custom=True,
            patologia=c['nombre'], lado_txt="Custom", frecuencias=c.get('frecuencias', []), 
            descripcion=c.get('descripcion', ''), sintomas=c.get('sintomas', ''), posicion=c.get('posicion', '')
        ))
        ids_procesados.add(c['id'])

    # 2. Base
    for zona, patologias in DB_TRATAMIENTOS_BASE.items():
        for patologia, specs in patologias.items():
            freqs = specs.get("frecuencias", [(660, 50), (850, 100)])
            desc = specs.get("descripcion", "")
            sint = specs.get("sintomas", "")
            pos = specs.get("posicion", "")
            v_group = specs.get("visual_group", "FLEX")
            req_tags = specs.get("req_tags", ['All'])
            momento_txt = specs.get("momento_txt", "Flexible")
            
            lados_a_generar = [("g", "General")] 
            if zona in ZONAS_SIMETRICAS:
                lados_a_generar = [("d", "Derecho"), ("i", "Izquierdo")]
            elif zona == "Abdomen": 
                if "Frontal" in patologia: lados_a_generar = [("f", "Frontal")]
            
            if zona == "Grasa/Estética" and "Grasa Localizada" in patologia:
                pass 
            else:
                for codigo, nombre_lado in lados_a_generar:
                    base_id = f"{zona[:3]}_{patologia[:4]}_{codigo}".lower().replace(" ", "")
                    id_t = "".join(ch for ch in base_id if ch.isalnum() or ch=="_")
                    nombre_final = f"{zona} {nombre_lado} ({patologia})" if nombre_lado != "General" else f"{zona} ({patologia})"
                    if id_t not in ids_procesados:
                        catalogo.append(Tratamiento(
                            id_t, nombre_final, zona, specs["ondas"], specs["energia"], specs["hz"], specs["dist"], specs["dur"], 
                            1, 7, "LESION", req_tags, v_group, momento_txt, [], specs.get("tips_ant", []), specs.get("tips_des", []), fases_config=fases_lesion,
                            patologia=patologia, lado_txt=nombre_lado, frecuencias=freqs, descripcion=desc, sintomas=sint, posicion=pos
                        ))

    # 3. Inyectar estáticos históricos de Grasa
    s = DB_TRATAMIENTOS_BASE["Grasa/Estética"]["Grasa Localizada"]
    for sufijo, nombre, lado in [("front", "Frontal", "Frontal"), ("d", "Flanco D", "Flanco Dcho"), ("i", "Flanco I", "Flanco Izq"), ("glutes", "Glúteos", "General")]:
        id_t = f"fat_{sufijo}"
        if id_t not in ids_procesados:
            catalogo.append(Tratamiento(id_t, f"Grasa {nombre}", "Abdomen", s["ondas"], s["energia"], s["hz"], s["dist"], s["dur"], 1, 7, "GRASA", ["Active"], "PRE", "Pre-Entreno", ["🌙 Noche"], s["tips_ant"], s["tips_des"], patologia="Grasa Localizada", lado_txt=lado, frecuencias=s.get("frecuencias"), descripcion=s.get("descripcion"), sintomas=s.get("sintomas"), posicion=s.get("posicion")))

    return catalogo

# ==============================================================================
# 4. GESTIÓN DE DATOS Y PERSISTENCIA
# ==============================================================================
def cargar_datos_completos():
    default_db = {
        "configuracion_rutina": {"semana": RUTINA_SEMANAL, "tags": TAGS_ACTIVIDADES},
        "usuario_rutina": {"historial": {}, "meta_diaria": {}, "meta_cardio": {}, "ciclos_activos": {}, "descartados": {}, "planificados_adhoc": {}, "tratamientos_custom": [], "confirmaciones_diarias": {}}, 
        "usuario_libre": {"historial": {}, "meta_diaria": {}, "meta_cardio": {}, "ciclos_activos": {}, "descartados": {}, "planificados_adhoc": {}, "tratamientos_custom": [], "confirmaciones_diarias": {}}
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
                if "confirmaciones_diarias" not in datos[user]: datos[user]["confirmaciones_diarias"] = {}
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
        return {"semana": nueva_semana, "tags": TAGS_ACTIVIDADES}
    except: return None

# --- 5. LÓGICA AI (GEMINI) ---
def consultar_ia(dolencia):
    api_key = None
    try: api_key = st.secrets["GEMINI_API_KEY"]
    except: pass
    if not api_key and 'api_key_val' in st.session_state: api_key = st.session_state.api_key_val
    if not api_key: return None

    genai.configure(api_key=api_key)
    
    prompt = f"""
    Actúa como experto en Fotobiomodulación. Usuario: "{dolencia}".
    Genera una LISTA de posibles tratamientos en formato JSON Array.
    Cada objeto debe tener:
    {{
        "nombre": "Título",
        "zona": "Parte cuerpo",
        "descripcion": "Qué hace biológicamente (max 20 palabras)",
        "sintomas": "Síntomas que confirma (max 20 palabras)",
        "posicion": "Cómo poner el panel y el cuerpo (max 20 palabras)",
        "ondas": "660+850",
        "energia": "Texto resumen",
        "frecuencias": [[660, 50], [850, 100]],
        "hz": "Texto Hz",
        "dist": "Texto dist",
        "dur": 10,
        "tips_ant": ["Tip 1"],
        "tips_des": ["Tip 1"],
        "es_lesion": true,
        "tipo": "LESION"
    }}
    Devuelve un JSON Array con 1 a 3 opciones.
    """
    
    modelos = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
    for m in modelos:
        try:
            model = genai.GenerativeModel(m)
            response = model.generate_content(prompt)
            clean = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean)
            if isinstance(data, dict): data = [data]
            return data
        except: continue
    return None

# --- 6. HELPERS VISUALES ---
def mostrar_visualizador_mega(t):
    if not t.frecuencias: return
    st.caption("Configuración Panel:")
    cols = st.columns(len(t.frecuencias))
    for idx, (nm, pct) in enumerate(t.frecuencias):
        bg = "#ffebee" if pct >= 80 else "#f5f5f5"
        border = "#ef5350" if pct >= 80 else "#bdbdbd"
        txt = "#b71c1c" if pct >= 80 else "#616161"
        cols[idx].markdown(f"""<div style="background-color:{bg};border:1px solid {border};border-radius:5px;padding:5px;text-align:center;font-size:12px;color:{txt};font-weight:bold;">{nm}nm<br>{pct}%</div>""", unsafe_allow_html=True)

def mostrar_ficha_tecnica(t, lista_completa):
    if t.descripcion: st.info(f"ℹ️ **Info:** {t.descripcion}")
    c_sin, c_pos = st.columns(2)
    with c_sin:
        if t.sintomas: st.markdown(f"**🩺 Síntomas:**\n{t.sintomas}")
    with c_pos:
        if t.posicion: st.warning(f"**🧘 Posición:**\n{t.posicion}")
    
    mostrar_visualizador_mega(t)
    st.divider()
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"**Zona:** {t.zona}\n**Intensidad:** {t.config_energia}")
    with c2: st.markdown(f"**Hz:** {t.herzios}\n**Tiempo:** {t.duracion} min ({t.distancia})")
    
    with st.expander("Consejos"):
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
        if ciclo and ciclo.get('activo'): presentes.add(t.id)
    return presentes

# ==============================================================================
# 7. UI PRINCIPAL
# ==============================================================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def login_screen():
    st.title("🔐 Acceso")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        usr = st.selectbox("Usuario", ["Seleccionar...", "Benja", "Eva"])
        if st.button("Entrar", use_container_width=True) and usr != "Seleccionar...":
            st.session_state.logged_in = True
            st.session_state.current_user_name = usr
            st.session_state.current_user_role = "usuario_rutina" if usr == "Benja" else "usuario_libre"
            st.rerun()

if not st.session_state.logged_in: login_screen(); st.stop()

if 'db_global' not in st.session_state: st.session_state.db_global = cargar_datos_completos()
clave_usuario = st.session_state.current_user_role
db_usuario = st.session_state.db_global[clave_usuario]
lista_tratamientos = obtener_catalogo(db_usuario.get("tratamientos_custom", []))

with st.sidebar:
    st.write(f"Hola, **{st.session_state.current_user_name}**")
    menu_navegacion = st.radio("Menú", ["📅 Panel Diario", "🗓️ Panel Semanal", "📊 Historial", "🚑 Clínica", "🔍 Buscador AI", "🗂️ Gestionar Tratamientos"])
    if HAS_GEMINI:
        try: _ = st.secrets["GEMINI_API_KEY"]
        except: 
            if 'api_key_val' not in st.session_state: st.session_state.api_key_val = ""
            api_key = st.text_input("🔑 OpenAI API Key (Gemini)", type="password", value=st.session_state.api_key_val)
            if api_key: st.session_state.api_key_val = api_key
    st.divider()
    if st.button("💾 Guardar Todo"):
        guardar_datos_completos(st.session_state.db_global); st.success("Guardado.")
    if st.button("Cerrar Sesión"): st.session_state.logged_in = False; st.rerun()

# --- VISTAS ---
if menu_navegacion == "📅 Panel Diario":
    st.title("📅 Panel Diario")
    c_f, c_r = st.columns([2,1])
    fecha_seleccionada = c_f.date_input("Fecha", datetime.date.today())
    fecha_str = fecha_seleccionada.isoformat()
    
    rutina_fuerza, rutina_cardio, tags_dia, man_f, man_c, todas_rutinas = obtener_rutina_completa(fecha_seleccionada, st.session_state.db_global, db_usuario)
    confirmado = db_usuario.get("confirmaciones_diarias", {}).get(fecha_str, False)

    if clave_usuario == "usuario_rutina":
        if not confirmado:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**🏋️ Fuerza**")
                def_f = [x for x in rutina_fuerza if "Descanso" not in x]
                sel_f = st.multiselect("Rutina:", def_f, default=def_f, key=f"sf_{fecha_str}")
                if set(sel_f) != set(rutina_fuerza):
                    if "meta_diaria" not in db_usuario: db_usuario["meta_diaria"] = {}
                    db_usuario["meta_diaria"][fecha_str] = sel_f
            with c2:
                st.markdown("**🏃 Cardio**")
                idx = list(GENERIC_CARDIO_PARAMS.keys()).index(rutina_cardio.get("actividad", "Descanso Cardio")) if rutina_cardio.get("actividad") in GENERIC_CARDIO_PARAMS else 0
                sel_c = st.selectbox("Actividad:", ["Descanso Cardio"] + list(GENERIC_CARDIO_PARAMS.keys())[:-1], index=idx, key=f"sc_{fecha_str}")
                params = rutina_cardio.copy(); params["actividad"] = sel_c
                if sel_c != "Descanso Cardio":
                    cp1, cp2 = st.columns(2)
                    params["tiempo"] = cp1.number_input("Min:", value=params.get("tiempo", 15), key=f"t_{fecha_str}")
                    if "velocidad" in GENERIC_CARDIO_PARAMS.get(sel_c, {}):
                        params["velocidad"] = cp2.number_input("Km/h:", value=float(params.get("velocidad", 6.5)), step=0.5, format="%.1f", key=f"v_{fecha_str}")
                    if "inclinacion" in GENERIC_CARDIO_PARAMS.get(sel_c, {}):
                        params["inclinacion"] = cp2.number_input("Inc %:", value=float(params.get("inclinacion", 0.0)), step=0.5, format="%.1f", key=f"i_{fecha_str}")
                if params != rutina_cardio:
                    if "meta_cardio" not in db_usuario: db_usuario["meta_cardio"] = {}
                    db_usuario["meta_cardio"][fecha_str] = params
                    guardar_datos_completos(st.session_state.db_global); st.rerun()
            
            if st.button("✅ Confirmar Rutina", type="primary", use_container_width=True):
                if "confirmaciones_diarias" not in db_usuario: db_usuario["confirmaciones_diarias"] = {}
                db_usuario["confirmaciones_diarias"][fecha_str] = True
                guardar_datos_completos(st.session_state.db_global); st.rerun()
        else:
            st.success(f"Rutina: {', '.join(rutina_fuerza)} | {rutina_cardio.get('actividad')}")
            if st.button("✏️ Editar"): 
                db_usuario["confirmaciones_diarias"][fecha_str] = False; guardar_datos_completos(st.session_state.db_global); st.rerun()

    st.divider()
    
    # ADD MANUAL
    if confirmado or clave_usuario == "usuario_libre":
        with st.expander("➕ Añadir Tratamiento Manual"):
            zonas = sorted(list(set(t.zona for t in lista_tratamientos)))
            z_sel = st.selectbox("Zona:", ["--"] + zonas, key="mz_sel")
            if z_sel != "--":
                pats = sorted(list(set(t.patologia for t in lista_tratamientos if t.zona == z_sel)))
                p_sel = st.selectbox("Tratamiento:", ["--"] + pats, key="mp_sel")
                if p_sel != "--":
                    vars_objs = [t for t in lista_tratamientos if t.zona == z_sel and t.patologia == p_sel]
                    v_sel = st.selectbox("Lado/Variante:", [t.nombre for t in vars_objs], key="mv_sel")
                    
                    t_obj = next((t for t in vars_objs if t.nombre == v_sel), None)
                    if t_obj:
                        if t_obj.sintomas: st.info(f"**Síntomas:** {t_obj.sintomas}")
                        if t_obj.posicion: st.warning(f"**Posición:** {t_obj.posicion}")
                        
                        if st.button("Añadir al Día"):
                            if "planificados_adhoc" not in db_usuario: db_usuario["planificados_adhoc"] = {}
                            if fecha_str not in db_usuario["planificados_adhoc"]: db_usuario["planificados_adhoc"][fecha_str] = {}
                            db_usuario["planificados_adhoc"][fecha_str][t_obj.id] = "FLEX"
                            guardar_datos_completos(st.session_state.db_global); st.rerun()

    # RENDER TARJETAS
    adhoc = db_usuario.get("planificados_adhoc", {}).get(fecha_str, {})
    presentes = obtener_tratamientos_presentes(fecha_str, db_usuario, lista_tratamientos)
    registros = db_usuario["historial"].get(fecha_str, {})
    
    to_show = []
    for t in lista_tratamientos:
        if t.id in adhoc or t.id in registros: to_show.append((t, "adhoc"))
        else:
            ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
            if ciclo and ciclo['activo']: to_show.append((t, "clinica"))
    
    for t, origen in to_show:
        hechos = len(registros.get(t.id, []))
        icon = "✅" if hechos >= t.max_diario else ("🩺" if origen == "clinica" else "📍")
        with st.expander(f"{icon} {t.nombre} ({hechos}/{t.max_diario})"):
            if hechos >= t.max_diario:
                st.success("Completado")
                if st.button("Deshacer", key=f"undo_{t.id}"):
                    del db_usuario["historial"][fecha_str][t.id]
                    guardar_datos_completos(st.session_state.db_global); st.rerun()
            else:
                mostrar_ficha_tecnica(t, lista_tratamientos)
                if st.button("Registrar Ahora", key=f"reg_{t.id}"):
                    now = datetime.datetime.now().strftime('%H:%M')
                    if fecha_str not in db_usuario["historial"]: db_usuario["historial"][fecha_str] = {}
                    if t.id not in db_usuario["historial"][fecha_str]: db_usuario["historial"][fecha_str][t.id] = []
                    db_usuario["historial"][fecha_str][t.id].append({"hora": now, "detalle": "Manual"})
                    guardar_datos_completos(st.session_state.db_global); st.rerun()
                if origen == "adhoc" and st.button("Quitar del plan", key=f"del_{t.id}"):
                    del db_usuario["planificados_adhoc"][fecha_str][t.id]
                    guardar_datos_completos(st.session_state.db_global); st.rerun()

elif menu_navegacion == "🔍 Buscador AI":
    st.title("🔍 Buscador & Generador AI")
    if not HAS_GEMINI: st.error("Falta API Key"); st.stop()
    
    if 'ai_results' not in st.session_state: st.session_state.ai_results = []
    
    q = st.text_input("Describe dolencia:")
    if st.button("Buscar") and q:
        with st.spinner("Generando opciones visuales..."):
            res = consultar_ia(q)
            if res: st.session_state.ai_results = res
    
    if st.session_state.ai_results:
        st.write(f"He encontrado {len(st.session_state.ai_results)} opciones:")
        for i, r in enumerate(st.session_state.ai_results):
            with st.container(border=True):
                st.subheader(r['nombre'])
                temp = Tratamiento("prev", r['nombre'], r['zona'], r['ondas'], r['energia'], r['hz'], r['dist'], r['dur'], 1, 7, "AI", [], "FLEX", "AI", [], r['tips_ant'], r['tips_des'], frecuencias=r.get('frecuencias'), descripcion=r.get('descripcion'), sintomas=r.get('sintomas'), posicion=r.get('posicion'))
                mostrar_ficha_tecnica(temp, [])
                
                c1, c2, c3 = st.columns(3)
                if c1.button(f"💾 Guardar Disponibles", key=f"s_{i}"):
                    id_new = str(uuid.uuid4())[:8]; r['id'] = id_new
                    db_usuario["tratamientos_custom"].append(r)
                    guardar_datos_completos(st.session_state.db_global)
                    st.success("Guardado!"); st.rerun()
                
                if c2.button(f"📅 Planificar Hoy", key=f"p_{i}"):
                    id_new = str(uuid.uuid4())[:8]; r['id'] = id_new; r['tipo'] = 'PUNTUAL'
                    db_usuario["tratamientos_custom"].append(r)
                    hoy = datetime.date.today().isoformat()
                    if "planificados_adhoc" not in db_usuario: db_usuario["planificados_adhoc"] = {}
                    if hoy not in db_usuario["planificados_adhoc"]: db_usuario["planificados_adhoc"][hoy] = {}
                    db_usuario["planificados_adhoc"][hoy][id_new] = "FLEX"
                    guardar_datos_completos(st.session_state.db_global)
                    st.success("Añadido a hoy!"); st.rerun()
                
                if c3.button(f"🚑 Empezar Clínica", key=f"c_{i}"):
                    id_new = str(uuid.uuid4())[:8]; r['id'] = id_new; r['tipo'] = 'LESION'
                    r['fases'] = [{"nombre": "Estándar", "dias_fin": 30}]
                    db_usuario["tratamientos_custom"].append(r)
                    if "ciclos_activos" not in db_usuario: db_usuario["ciclos_activos"] = {}
                    db_usuario["ciclos_activos"][id_new] = {"fecha_inicio": datetime.date.today().isoformat(), "activo": True, "modo": "fases", "estado": "activo", "dias_saltados": []}
                    guardar_datos_completos(st.session_state.db_global)
                    st.success("Clínica iniciada!"); st.rerun()
        
        if st.button("Limpiar Búsqueda"):
            st.session_state.ai_results = []
            st.rerun()

elif menu_navegacion == "🗂️ Gestionar Tratamientos":
    st.title("🗂️ Gestionar Tratamientos")
    nombres = [t.nombre for t in lista_tratamientos]
    sel = st.selectbox("Editar:", ["--"] + nombres)
    if sel != "--":
        t = next(x for x in lista_tratamientos if x.nombre == sel)
        with st.form("edit"):
            nn = st.text_input("Nombre", t.nombre)
            nd = st.text_area("Descripción", t.descripcion)
            ns = st.text_area("Síntomas", t.sintomas)
            np = st.text_area("Posición", t.posicion)
            if st.form_submit_button("Guardar"):
                new_data = t.__dict__.copy()
                new_data['nombre'] = nn; new_data['descripcion'] = nd
                new_data['sintomas'] = ns; new_data['posicion'] = np
                new_data['id'] = str(uuid.uuid4())[:8] if not t.es_custom else t.id
                
                if t.es_custom:
                    db_usuario["tratamientos_custom"] = [x for x in db_usuario["tratamientos_custom"] if x['id'] != t.id]
                db_usuario["tratamientos_custom"].append(new_data)
                guardar_datos_completos(st.session_state.db_global)
                st.success("Guardado!"); st.rerun()
        
        if t.es_custom and st.button("Borrar"):
            db_usuario["tratamientos_custom"] = [x for x in db_usuario["tratamientos_custom"] if x['id'] != t.id]
            guardar_datos_completos(st.session_state.db_global)
            st.success("Borrado!"); st.rerun()

elif menu_navegacion == "🚑 Clínica":
    st.title("🚑 Clínica")
    
    with st.expander("🆕 Iniciar Tratamiento Manualmente"):
        zonas = sorted(list(set(t.zona for t in lista_tratamientos)))
        z_sel = st.selectbox("Zona:", ["--"] + zonas, key="cz_sel")
        if z_sel != "--":
            pats = sorted(list(set(t.patologia for t in lista_tratamientos if t.zona == z_sel)))
            p_sel = st.selectbox("Tratamiento:", ["--"] + pats, key="cp_sel")
            if p_sel != "--":
                vars_objs = [t for t in lista_tratamientos if t.zona == z_sel and t.patologia == p_sel]
                v_sel = st.selectbox("Lado/Variante:", [t.nombre for t in vars_objs], key="cv_sel")
                
                if st.button("Iniciar Ciclo"):
                    t_obj = next((t for t in vars_objs if t.nombre == v_sel), None)
                    if t_obj:
                        if "ciclos_activos" not in db_usuario: db_usuario["ciclos_activos"] = {}
                        db_usuario["ciclos_activos"][t_obj.id] = {"fecha_inicio": datetime.date.today().isoformat(), "activo": True}
                        guardar_datos_completos(st.session_state.db_global); st.rerun()

    for t in lista_tratamientos:
        ciclo = db_usuario.get("ciclos_activos", {}).get(t.id)
        if ciclo and ciclo['activo']:
            st.info(f"En curso: {t.nombre} (Desde {ciclo['fecha_inicio']})")
            if st.button(f"Finalizar {t.nombre}"):
                ciclo['activo'] = False
                guardar_datos_completos(st.session_state.db_global); st.rerun()

elif menu_navegacion == "🗓️ Panel Semanal":
    st.title("🗓️ Panel Semanal")
    d_ref = st.date_input("Semana de:", datetime.date.today())
    start = d_ref - timedelta(days=d_ref.weekday())
    
    tabs = st.tabs(["L", "M", "X", "J", "V", "S", "D"])
    # AQUI ESTABA EL ERROR: Usar funciones auxiliares para renderizar cada día completo
    for i, tab in enumerate(tabs):
        with tab:
            dia = start + timedelta(days=i)
            fecha_dia_str = dia.isoformat()
            st.subheader(dia.strftime("%A %d/%m"))
            
            # Replicamos logica de renderizado ligera
            rut_f, rut_c, _, _, _, _ = obtener_rutina_completa(dia, st.session_state.db_global, db_usuario)
            st.markdown(f"**🏋️ {', '.join(rut_f)}** | **🏃 {rut_c.get('actividad', 'Descanso')}**")
            st.divider()
            
            # Tratamientos
            adhoc = db_usuario.get("planificados_adhoc", {}).get(fecha_dia_str, {})
            registros = db_usuario["historial"].get(fecha_dia_str, {})
            
            # Merge de tratamientos del día
            day_treatments = []
            for t in lista_tratamientos:
                is_adhoc = t.id in adhoc
                is_clinic = db_usuario.get("ciclos_activos", {}).get(t.id, {}).get('activo', False)
                if is_adhoc or is_clinic:
                    day_treatments.append((t, "clinica" if is_clinic else "adhoc"))

            if not day_treatments:
                st.caption("Sin tratamientos planificados.")
            
            for t, origen in day_treatments:
                hechos = len(registros.get(t.id, []))
                icon = "✅" if hechos >= 1 else ("🩺" if origen == "clinica" else "📍")
                with st.expander(f"{icon} {t.nombre}"):
                    mostrar_ficha_tecnica(t, lista_tratamientos)
                    if st.button("Registrar", key=f"w_reg_{t.id}_{i}"):
                        now = datetime.datetime.now().strftime('%H:%M')
                        if fecha_dia_str not in db_usuario["historial"]: db_usuario["historial"][fecha_dia_str] = {}
                        if t.id not in db_usuario["historial"][fecha_dia_str]: db_usuario["historial"][fecha_dia_str][t.id] = []
                        db_usuario["historial"][fecha_dia_str][t.id].append({"hora": now, "detalle": "Semanal"})
                        guardar_datos_completos(st.session_state.db_global); st.rerun()

elif menu_navegacion == "📊 Historial":
    st.title("📊 Historial")
    st.write(db_usuario.get("historial", {}))
