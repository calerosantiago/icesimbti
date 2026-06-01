# Influencia del Tipo de Personalidad (MBTI) en la Elección de Carrera y Rendimiento Académico
### Universidad Icesi · Curso de Estadística – Semana 16

Aplicación para la recolección, procesamiento y análisis estadístico de perfiles de personalidad MBTI en estudiantes universitarios. Genera un reporte HTML académico con estadística descriptiva, tablas de contingencia y probabilidad condicional empírica P(Facultad | Tipo MBTI).

---

## Pregunta de Investigación

> ¿En qué medida el tipo de personalidad (MBTI) se relaciona con la elección de carrera y el rendimiento académico en los estudiantes de la Universidad Icesi?

---

## Estructura del Proyecto

```
icesimbti/
├── app.py                    # Interfaz web Gradio (cuestionario interactivo)
├── server.py                 # Servidor FastMCP para que LLMs tomen el test
├── pf_cli.py                 # CLI con arquitectura PocketFlow
├── flow.py                   # Definición del pipeline PocketFlow
├── nodes.py                  # Nodos PocketFlow (carga, análisis, exportación)
├── generate_conclusion.py    # ⭐ Generador del reporte de investigación Icesi
├── exel_to_json.py           # Conversión Excel → JSONs individuales en input/
├── questions.txt             # Banco de preguntas MBTI
├── requirements.txt          # Dependencias Python
├── input/                    # JSONs crudos por participante (salida de exel_to_json.py)
│   └── participant_1.json … participant_70.json
├── reports/                  # JSONs procesados con tipo MBTI calculado (salida de pf_cli.py)
│   └── mbti_questionnaire_<TIPO>_participant_<N>_<TIMESTAMP>.json
├── conclusions/              # Reporte HTML final (salida de generate_conclusion.py)
│   └── reporte_mbti_icesi.html
├── docs/
│   └── Propuesta del proyecto(Estadistica) semana 16.docx
├── utils/
│   ├── mbti_scoring.py       # Algoritmo de puntuación MBTI tradicional
│   ├── questionnaire.py      # Sets de preguntas (20/40/60) y serialización
│   ├── call_llm.py           # Integración LLM (Gemini)
│   ├── report_generator.py   # Generación de reportes HTML individuales
│   └── test_data.py          # Datos de prueba por tipo MBTI
└── input_reference.json      # JSON de referencia / ejemplo de estructura
```

---

## Pipeline Completo (uso real)

El proyecto se ejecuta en tres pasos secuenciales:

### Paso 1 — Convertir Excel a JSON

Convierte `input.xlsx` (respuestas recolectadas) en un JSON por participante dentro de `input/`.

```bash
python3 exel_to_json.py
# Requiere: input.xlsx en la raíz del proyecto
# Salida:   input/participant_1.json … input/participant_70.json
```

```
Processing 70 participants...
[ok] Participant 1
...
[ok] Participant 70
Done.
```

### Paso 2 — Calcular tipo MBTI con PocketFlow

Procesa todos los JSONs de `input/`, calcula el tipo MBTI por puntuación tradicional y exporta los resultados a `reports/`.

```bash
python3 pf_cli.py --import-file input/*
# Salida: reports/mbti_questionnaire_<TIPO>_participant_<N>_<TIMESTAMP>.json
#         reports/mbti_report_<TIPO>_participant_<N>_<TIMESTAMP>.html  (reporte individual)
```

Ejemplo de salida por participante:
```
Processing: input/participant_1.json
Running PocketFlow pipeline (Traditional MBTI only)...
==================================================
MBTI Type: ENFJ
Report: reports/mbti_report_ENFJ_participant_1_20260601_000628.html
Export: mbti_questionnaire_ENFJ_participant_1_20260601_000628.json
Dimension Scores:
  E/I: E (57.9%)
  S/N: N (60.0%)
  T/F: F (52.6%)
  J/P: J (65.0%)
Demographics included in export.
```

### Paso 3 — Generar reporte de investigación

Lee todos los JSONs de `reports/` y produce el reporte académico HTML completo.

```bash
python3 generate_conclusion.py
# Salida: ./conclusions/reporte_mbti_icesi.html
```

```
=== Generando Reporte MBTI – Universidad Icesi ===

Datos extraídos de 70 participantes.
Tipos MBTI encontrados (8):
  ENFJ: 43 (61.4%)
  INFJ: 12 (17.1%)
  ENFP: 4 (5.7%)
  ENTJ: 3 (4.3%)
  ESFJ: 3 (4.3%)
  INFP: 2 (2.9%)
  INTJ: 2 (2.9%)
  ISFJ: 1 (1.4%)
Generando gráficas...
Gráficas generadas correctamente.
✓ Listo. Reporte guardado en: ./conclusions/reporte_mbti_icesi.html
```

> **Nota:** Matplotlib 3.7+ emite un `DeprecationWarning` por el uso de `plt.cm.get_cmap()`.
> No afecta la ejecución. Para silenciarlo: `python3 -W ignore generate_conclusion.py`

---

## Flujo de Datos

```
input.xlsx
     │
     ▼  python3 exel_to_json.py
input/
participant_1.json … participant_70.json
     │
     ▼  python3 pf_cli.py --import-file input/*
reports/
mbti_questionnaire_<TIPO>_participant_<N>_<TIMESTAMP>.json
     │
     ▼  python3 generate_conclusion.py
conclusions/
reporte_mbti_icesi.html
```

---

## Reporte de Investigación (`generate_conclusion.py`)

Lee `./reports/*.json` y genera un HTML académico alineado con los objetivos del proyecto.

### Contenido del reporte

| Sección | Descripción |
|---------|-------------|
| Definición del problema | Pregunta de investigación y delimitación |
| Objetivos | General y específicos del proyecto |
| Marco teórico | Teoría Jung/Myers-Briggs, congruencia vocacional |
| Metodología | MAS, n=70, nivel de confianza 95% |
| Caracterización de la muestra | Edad, género, semestre, carrera, facultad |
| Distribución de tipos MBTI | Frecuencias absolutas y relativas, gráfica de barras |
| Análisis dimensional | E/I, N/S, F/T, J/P con gráficas |
| Indicadores académicos | Escala Likert 1–5 con media y desviación estándar |
| **Tabla de contingencia** | Facultad × Tipo MBTI (frecuencias absolutas) |
| **Probabilidad condicional** | P(Facultad \| Tipo MBTI) en porcentaje |
| Conclusiones | 6 hallazgos basados en los objetivos del proyecto |
| Limitaciones | Consideraciones metodológicas |
| Referencias | UNEA 2026, UNITEC 2026, Jung, Myers & Myers |

### Resultados observados (n = 70, Mayo 2026)

| Tipo MBTI | n | % |
|-----------|---|---|
| ENFJ | 43 | 61.4% |
| INFJ | 12 | 17.1% |
| ENFP | 4 | 5.7% |
| ENTJ | 3 | 4.3% |
| ESFJ | 3 | 4.3% |
| INFP | 2 | 2.9% |
| INTJ | 2 | 2.9% |
| ISFJ | 1 | 1.4% |

### Clasificación automática por Facultades (Universidad Icesi)

| Facultad | Ejemplos de carreras |
|----------|----------------------|
| Ciencias Administrativas y Económicas | Administración, Economía, Finanzas, Negocios Internacionales |
| Ingenierías, Diseño y Tecnologías | Ing. de Sistemas, Ing. Industrial, Diseño Industrial |
| Derecho, Ciencias Humanas y Sociales | Derecho, Psicología, Comunicación Social, Música |
| Ciencias Naturales y de la Salud | Medicina, Biología, Enfermería, Química |

### Estructura del JSON esperado en `reports/`

```json
{
  "questionnaire": {
    "responses": { "1": 4, "2": 3 },
    "demographics": {
      "participant_number": 70,
      "Edad": 17,
      "Género": "Masculino",
      "Carrera": "Música",
      "Semestre": 4,
      "¿Carrera fue primera opción?": "No",
      "Seguridad en elección de carrera": 5,
      "¿Personalidad encaja con la carrera?": 4,
      "Éxito percibido en la carrera": 4,
      "Satisfacción con desempeño académico": 3,
      "Nivel de motivación": 4,
      "Nivel de estrés académico": 3,
      "Manejo de carga académica": 4,
      "Horas de estudio semanales": 6,
      "Rol en trabajos grupales": "Organizador",
      "Expresar ideas en público": 4,
      "Influencia personalidad en rendimiento": 5
    }
  },
  "results": {
    "mbti_type": "ENFJ",
    "dimension_scores": { "E_score": 0.53, "N_score": 0.76, "F_score": 0.65, "J_score": 0.63 },
    "confidence_scores": { "EI_confidence": 0.06, "SN_confidence": 0.53 }
  },
  "demographics": { }
}
```

---

## Otros modos de uso

### Interfaz Web (`app.py`)

Para recolección interactiva (un participante a la vez):

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="tu-api-key"
python3 app.py
# Abre http://127.0.0.1:7860
```

- Cuestionario de 20/40/60 preguntas con guardado automático
- Análisis con LLM (Gemini) con referencias a preguntas específicas
- Exporta JSON directamente a `reports/`

### CLI individual

```bash
# Cuestionario interactivo
python3 pf_cli.py

# Con datos de prueba
python3 pf_cli.py --test --test-type ENFJ

# Un archivo específico
python3 pf_cli.py --import-file input/participant_70.json
```

### Servidor MCP (`server.py`)

Permite que LLMs tomen el test MBTI vía Model Context Protocol.

```bash
python3 server.py
```

Ver `MCP_README.md` para detalles de integración.

---

## Análisis Estadístico Aplicado

| Técnica | Aplicación en el proyecto |
|---------|--------------------------|
| Medidas de tendencia central | Media de indicadores Likert por tipo MBTI |
| Medidas de dispersión | Desviación estándar de autopercepción académica |
| Distribuciones de frecuencia | Frecuencia absoluta y relativa de los 8 tipos encontrados |
| Probabilidad empírica | P(Facultad \| Tipo MBTI) via tabla de contingencia |
| Tablas de contingencia | Cruce Facultad × Tipo MBTI (4 facultades × 8 tipos) |
| Gráficos | Barras, sectores, histogramas, barras de error (±1σ) |

---

## Dependencias

```bash
pip install -r requirements.txt
```

Principales: `gradio>=4.0.0`, `google-genai>=0.3.0`, `matplotlib`, `beautifulsoup4`, `markdown`

---

## Muestra

- **n = 70 estudiantes** de pregrado, Universidad Icesi
- **Muestreo:** Aleatorio Simple (MAS), α = 0.05, p = q = 0.5
- **Instrumento:** MBTI de 60 preguntas vía [mbti-pocketflow](https://huggingface.co/spaces/Fancellu/mbti-pocketflow)
- **Periodo:** Mayo 2026

---

## Referencias

- UNEA (2026). *Test de personalidad y elección de carrera.* https://www.unea.edu.mx/blog/test-personalidad-y-carrera
- UNITEC (2026). *¿Qué carrera estudiar según tu personalidad?* https://blogs.unitec.mx/que-carrera-estudiar-segun-tu-personalidad
- Myers, I. B., & Myers, P. B. (1995). *Gifts Differing.* Davies-Black Publishing.
- Jung, C. G. (1971). *Psychological Types.* Princeton University Press.

---

*Proyecto de estadística descriptiva · Universidad Icesi · 2026*
