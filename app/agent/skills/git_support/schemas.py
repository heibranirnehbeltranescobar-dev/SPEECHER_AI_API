from google.genai import types

git_skill_declaration = types.FunctionDeclaration(
    name="get_git_guide",
    description="Consulta la guía oficial de comandos y buenas prácticas de Git y GitHub. Úsalo cuando un estudiante pregunte sobre control de versiones.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "concept": types.Schema(
                type=types.Type.STRING,
                description="El comando o concepto de Git a consultar (ej. 'commit', 'merge', 'pull request', 'rebase')."
            )
        },
        required=["concept"]
    )
)