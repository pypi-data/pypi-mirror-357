# EPA Syllabicate

Módulo Python para la silabificación de palabras.

## Uso

```python
from epa_syllabicate import syllabicate

# Ejemplo de uso
word = "ehemplo"
silabes = syllabicate(word)
print(silabas)  # ['e', 'hem', 'plo']
```

## Desarrollo

### Instalación para desarrollo

Para contribuir al proyecto, primero clona el repositorio y luego instala las dependencias de desarrollo:

```bash
git clone https://github.com/tu-usuario/epa-syllabicate.git
cd epa-syllabicate
python -m env .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

### Ejecución de tests

Para ejecutar los tests:

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests con cobertura
pytest --cov=epa_syllabicate
```

## Requisitos

- Python >= 3.8

## Licencia

Este proyecto está licenciado bajo la Licencia GPL v3 - ver el archivo [LICENSE](LICENSE) para más detalles. 