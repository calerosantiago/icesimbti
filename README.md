# Influencia del Tipo de Personalidad (MBTI) en la Elección de Carrera y Rendimiento Académico
### Universidad Icesi · Curso de Estadística

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
├── generate_conclusion.py    # enerador del reporte de investigación Icesi
├── exel_to_json.py           # Conversión de datos Excel → JSON
├── questions.txt             # Banco de preguntas MBTI
├── requirements.txt          # Dependencias Python
├── reports/                  # JSONs individuales por participante (input)
├── conclusions/              # Reporte HTML generado (output)
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

## Flujo de Datos

```
Participante
     │
     ▼
app.py / pf_cli.py          ← cuestionario MBTI (60 preguntas)
     │
     ▼
reports/                    ← JSON por participante
mbti_questionnaire_<TIPO>_participant_<N>_<TIMESTAMP>.json
     │
     ▼
generate_conclusion.py      ← lee todos los JSONs de reports/
     │
     ▼
conclusions/
reporte_mbti_icesi.html     ← reporte académico completo
```

---

## Reporte de Investigación (`generate_conclusion.py`)

Script principal del proyecto estadístico. Lee los JSONs de `./reports` y genera un reporte HTML académico alineado con los objetivos del curso.

### Ejecutar

```bash
python generate_conclusion.py
# Salida: ./conclusions/reporte_mbti_icesi.html
```

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
| **Tabla de contingencia** | Facultad × Tipo MBTI (frecuencias) |
| **Probabilidad condicional** | P(Facultad \| Tipo MBTI) en porcentaje |
| Conclusiones | 6 hallazgos basados en los objetivos del proyecto |
| Limitaciones | Consideraciones metodológicas |
| Referencias | UNEA 2026, UNITEC 2026, Jung, Myers & Myers |

### Estructura del JSON esperado en `reports/`

```json
{
  "questionnaire": {
    "responses": { "1": 4, "2": 3, ... },
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
    "dimension_scores": { ... },
    "confidence_scores": { ... }
  },
  "demographics": { ... }
}
```

### Clasificación por Facultades (Universidad Icesi)

El script asigna automáticamente cada carrera a su facultad:

| Facultad | Ejemplos de carreras |
|----------|----------------------|
| Ciencias Administrativas y Económicas | Administración, Economía, Finanzas, Negocios Internacionales |
| Ingenierías, Diseño y Tecnologías | Ing. de Sistemas, Ing. Industrial, Diseño Industrial |
| Derecho, Ciencias Humanas y Sociales | Derecho, Psicología, Comunicación Social, Música |
| Ciencias Naturales y de la Salud | Medicina, Biología, Enfermería, Química |

---

## Interfaz Web (`app.py`)

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="tu-api-key"
python app.py
# Abre http://127.0.0.1:7860
```

Funcionalidades:
- Cuestionario de 20/40/60 preguntas con guardado automático
- Análisis con LLM (Gemini) con referencias a preguntas específicas
- Exportación del JSON al directorio `reports/`
- Generación de reporte HTML individual por participante

---

## CLI (`pf_cli.py`)

```bash
# Cuestionario interactivo
python pf_cli.py

# Con datos de prueba (útil para desarrollo)
python pf_cli.py --test --test-type ENFJ

# Retomar cuestionario guardado
python pf_cli.py --import-file reports/mbti_questionnaire_ENFJ_participant_70_*.json
```

---

## Servidor MCP (`server.py`)

Permite que modelos de lenguaje tomen el test MBTI vía Model Context Protocol.

```bash
python server.py
```

Ver `MCP_README.md` para detalles de integración.

---

## Análisis Estadístico del Proyecto

El proyecto aplica las siguientes técnicas del curso:

| Técnica | Aplicación |
|---------|------------|
| Medidas de tendencia central | Media de indicadores Likert por tipo MBTI |
| Medidas de dispersión | Desviación estándar de autopercepción académica |
| Distribuciones de frecuencia | Frecuencia absoluta y relativa de tipos MBTI |
| Probabilidad empírica | P(MBTI \| Carrera), P(Facultad \| Tipo MBTI) |
| Tablas de contingencia | Cruce Facultad × Tipo MBTI |
| Gráficos | Barras, sectores, histogramas, barras con error |

---

## Dependencias

```bash
pip install -r requirements.txt
```

Principales:
- `gradio>=4.0.0` — interfaz web
- `google-genai>=0.3.0` — análisis LLM
- `matplotlib` — generación de gráficas
- `beautifulsoup4` — parsing HTML
- `markdown` — generación de reportes

---

## Muestra

- **n = 70 estudiantes** de pregrado, Universidad Icesi
- **Muestreo:** Aleatorio Simple (MAS), α = 0.05, p = q = 0.5
- **Instrumento:** MBTI de 60 preguntas vía [mbti-pocketflow](https://huggingface.co/spaces/Fancellu/mbti-pocketflow)
- **Periodo de recolección:** Mayo 2026

---

## Referencias

- UNEA (2026). *Test de personalidad y elección de carrera.* https://www.unea.edu.mx/blog/test-personalidad-y-carrera
- UNITEC (2026). *¿Qué carrera estudiar según tu personalidad?* https://blogs.unitec.mx/que-carrera-estudiar-segun-tu-personalidad
- Myers, I. B., & Myers, P. B. (1995). *Gifts Differing.* Davies-Black Publishing.
- Jung, C. G. (1971). *Psychological Types.* Princeton University Press.

---

*Proyecto de estadística descriptiva · Universidad Icesi · 2026*
