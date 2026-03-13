
def get_quality_standard(pillar: str) -> str:

    # Static data based on ISO/IEC 25010 software quality pillars
    standard = {
        "mantenibilidad": "Capacidad del software para ser modificado efectiva y eficientemente. Incluye modularidad, reusabilidad y capacidad de ser analizado.",
        "usabilidad": "Grado en que un producto puede ser utilizado por estudiantes o usuarios para lograr metas con efectividad y satisfacción.",
        "seguridad": "Grado en que el sistema protege la información y los datos para evitar accesos no autorizados.",
        "eficiencia": "Desempeño relativo a la cantidad de recursos utilizados bajo condiciones determinadas."
    }
    
    pillar_lower = pillar.lower()
    for key, value in standard.items():
        if key in pillar_lower:
            return f"Definición técnica para '{key}': {value}"
            
    return "Pilar no encontrado en la base de datos de estándares de calidad."