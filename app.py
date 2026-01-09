import datetime

class MegaPanelTratamiento:
    def __init__(self, id_trat, nombre, zona, ondas, intensidad, distancia_cm, duracion_min, frecuencia, momento_ideal, incompatibilidades):
        self.id = id_trat
        self.nombre = nombre
        self.zona = zona  # Ej: "Rodilla Derecha"
        self.ondas = ondas  # Ej: "NIR + RED"
        self.intensidad = intensidad  # Ej: "100%"
        self.distancia_cm = distancia_cm  # Rango en cm
        self.duracion_min = duracion_min
        self.frecuencia = frecuencia
        self.momento_ideal = momento_ideal  # Ej: "Pre-Entreno", "Noche", "Flexible"
        self.incompatibilidades = incompatibilidades
        self.completado_hoy = False
        self.ultimo_registro = None

    def mostrar_instrucciones(self):
        print(f"\n--- CONFIGURACIÓN MEGA PANEL: {self.nombre.upper()} ---")
        print(f"🎯 Zona: {self.zona}")
        print(f"💡 Ondas: {self.ondas}")
        print(f"⚡ Intensidad: {self.intensidad}")
        print(f"wb📏 Distancia: {self.distancia_cm}")
        print(f"⏱️ Tiempo: {self.duracion_min} minutos")
        print(f"📅 Frecuencia: {self.frecuencia}")
        print(f"⚠️ PRECAUCIÓN: {self.incompatibilidades}")
        
        # Lógica de elección de momento (Pre/Post)
        if self.momento_ideal == "Flexible_Entreno":
            eleccion = input("\n¿Vas a realizarlo ANTES o DESPUÉS de entrenar? (Escribe 'antes' o 'despues'): ").lower()
            if eleccion == "antes":
                print("✅ Configuración PRE-ENTRENO seleccionada: Ideal para calentar tejido o movilizar grasa.")
            else:
                print("✅ Configuración POST-ENTRENO seleccionada: Ideal para recuperación y bajar inflamación.")
        elif self.momento_ideal == "Pre_Obligatorio":
            print("❗ IMPORTANTE: Realizar ANTES del ejercicio para movilizar la grasa.")
        elif self.momento_ideal == "Noche":
            print("🌙 MODO SUEÑO: Asegúrate de que la intensidad esté baja (10-20%) y no usar pulsos.")

    def marcar_completado(self):
        self.completado_hoy = True
        self.ultimo_registro = datetime.datetime.now()
        print(f"✅ Tratamiento '{self.nombre}' registrado correctamente a las {self.ultimo_registro.strftime('%H:%M')}.")

# --- BASE DE DATOS DE PROTOCOLOS (Actualizada con Manual + Ciencia) ---

protocolos = [
    # --- DOLOR ARTICULAR (Rodillas y Codos separados por lado) ---
    MegaPanelTratamiento(
        id_trat="rodilla_d", nombre="Rodilla Derecha (Dolor)", zona="Rodilla Derecha",
        ondas="NIR + RED (Todas ON)", intensidad="100%", distancia_cm="15-20 cm",
        duracion_min=10, frecuencia="6-7x/semana (2x/día si agudo)",
        momento_ideal="Flexible_Entreno",
        incompatibilidades="Implantes metálicos (vigilar calor), Cáncer activo."
    ),
    MegaPanelTratamiento(
        id_trat="rodilla_i", nombre="Rodilla Izquierda (Dolor)", zona="Rodilla Izquierda",
        ondas="NIR + RED (Todas ON)", intensidad="100%", distancia_cm="15-20 cm",
        duracion_min=10, frecuencia="6-7x/semana (2x/día si agudo)",
        momento_ideal="Flexible_Entreno",
        incompatibilidades="Implantes metálicos (vigilar calor), Cáncer activo."
    ),
    MegaPanelTratamiento(
        id_trat="codo_d", nombre="Codo Derecho (Dolor)", zona="Codo Derecho",
        ondas="NIR + RED (Todas ON)", intensidad="100%", distancia_cm="15-20 cm",
        duracion_min=10, frecuencia="6-7x/semana",
        momento_ideal="Flexible_Entreno",
        incompatibilidades="Infiltraciones recientes (esperar 5 días)."
    ),
    MegaPanelTratamiento(
        id_trat="codo_i", nombre="Codo Izquierdo (Dolor)", zona="Codo Izquierdo",
        ondas="NIR + RED (Todas ON)", intensidad="100%", distancia_cm="15-20 cm",
        duracion_min=10, frecuencia="6-7x/semana",
        momento_ideal="Flexible_Entreno",
        incompatibilidades="Infiltraciones recientes (esperar 5 días)."
    ),

    # --- PÉRDIDA DE GRASA (Flancos separados, distancia muy corta) ---
    MegaPanelTratamiento(
        id_trat="abdo_d", nombre="Flanco Abdominal Derecho (Grasa)", zona="Abdomen Derecho",
        ondas="NIR + RED (Todas ON)", intensidad="100%", distancia_cm="10-15 cm (Muy cerca)",
        duracion_min=10, frecuencia="5-7x/semana",
        momento_ideal="Pre_Obligatorio", # Prioridad Pre-Entreno
        incompatibilidades="Tatuajes oscuros (riesgo quemadura), Embarazo."
    ),
    MegaPanelTratamiento(
        id_trat="abdo_i", nombre="Flanco Abdominal Izquierdo (Grasa)", zona="Abdomen Izquierdo",
        ondas="NIR + RED (Todas ON)", intensidad="100%", distancia_cm="10-15 cm (Muy cerca)",
        duracion_min=10, frecuencia="5-7x/semana",
        momento_ideal="Pre_Obligatorio",
        incompatibilidades="Tatuajes oscuros (riesgo quemadura), Embarazo."
    ),

    # --- RECUPERACIÓN MUSCULAR (Antebrazos) ---
    MegaPanelTratamiento(
        id_trat="antebrazo_d", nombre="Antebrazo Derecho (Recuperación)", zona="Antebrazo Derecho",
        ondas="NIR + RED", intensidad="100%", distancia_cm="15-30 cm",
        duracion_min=10, frecuencia="3-5x/semana",
        momento_ideal="Flexible_Entreno", # Preferiblemente Post, pero flexible
        incompatibilidades="Ninguna específica. Opcional: Usar pulsos 50Hz."
    ),
    MegaPanelTratamiento(
        id_trat="antebrazo_i", nombre="Antebrazo Izquierdo (Recuperación)", zona="Antebrazo Izquierdo",
        ondas="NIR + RED", intensidad="100%", distancia_cm="15-30 cm",
        duracion_min=10, frecuencia="3-5x/semana",
        momento_ideal="Flexible_Entreno",
        incompatibilidades="Ninguna específica. Opcional: Usar pulsos 50Hz."
    ),

    # --- HORMONAL Y CEREBRAL (Protocolos Especiales) ---
    MegaPanelTratamiento(
        id_trat="testo", nombre="Boost Testosterona", zona="Testículos",
        ondas="NIR + RED", intensidad="100%", distancia_cm="15-20 cm",
        duracion_min=8, frecuencia="5-7x/semana",
        momento_ideal="Mañana",
        incompatibilidades="Tumores testiculares, Varicocele (consultar)."
    ),
    MegaPanelTratamiento(
        id_trat="cerebro", nombre="Salud Cerebral (Cognitivo)", zona="Cabeza/Frente",
        ondas="NIR (Infrarrojo)", intensidad="100%", distancia_cm="30 cm",
        duracion_min=10, frecuencia="5-7x/semana",
        momento_ideal="Flexible",
        incompatibilidades="USO OBLIGATORIO DE GAFAS (Protección Retina)."
    ),
    MegaPanelTratamiento(
        id_trat="sueno", nombre="Sueño y Ritmo Circadiano", zona="Cuerpo Completo / Ambiente",
        ondas="SOLO RED (Apagar NIR)", intensidad="10-20% (Baja)", distancia_cm=">50 cm",
        duracion_min=15, frecuencia="Diario",
        momento_ideal="Noche",
        incompatibilidades="NO USAR PULSOS (Epilepsia/Estimulación)."
    )
]

# --- EJEMPLO DE USO EN LA APP ---
def ejecutar_app():
    print("\n📱 --- APP MEGA PANEL CONTROL ---")
    print("Selecciona un tratamiento para ver configuración:")
    
    # Listar tratamientos disponibles
    for i, t in enumerate(protocolos):
        estado = "✅" if t.completado_hoy else "⬜"
        print(f"{i+1}. {estado} {t.nombre}")

    try:
        opcion = int(input("\nNúmero de tratamiento: ")) - 1
        if 0 <= opcion < len(protocolos):
            seleccionado = protocolos[opcion]
            seleccionado.mostrar_instrucciones()
            
            confirmar = input("\n¿Marcar como realizado? (s/n): ")
            if confirmar.lower() == 's':
                seleccionado.marcar_completado()
        else:
            print("Opción no válida.")
    except ValueError:
        print("Entrada no válida.")

# Simulación de ejecución
if __name__ == "__main__":
    ejecutar_app()
