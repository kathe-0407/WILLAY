def get_recommendations(tipo_evento: str) -> dict:
    """
    Retorna un diccionario con las acciones recomendadas dependiendo del tipo de evento.
    Cumple con el contrato esperado para GET /recommendation/{tipo}.
    """
    tipo_upper = tipo_evento.upper()
    
    # Estructura base
    response = {
        "titulo": "Acciones recomendadas",
        "acciones": []
    }
    
    # Lógica de reglas de negocio
    if tipo_upper == "HELADA":
        response["acciones"] = [
            "Cubrir cultivos y proteger sistemas de riego",
            "Resguardar ganado en cobertizos",
            "Informar a la comunidad local",
            "Preparar suministros de emergencia"
        ]
    elif tipo_upper == "FRIAJE":
        response["acciones"] = [
            "Asegurar techos, puertas y ventanas",
            "Tener ropa de abrigo a disposición",
            "Proteger a población vulnerable (niños y ancianos)",
            "Evitar exposición prolongada a corrientes de aire frío"
        ]
    else:
        # Caso por defecto si se envía un evento desconocido
        response["titulo"] = "Recomendaciones preventivas generales"
        response["acciones"] = [
            "Mantenerse atento a los avisos oficiales del SENAMHI",
            "Coordinar con autoridades locales de Defensa Civil"
        ]
        
    return response
