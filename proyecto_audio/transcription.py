import whisper
import warnings

# Cargamos el modelo base de Whisper (se descarga automáticamente la primera vez)
# El modelo 'tiny' o 'base' es ideal para ejecución rápida en portátiles personales.
warnings.filterwarnings("ignore")
_modelo_whisper = None

def cargar_modelo_whisper():
    global _modelo_whisper
    if _modelo_whisper is None:
        # Usamos el modelo 'base' para equilibrar precisión en español y rendimiento local
        _modelo_whisper = whisper.load_model("base")
    return _modelo_whisper

def transcribir_audio(ruta_archivo):
    """
    Transcribe el archivo de audio a texto utilizando Whisper en español.
    """
    try:
        modelo = cargar_modelo_whisper()
        # Forzamos idioma español para mejorar la precisión del reconocimiento
        resultado = modelo.transcribe(ruta_archivo, language="es")
        texto_transcrito = resultado.get("text", "").strip()
        
        if not texto_transcrito:
            return None, "No se ha podido reconocer voz clara en el audio proporcionado."
            
        return texto_transcrito, None
    except Exception as e:
        return None, f"Error durante la transcripción de voz: {str(e)}"