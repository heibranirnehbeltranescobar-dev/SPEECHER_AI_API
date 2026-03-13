from google.genai import types

# Defines the schema for ISO/IEC 25010 queries
iso_skill_declaration = types.FunctionDeclaration(
    name="get_quality_standard",
    description="Consulta las definiciones oficiales de los pilares de calidad de software. Úsalo si el estudiante pregunta sobre usabilidad, seguridad o mantenimiento de código.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "pillar": types.Schema(
                type=types.Type.STRING,
                description="El pilar de calidad a consultar (ej. 'mantenibilidad', 'usabilidad', 'seguridad', 'eficiencia')."
            )
        },
        required=["pillar"]
    )
)