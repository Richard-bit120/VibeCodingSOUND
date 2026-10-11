import os
import uuid

MAX_FILE_SIZE_MB = 25  # Límite seguro para evitar saturación de memoria
FORMATOS_PERMITIDOS = ["wav", "mp3", "m4a", "flac"]

def validar_y_guardar_audio(uploaded_file):
    """
    Valida el formato, comprueba que el archivo tenga contenido 
    y lo almacena de forma segura en disco con un nombre único UUID.
    """
    if uploaded_file is None:
        return None, "No se ha proporcionado ningún archivo de audio."

    # Validar extensión
    extension = uploaded_file.name.split(".")[-1].lower()
    if extension not in FORMATOS_PERMITIDOS:
        return None, f"Formato no compatible ('.{extension}'). Use: {', '.join(FORMATOS_PERMITIDOS)}"

    # Validar tamaño (en bytes)
    bytes_data = uploaded_file.read()
    tamanio_mb = len(bytes_data) / (1024 * 1024)
    if tamanio_mb > MAX_FILE_SIZE_MB:
        return None, f"El archivo supera el tamaño máximo permitido ({MAX_FILE_SIZE_MB} MB)."

    if len(bytes_data) == 0:
        return None, "El archivo de audio está vacío."

    # Guardar archivo de manera segura con UUID
    nombre_seguro = f"{uuid.uuid4()}_{uploaded_file.name}"
    ruta_destino = os.path.join("audio_uploads", nombre_seguro)
    
    with open(ruta_destino, "wb") as f:
        f.write(bytes_data)

    return ruta_destino, None