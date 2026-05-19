# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proyecto

App web para halterófilos: el entrenador manda el plan en texto, el usuario introduce sus máximos y la app calcula los pesos por serie/repetición y enlaza vídeos de YouTube para cada ejercicio.

Idioma del código y la UI: **castellano**. Nombres de ejercicios: **inglés** (Snatch, Clean & Jerk, etc.).

## Stack

- **Backend**: Python 3 + Flask (`app.py`)
- **Frontend**: HTML/CSS/JS vanilla (sin frameworks)
- **Sin base de datos**: todo se calcula en memoria por petición

## Comandos

```bash
# Instalar dependencias
pip3 install -r requirements.txt

# Arrancar servidor de desarrollo
python3 app.py
# → http://127.0.0.1:5000
```

## Arquitectura

```
app.py            # Rutas Flask: GET /, POST /calcular, POST /subir-pdf
parser.py         # Parsea texto libre del entrenador → lista de ejercicios con pesos
calculator.py     # Mapa ejercicio→grupo de máximo, cálculo a 0.5 kg, URL de YouTube
pdf_extractor.py  # Extrae texto de PDF (pdfplumber); intenta tablas primero, luego texto libre
templates/        # index.html (plantilla Jinja, lógica JS inline)
static/           # style.css (tema oscuro, responsive)
```

### Flujo principal

1. El usuario sube un PDF arrastrándolo o con el selector de fichero.
2. El frontend hace `POST /subir-pdf` (multipart); el backend usa `pdfplumber` para extraer el texto y lo devuelve en JSON.
3. El texto extraído se vuelca en el textarea para que el usuario lo revise/corrija si el PDF tiene un formato inusual.
4. El usuario pulsa "Calcular pesos" → `POST /calcular` con los máximos y el texto.
5. `parser.py` detecta días de la semana y parsea cada línea con regex.
6. Para cada ejercicio llama a `calculator.py`, que resuelve el grupo de máximo (p.ej. "Hang Snatch" → `snatch`) y calcula `max × porcentaje / 100` redondeado a 0.5 kg.
7. La respuesta JSON se renderiza en el DOM con JS puro.

### Grupos de máximos (`calculator.py`)

| Clave        | Ejercicios que la usan                                      |
|--------------|-------------------------------------------------------------|
| `snatch`     | Snatch, Hang Snatch, Power Snatch, Snatch Pull, OHS, …      |
| `clean_jerk` | Clean & Jerk, Hang Clean, Power Clean, Clean Pull, Clean, … |
| `jerk`       | Jerk, Push Jerk, Split Jerk (si no se define, usa `clean_jerk`) |
| `back_squat` | Back Squat, Squat                                           |
| `front_squat`| Front Squat                                                 |

Para añadir variantes nuevas, editar `LIFT_GROUPS` en `calculator.py`.

### Formato del plan que acepta el parser

```
Lunes:
Snatch 5x3 @80%
Clean & Jerk 4x2+1 @85%
Back Squat 4x4 al 75%

Miércoles:
Hang Snatch 5x3 @75%
```

- Días: `Lunes`, `Martes`, … o `Day 1`, `Día 1`.
- Reps compuestas (`2+1`) se detallan bloque a bloque en la tabla de series.
- Separador de porcentaje: `@`, `a`, `al` (con o sin espacio).
