from google.genai import types

knowledge_skill_declaration = types.FunctionDeclaration(
    name="search_internal_knowledge",
    description=(
        "Busca información en la base de conocimientos técnicos de ingeniería. "
        "Contiene manuales de desarrollo (ej. Git), estándares de calidad, definiciones "
        "y guías de software. Úsalo SIEMPRE que el estudiante pregunte sobre cómo usar "
        "una herramienta, conceptos de programación, o necesite documentación técnica."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(
                type=types.Type.STRING,
                description="La pregunta clara y concisa a buscar en la base de datos."
            )
        },
        required=["query"]
    )
)