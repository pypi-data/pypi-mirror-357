# EPA Syllabifier

Módulo Python para la silabificación de palabras.

## Uso

```python
>>> from epa_syllabifier import syllabify
>>> syllabify("arcançía")
['ar', 'can', 'çía']
```

## Desarrollo

### Instalación para desarrollo

Para contribuir al proyecto, primero clona el repositorio y luego instala las dependencias de desarrollo:

```bash
git clone https://github.com/andalugeeks/epa-syllabifier.git
cd epa-syllabifier

# Configuración completa de desarrollo (crea venv e instala dependencias)
make dev-setup

# Ver comando para activar el entorno virtual
make activate
```

### Ejecución de tests

Para ejecutar los tests:

```bash
# Ejecutar todos los tests
make test

# Ejecutar tests con cobertura
make test-coverage

# Ejecutar tests con salida detallada
make test-verbose

# Ejecutar tests
make quick-test
```

### Comandos útiles de desarrollo

```bash
# Ver todos los comandos disponibles
make help

# Formatear código con Black
make format

# Verificar formato del código
make lint

# Construir el paquete
make build

# Limpiar archivos temporales
make clean

# Configuración completa: limpieza + instalación + tests
make all
```

## Requisitos

- Python >= 3.8

## Licencia

Este proyecto está licenciado bajo la Licencia GPL v3 - ver el archivo [LICENSE](LICENSE) para más detalles. 