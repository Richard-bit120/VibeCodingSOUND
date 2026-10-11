import streamlit as st
import pandas as pd
import os
from database import inicializar_base_datos, guardar_comentario_audio, obtener_historial_completo
from audio_processor import validar_y_guardar_audio
from transcription import transcribir_audio
from sentiment_analysis import analizar_sentimiento

# Configuración de página
st.set_page_config(
    page_title="Análisis de Audios de Comentarios",
    page_icon="🎙️",
    layout="wide"
)

# Inicializar base de datos y carpetas
inicializar_base_datos()

def main():
    st.title("🎙️ Sistema de Procesamiento y Análisis de Audios de Clientes")
    st.markdown(
        "Aplicación desarrollada para la materia **Ingeniería de Software**. "
        "Permite transcribir notas de voz de clientes, analizar su sentimiento mediante NLP e historizar los resultados."
    )

    menu = st.sidebar.selectbox(
        "Navegación", 
        ["Panel Principal", "Carga Individual de Audio", "Historial y Auditoría"]
    )

    if menu == "Panel Principal":
        st.header("📊 Métricas Generales del Sistema")
        registros = obtener_historial_completo()
        
        total = len(registros)
        exitosos = sum(1 for r in registros if r[10] == "Procesado Correctamente")
        positivos = sum(1 for r in registros if r[7] == "Positivo")
        negativos = sum(1 for r in registros if r[7] == "Negativo")
        neutrales = sum(1 for r in registros if r[7] == "Neutral")
        
        satisfaccion = (positivos / exitosos * 100) if exitosos > 0 else 0.0

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Audios", total)
        col2.metric("Procesados OK", exitosos)
        col3.metric("Positivos", positivos, delta="😊")
        col4.metric("Negativos", negativos, delta="😞", delta_color="inverse")
        col5.metric("Satisfacción", f"{satisfaccion:.1f}%")

        st.markdown("---")
        if total > 0:
            st.subheader("Distribución de Sentimientos en Audios")
            df_chart = pd.DataFrame({
                'Sentimiento': ['Positivo', 'Negativo', 'Neutral'],
                'Cantidad': [positivos, negativos, neutrales]
            })
            st.bar_chart(df_chart.set_index('Sentimiento'))
        else:
            st.info("Aún no hay audios procesados registrados en la base de datos.")

    elif menu == "Carga Individual de Audio":
        st.header("📤 Cargar y Procesar Audio de Comentario")
        
        with st.form("form_audio"):
            producto = st.text_input("Nombre o Identificador del Producto *")
            cliente = st.text_input("Identificador o Nombre del Cliente *")
            
            archivo_audio = st.file_uploader(
                "Selecciona un archivo de audio (WAV, MP3, M4A, FLAC)", 
                type=["wav", "mp3", "m4a", "flac"]
            )
            
            col_l, col_d = st.columns(2)
            with col_l:
                likes = st.number_input("Likes iniciales de la reseña", min_value=0, value=0)
            with col_d:
                dislikes = st.number_input("Dislikes iniciales de la reseña", min_value=0, value=0)

            submit = st.form_submit_button("🚀 Procesar Audio y Transcribir")

            if submit:
                if not producto.strip() or not cliente.strip():
                    st.error("Error: El producto y el cliente son obligatorios.")
                elif archivo_audio is None:
                    st.error("Error: Debes adjuntar un archivo de audio.")
                else:
                    # 1. Validar y guardar audio de forma segura
                    ruta_guardada, error_audio = validar_y_guardar_audio(archivo_audio)
                    if error_audio:
                        st.error(f"❌ {error_audio}")
                        guardar_comentario_audio(
                            producto, cliente, likes, dislikes, 
                            archivo_audio.name, "", "N/A", error_audio, "Error de Archivo"
                        )
                    else:
                        with st.spinner("🤖 Transcribiendo audio con IA (Whisper local)..."):
                            # 2. Transcribir audio
                            transcripcion, error_trans = transcribir_audio(ruta_guardada)
                            
                            if error_trans:
                                st.error(f"❌ {error_trans}")
                                guardar_comentario_audio(
                                    producto, cliente, likes, dislikes, 
                                    ruta_guardada, "", "N/A", error_trans, "Error de Transcripción"
                                )
                            else:
                                # 3. Analizar sentimiento
                                sentimiento, analisis = analizar_sentimiento(transcripcion)
                                
                                # 4. Guardar resultado exitoso
                                guardar_comentario_audio(
                                    producto, cliente, likes, dislikes, 
                                    ruta_guardada, transcripcion, sentimiento, analisis, "Procesado Correctamente"
                                )
                                
                                st.success("✅ ¡Audio procesado, transcrito y analizado con éxito!")
                                st.markdown(f"**Transcripción:** {transcripcion}")
                                st.markdown(f"**Sentimiento Detectado:** {sentimiento}")
                                st.info(f"**Análisis:** {analisis}")

    elif menu == "Historial y Auditoría":
        st.header("📋 Historial de Audios Procesados")
        registros = obtener_historial_completo()
        
        if not registros:
            st.info("No hay registros en la base de datos.")
        else:
            df = pd.DataFrame(registros, columns=[
                "ID", "Producto", "Cliente", "Likes", "Dislikes", 
                "Archivo", "Transcripción", "Sentimiento", "Análisis", "Fecha", "Estado"
            ])
            
            # Filtros interactivos
            col1, col2, col3 = st.columns(3)
            with col1:
                filtro_prod = st.selectbox("Filtrar por Producto", ["Todos"] + list(df["Producto"].unique()))
            with col2:
                filtro_sent = st.selectbox("Filtrar por Sentimiento", ["Todos"] + list(df["Sentimiento"].unique()))
            with col3:
                filtro_est = st.selectbox("Filtrar por Estado", ["Todos"] + list(df["Estado"].unique()))

            df_f = df.copy()
            if filtro_prod != "Todos":
                df_f = df_f[df_f["Producto"] == filtro_prod]
            if filtro_sent != "Todos":
                df_f = df_f[df_f["Sentimiento"] == filtro_sent]
            if filtro_est != "Todos":
                df_f = df_f[df_f["Estado"] == filtro_est]

            st.dataframe(df_f.drop(columns=["Archivo"]), use_container_width=True)

            # Opción para reproducir audio original
            st.markdown("### 🎧 Reproductor de Audio Original")
            id_sel = st.selectbox("Selecciona ID de registro para escuchar audio", [None] + list(df_f["ID"]))
            if id_sel:
                row = df[df["ID"] == id_sel].iloc[0]
                ruta_audio = row["Archivo"]
                if os.path.exists(ruta_audio):
                    st.audio(ruta_audio)
                else:
                    st.warning("El archivo de audio original ya no se encuentra disponible en disco.")

if __name__ == "__main__":
    main()