import datetime
import json
import os

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
        # Tipos de momento: 'Flexible_Entreno', 'Pre_Obligatorio', 'Mañana', 'Noche', 'Cualquiera'
        self.momento_tipo = momento_tipo 
        self.incompatibilidades = incompatibilidades
        self.completado_hoy = False
        self.detalle_realizacion = "" # Para guardar si fue "Antes" o "Despues"

    def mostrar_info(self):
        print(f"\n{'='*60}")
        print(f"🔹 TRATAMIENTO: {self.nombre.upper()}")
        print(f"{'='*60}")
        print(f"📍 Zona:        {self.zona}")
        print(f"💡 Luces:       {self.ondas}")
        print(f"🔥 Intensidad:  {self.intensidad}")
        print(f"📏 Distancia:   {self.distancia}")
        print(f"⏱️  Duración:    {self.duracion} min")
        print(f"📅 Frecuencia:  {self.frecuencia}")
        print(f"⚠️  PRECAUCIÓN:  {self.incompatibilidades}")
        print(f"{'-'*60}")

    def realizar(self):
        ahora = datetime.datetime.now()
        hora_actual = ahora.hour
        
        # --- Lógica de Advertencia Horaria ---
        if self.momento_tipo == 'Mañana' and hora_actual > 12:
            print("⚠️  NOTA: Este tratamiento es óptimo por la MAÑANA (pico hormonal).")
        elif self.momento_tipo == 'Noche' and hora_actual < 19:
            print("⚠️  NOTA: Este tratamiento es para DORMIR. Hacerlo ahora podría darte sueño o no ser efectivo.")

        # --- Lógica de Selección de Momento (Entreno) ---
        nota_extra = ""
        
        if self.momento_tipo == 'Flexible_Entreno':
            while True:
                opcion = input("\n🏋️ ¿Vas a realizarlo ANTES o DESPUÉS de entrenar? (a/d): ").lower()
                if opcion.startswith('a'):
                    nota_extra = "Realizado PRE-ENTRENO (Calentamiento/Activación)"
                    print(f"✅ Registrando como: {nota_extra}")
                    break
                elif opcion.startswith('d'):
                    nota_extra = "Realizado POST-ENTRENO (Recuperación/Inflamación)"
                    print(f"✅ Registrando como: {nota_extra}")
                    break
                else:
                    print("Por favor, elige 'a' (Antes) o 'd' (Después).")
        
        elif self.momento_tipo == 'Pre_Obligatorio':
            print("\n🔥 IMPORTANTE: Debes realizar ejercicio físico en los próximos 30-60 min para oxidar la grasa liberada.")
            confirmar = input("¿Confirmas que vas a entrenar después? (s/n): ")
            if confirmar.lower() != 's':
                print("❌ Tratamiento cancelado. Sin ejercicio, la grasa se reabsorbe.")
                return False
            nota_extra = "Realizado PRE-ENTRENO (Obligatorio para Grasa)"

        # --- Confirmación Final ---
        if self.momento_tipo not in ['Flexible_Entreno', 'Pre_Obligatorio']:
             input("\nPresiona ENTER cuando termines la sesión...")

        self.completado_hoy = True
        self.detalle_realizacion = f"{ahora.strftime('%H:%M')} - {nota_extra}"
        print(f"\n✅ ¡Tratamiento '{self.nombre}' registrado con éxito!")
        return True

# --- BASE DE DATOS MAESTRA (Con tus parámetros actualizados) ---
def cargar_tratamientos():
    return [
        # --- DOLOR ARTICULAR ---
        Tratamiento("rodilla_d", "Rodilla Derecha (Dolor)", "Rodilla Dcha", "NIR + RED (Todo ON)", "100%", "15-20 cm", 10, "6-7x/sem", "Flexible_Entreno", "Implantes metálicos (calor), Cáncer activo."),
        Tratamiento("rodilla_i", "Rodilla Izquierda (Dolor)", "Rodilla Izq", "NIR + RED (Todo ON)", "100%", "15-20 cm", 10, "6-7x/sem", "Flexible_Entreno", "Implantes metálicos (calor), Cáncer activo."),
        Tratamiento("codo_d", "Codo Derecho (Dolor)", "Codo Dcho", "NIR + RED (Todo ON)", "100%", "15-20 cm", 10, "6-7x/sem", "Flexible_Entreno", "No usar si hubo infiltración hace <5 días."),
        Tratamiento("codo_i", "Codo Izquierdo (Dolor)", "Codo Izq", "NIR + RED (Todo ON)", "100%", "15-20 cm", 10, "6-7x/sem", "Flexible_Entreno", "No usar si hubo infiltración hace <5 días."),
        
        # --- GRASA (Distancia Corta + Pre-Entreno Obligatorio) ---
        Tratamiento("fat_d", "Flanco Derecho (Quema Grasa)", "Abdomen Dcho", "NIR + RED (Todo ON)", "100%", "10-15 cm (Muy Cerca)", 10, "5-7x/sem", "Pre_Obligatorio", "Cuidado con tatuajes oscuros. Embarazo prohibido."),
        Tratamiento("fat_i", "Flanco Izquierdo (Quema Grasa)", "Abdomen Izq", "NIR + RED (Todo ON)", "100%", "10-15 cm (Muy Cerca)", 10, "5-7x/sem", "Pre_Obligatorio", "Cuidado con tatuajes oscuros. Embarazo prohibido."),
        
        # --- RECUPERACIÓN MUSCULAR ---
        Tratamiento("arm_d", "Antebrazo Derecho (Músculo)", "Antebrazo Dcho", "NIR + RED", "100%", "15-30 cm", 10, "3-5x/sem", "Flexible_Entreno", "Opcional: Pulsos 50Hz para drenar."),
        Tratamiento("arm_i", "Antebrazo Izquierdo (Músculo)", "Antebrazo Izq", "NIR + RED", "100%", "15-30 cm", 10, "3-5x/sem", "Flexible_Entreno", "Opcional: Pulsos 50Hz para drenar."),
        
        # --- PROTOCOLOS ESPECIALES ---
        Tratamiento("testo", "Boost Testosterona", "Testículos", "NIR + RED", "100%", "15-20 cm", 5, "5-7x/sem", "Mañana", "No exceder tiempo. Consultar si hay varicocele."),
        Tratamiento("brain", "Salud Cerebral (Cognitivo)", "Cabeza/Frente", "SOLO NIR (Infrarrojo)", "100%", "30 cm", 10, "5-7x/sem", "Cualquiera", "⛔ GAFAS OBLIGATORIAS. NIR daña la retina si se mira fijo."),
        Tratamiento("sleep", "Sueño y Ritmo Circadiano", "Ambiente Habitación", "SOLO RED (Rojo)", "10-20% (Bajo)", "> 50 cm",
