# Hack$U Academy Courses Library

Una biblioteca Python para consultar cursos de la academia Hack4U

## Cursos disponibles:

- Introduccion a Linux [15 horas]
- Personalizacion de Linux [3 horas]
- Introduccion al Hacking [53 horas]
- Python Ofensivo [35 horas]

## Instalacion 

Instala el paquete usando `pip3`:

```python3
pip3 instal hack4u
```
## Uso basico

### Listar todos los cursos

```pyhton
from hack4u import list_courses

for course in list_courses():
    print(course)
```

### Obtener un curso por nombre

```python
from hack4u import get_course_by_name

course = get_course_by_name("Introduccion a Linux")
print(course)
```

### Calcular duracion total de los cursos

```python3
from hack3u.utils import total_duration

print(f"Duracion total: {total_duration()} horas")
```
