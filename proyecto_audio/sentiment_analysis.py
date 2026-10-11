def analizar_sentimiento(texto):
    """
    Analiza la transcripción del audio mediante reglas léxicas en español.
    Clasifica en Positivo, Negativo o Neutral y emite una explicación analítica.
    """
    if not texto:
        return "Neutral", "Transcripción vacía o no disponible para análisis."

    texto_lower = texto.lower()

    palabras_positivas = [
        "encantó", "perfecto", "excelente", "maravilloso", "recomiendo", 
        "feliz", "bueno", "calidad", "rápido", "agradable", "satisfecho", "funciona perfectamente"
    ]
    palabras_negativas = [
        "mala", "malo", "pésimo", "horrible", "falló", "roto", "decepcionó", 
        "tardó", "problema", "defecto", "inútil", "queja", "no funciona", "muy mala"
    ]

    score_positivo = sum(1 for p in palabras_positivas if p in texto_lower)
    score_negativo = sum(1 for p in palabras_negativas if p in texto_lower)

    if score_positivo > score_negativo:
        sentimiento = "Positivo"
        analisis = f"El audio expresa satisfacción con el producto ({score_positivo} indicadores positivos detectados)."
    elif score_negativo > score_positivo:
        sentimiento = "Negativo"
        analisis = f"El audio reporta fallas, insatisfacción o desaprobación ({score_negativo} indicadores negativos detectados)."
    else:
        if score_positivo == 0 and score_negativo == 0:
            sentimiento = "Neutral"
            analisis = "Opinión descriptiva o neutral sin carga emocional marcada."
        else:
            sentimiento = "Neutral"
            analisis = "Opinión mixta o equilibrada con argumentos a favor y en contra."

    return sentimiento, analisis