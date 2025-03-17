import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import whisper
import ollama
from gtts import gTTS
import os
import sounddevice as sd
import soundfile as sf
from playsound import playsound
import uuid
import asyncio
import logging

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)

# Obtener la ruta del directorio del script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Configuración de Whisper
whisper_model = whisper.load_model("tiny")

# Configuración de Ollama
model_name = "mistral"

# Nombre del asistente
nombre_asistente = "ELISA"

# Variable para almacenar el nombre del usuario
nombre_usuario = None

# Rutas relativas para archivos
temp_audio_path = os.path.join(script_dir, "grabacion.wav")
conversacion_path = os.path.join(script_dir, "conversacion.txt")

class AsistenteELISA(toga.App):
    def startup(self):
        # Diseño principal
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # Área de texto para la conversación
        self.conversacion = toga.MultilineTextInput(style=Pack(flex=1), readonly=True)
        main_box.add(self.conversacion)

        # Botón para grabar
        self.boton_grabar = toga.Button("Comenzar a grabar", on_press=self.iniciar_asistente, style=Pack(padding=5))
        main_box.add(self.boton_grabar)

        # Presentación del asistente
        self.actualizar_interfaz(f"{nombre_asistente}: ¡Hola! Soy ELISA, tu asistente virtual para ayudarte. ¿Cómo te llamas?")
        self.hablar("¡Hola! Soy ELISA, tu asistente virtual para ayudarte. ¿Cómo te llamas?")

        # Ventana principal
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def iniciar_asistente(self, widget):
        """Inicia la grabación y el procesamiento de audio."""
        self.boton_grabar.enabled = False
        self.actualizar_interfaz("Grabando...\n")
        asyncio.create_task(self.procesar_audio())  # Usar asyncio.create_task

    async def procesar_audio(self):
        """Procesa el audio grabado."""
        global nombre_usuario

        # Grabar audio
        self.grabar_audio()

        # Transcribir audio
        texto = self.transcribir_audio()
        self.actualizar_interfaz(f"Tú: {texto}\n")

        # Si es la primera interacción, guardar el nombre del usuario
        if nombre_usuario is None:
            nombre_usuario = texto
            respuesta = f"¡Mucho gusto, {nombre_usuario}! ¿En qué puedo ayudarte hoy?"
            self.actualizar_interfaz(f"{nombre_asistente}: {respuesta}\n")
            self.hablar(respuesta)
        else:
            # Generar respuesta
            respuesta = self.generar_respuesta(texto)
            self.actualizar_interfaz(f"{nombre_asistente}: {respuesta}\n")
            self.hablar(respuesta)

        # Guardar la conversación en un archivo de texto
        self.guardar_conversacion(f"Tú: {texto}\n{nombre_asistente}: {respuesta}\n")

        self.boton_grabar.enabled = True

    def grabar_audio(self):
        """Graba audio usando sounddevice."""
        try:
            samplerate = 16000  # Frecuencia de muestreo
            duration = 5  # Duración de la grabación en segundos
            logging.debug("Grabando...")
            audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
            sd.wait()  # Espera a que termine la grabación
            sf.write(temp_audio_path, audio, samplerate)  # Guarda el archivo
            logging.debug(f"Grabación guardada en {temp_audio_path}")
        except Exception as e:
            logging.error(f"Error al grabar audio: {e}")

    def transcribir_audio(self):
        """Transcribe el audio a texto usando Whisper."""
        if not os.path.exists(temp_audio_path):
            logging.error(f"Error: El archivo {temp_audio_path} no existe.")
            return ""
        try:
            # Cargar el audio y transcribirlo
            resultado = whisper_model.transcribe(temp_audio_path)
            return resultado["text"]  # Acceder directamente al texto transcrito
        except Exception as e:
            logging.error(f"Error al transcribir audio: {e}")
            return ""

    def generar_respuesta(self, texto):
        """Genera una respuesta usando Ollama."""
        try:
            prompt = (
                f"Eres {nombre_asistente}, un asistente virtual amigable y servicial para estudiantes de primaria y secundaria en Venezuela. "
                f"Responde al siguiente mensaje de manera clara, concisa y con un máximo de 50 palabras: {texto}"
            )
            respuesta = ollama.generate(
                model=model_name,
                prompt=prompt,
                options={"max_tokens": 50}  # Limita la respuesta a 50 tokens
            )
            return respuesta["response"]
        except Exception as e:
            logging.error(f"Error al generar respuesta: {e}")
            return "Lo siento, no pude generar una respuesta."

    def hablar(self, texto):
        """Convierte el texto en voz usando gTTS."""
        try:
            # Usar una ruta temporal única
            temp_tts_path = os.path.join(script_dir, f"respuesta_{uuid.uuid4()}.mp3")
            tts = gTTS(text=texto, lang="es")
            tts.save(temp_tts_path)
            playsound(temp_tts_path)  # Reproduce el archivo de audio
        except Exception as e:
            logging.error(f"Error al convertir texto a voz: {e}")

    def actualizar_interfaz(self, mensaje):
        """Actualiza la interfaz gráfica con un nuevo mensaje."""
        self.conversacion.value += mensaje

    def guardar_conversacion(self, mensaje):
        """Guarda la conversación en un archivo de texto."""
        try:
            with open(conversacion_path, "a", encoding="utf-8") as archivo:
                archivo.write(mensaje)
            logging.debug(f"Conversación guardada en {conversacion_path}")
        except Exception as e:
            logging.error(f"Error al guardar la conversación: {e}")

def main():
    return AsistenteELISA("AsistenteELISA", "org.example.asistenteelisa")

if __name__ == "__main__":
    app = main()
    app.main_loop()