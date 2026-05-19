# 🏋️ Halterofilia — Calculadora de pesos de entrenamiento

App web para halterófilos que calcula los kilos exactos de cada serie a partir del PDF semanal del entrenador.

## ¿Qué hace?

1. **Sube el PDF** de tu entrenador (arrastra y suelta o selecciona el fichero)
2. **Introduce tus máximos** (Arrancada, Dos Tiempos, Jerk, Sentadillas)
3. La app **calcula automáticamente** el peso de cada serie y bloque de repeticiones
4. Cada ejercicio incluye un enlace directo a **YouTube** para ver la técnica

### Características

- Soporta el formato real de planes de halterofilia: nombre del ejercicio en una línea, series en líneas separadas o inline
- Maneja **rangos de porcentaje** (`80-90%` → muestra `72–81 kg`)
- Ejercicios sin porcentaje (peso moderado, subiendo carga) se muestran sin error
- Si no introduces tu RM de Sentadilla Trasera, calcula automáticamente la base como **120% del C&J** (convención habitual en halterofilia)
- Reconoce más de 25 variantes de Arrancada, Dos Tiempos, Jerk y Sentadilla

## Instalación

```bash
git clone https://github.com/Davidbg90/Halterofilia.git
cd Halterofilia
pip install -r requirements.txt
python3 app.py
```

Abre el navegador en **http://127.0.0.1:5000**

## Formato del plan que reconoce

```
DIA 1
A) Snatch
1x3 70%
3x1 80%
NOTAS: usar correas

B) Back squat 5x4 75-80%
NOTAS: porcentajes sobre el 120% del C&J

DIA 2
A) Hang clean + Clean + Split jerk
2x1 75%
2x1 80%
```

## Stack

- **Backend:** Python 3 + Flask
- **Extracción de PDF:** pdfplumber
- **Frontend:** HTML/CSS/JS vanilla (sin frameworks)
