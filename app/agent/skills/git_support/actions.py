
def get_git_guide(concept: str) -> str:
    # Static dictionary simulating a database query
    official_guide = {
        "commit": "Un commit guarda los cambios en tu repositorio local. Regla de la institución: Usa siempre mensajes descriptivos en imperativo (ej: 'feat: agregar login').",
        "merge": "Une dos ramas de desarrollo. Recuerda siempre hacer 'pull' y resolver los conflictos localmente en VS Code antes de completar el merge.",
        "pull request": "Es la petición para integrar tus cambios a la rama principal (main) en GitHub. Debe ser revisada por al menos otro compañero antes de aprobarse.",
        "clone": "Descarga un repositorio remoto a tu máquina local usando 'git clone <url>'."
    }
    
    concept_lower = concept.lower()
    for key, value in official_guide.items():
        if key in concept_lower:
            return f"Información oficial sobre '{key}': {value}"
    
    return "No se encontró información sobre ese comando en la guía estática. Pide al estudiante que especifique un comando básico."