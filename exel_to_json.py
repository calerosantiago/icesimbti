import json
import os
from datetime import datetime

import numpy as np
import pandas as pd

# ============================================================
# CONFIG
# ============================================================

EXCEL_PATH = "input.xlsx"
REFERENCE_JSON_PATH = "input_reference.json"

OUTPUT_DIR = "input"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# LOAD MBTI QUESTION REFERENCE
# ============================================================

with open(REFERENCE_JSON_PATH, "r", encoding="utf-8") as f:
    reference_data = json.load(f)

reference_questions = reference_data["questionnaire"]["questions"]

english_question_to_info = {
    q["text"]: {
        "id": q["id"],
        "dimension": q["dimension"]
    }
    for q in reference_questions
}

# ============================================================
# QUESTION MAPPING
# ============================================================

spanish_to_english_question_mapping = {
    "Haces nuevos amigos con regularidad.": "You regularly make new friends.",
    "Te sientes cómodo acercándote a alguien que te parece interesante para iniciar una conversación.": "You feel comfortable just walking up to someone you find interesting and striking up a conversation.",
    "En eventos sociales, rara vez intentas presentarte a personas nuevas; prefieres hablar con quienes ya conoces.": "At social events, you rarely try to introduce yourself to new people and mostly talk to the ones you already know.",
    "Prefieres trabajar solo en lugar de hacerlo en equipo.": "You prefer to work alone rather than in a team.",
    "Disfrutas participar en actividades grupales.": "You enjoy participating in group activities.",
    "Te resulta fácil mantener la calma y la concentración incluso bajo presión.": "You find it easy to stay relaxed and focused even when there is some pressure.",
    "Te sientes con más energía cuando estás rodeado de otras personas.": "You are energized by being around other people.",
    "Prefieres tener unos pocos amigos cercanos en lugar de muchos conocidos.": "You prefer to have a few close friends rather than many acquaintances.",
    "Disfrutas ser el centro de atención.": "You enjoy being the center of attention.",
    "Necesitas tiempo a solas para recargar energías después de actividades sociales.": "You need quiet time to recharge after social activities.",
    "Te sientes cómodo siendo espontáneo en situaciones sociales.": "You feel comfortable being spontaneous in social situations.",
    "Prefieres la comunicación escrita sobre la verbal.": "You prefer written communication over verbal communication.",
    "Disfrutas de los eventos de networking y de conocer gente nueva.": "You enjoy networking events and meeting new people.",
    "Prefieres pensar bien las cosas antes de hablar.": "You prefer to think things through before speaking.",
    "Te sientes entusiasmado después de asistir a fiestas o reuniones sociales.": "You feel energized after attending parties or social gatherings.",
    "No te interesa mucho discutir diversas interpretaciones o análisis de obras creativas.": "You are not too interested in discussing various interpretations and analyses of creative works.",
    "Prefieres información práctica y concreta sobre teorías abstractas.": "You prefer practical, concrete information over abstract theories.",
    "Pasas mucho de tu tiempo libre explorando temas aleatorios que despiertan tu curiosidad.": "You spend a lot of your free time exploring various random topics that pique your interest.",
    "Te gustan los libros y películas que te permiten crear tu propia interpretación del final.": "You like books and movies that make you come up with your own interpretation of the ending.",
    "Disfrutas explorando nuevas ideas y posibilidades.": "You enjoy exploring new ideas and possibilities.",
    "Te enfocas en el 'aquí y ahora' en lugar de en las posibilidades del futuro.": "You focus on the here-and-now rather than possibilities for the future.",
    "Te interesa más lo que podría ser que lo que realmente es.": "You are more interested in what could be than what is.",
    "Prefieres trabajar con métodos establecidos en lugar de experimentar con enfoques nuevos.": "You prefer to work with established methods rather than experiment with new approaches.",
    "A menudo te pierdes tanto en tus pensamientos que ignoras o olvidas lo que te rodea.": "You often get so lost in thoughts that you ignore or forget your surroundings.",
    "Confías más en la experiencia que en la teoría.": "You trust experience more than theory.",
    "Te interesa más el panorama general que los detalles específicos.": "You are more interested in the big picture than the details.",
    "Prefieres ejemplos concretos sobre conceptos abstractos.": "You prefer concrete examples over abstract concepts.",
    "Disfrutas de las lluvias de ideas y de generar conceptos nuevos.": "You enjoy brainstorming and generating new ideas.",
    "Te enfocas en hechos y detalles en lugar de en interpretaciones.": "You focus on facts and details rather than interpretations.",
    "Te sientes atraído por discusiones teóricas y filosóficas.": "You are drawn to theoretical and philosophical discussions.",
    "Sueles mantener la calma, incluso bajo mucha presión.": "You usually stay calm, even under a lot of pressure.",
    "Eres más propenso a seguir a tu cabeza que a tu corazón.": "You are more inclined to follow your head than your heart.",
    "Ver a otras personas llorar puede hacer que tú también sientas ganas de llorar.": "Seeing other people cry can easily make you feel like you want to cry too.",
    "Eres una persona muy sentimental.": "You are very sentimental.",
    "Tu felicidad proviene más de ayudar a otros a lograr cosas que de tus propios logros.": "Your happiness comes more from helping others accomplish things than your own accomplishments.",
    "Te consideras más práctico que creativo.": "You consider yourself more practical than creative.",
    "Te resulta fácil empatizar con alguien cuyas experiencias son muy diferentes a las tuyas.": "You find it easy to empathize with a person whose experiences are very different from yours.",
    "Crees que las opiniones de todos deben respetarse, sin importar si están respaldadas por hechos o no.": "You think that everyone's views should be respected regardless of whether they are supported by facts or not.",
    "Te sientes más atraído por lugares concurridos y bulliciosos que por sitios tranquilos e íntimos.": "You feel more drawn to places with busy, bustling atmospheres than quiet, intimate places.",
    "Te preocupa más la verdad que los sentimientos de los demás.": "You are more concerned with truth than with people's feelings.",
    "Tomas decisiones basadas en la lógica más que en las emociones.": "You make decisions based on logic rather than feelings.",
    "Eres sensible a las emociones de los demás.": "You are sensitive to the emotions of others.",
    "Valoras la armonía y la cooperación por encima de la competencia.": "You value harmony and cooperation over competition.",
    "Prefieres el análisis objetivo sobre las consideraciones personales.": "You prefer objective analysis over personal considerations.",
    "Consideras importante mantener las relaciones personales incluso cuando es inconveniente.": "You find it important to maintain personal relationships even when it's inconvenient.",
    "A menudo haces un plan de respaldo para tu plan de respaldo.": "You often make a backup plan for a backup plan.",
    "Prefieres terminar por completo un proyecto antes de comenzar otro.": "You prefer to completely finish one project before starting another.",
    "Te gusta usar herramientas de organización como agendas y listas.": "You like to use organizing tools like schedules and lists.",
    "Sueles preferir hacer lo que sientes en cada momento en lugar de planificar una rutina diaria.": "You usually prefer just doing what you feel like at any given moment instead of planning a particular daily routine.",
    "Te interesan tantas cosas que te resulta difícil elegir qué probar después.": "You are interested in so many things that you find it difficult to choose what to try next.",
    "Prefieres improvisar en lugar de dedicar tiempo a crear un plan detallado.": "You prefer to improvise rather than spend time coming up with a detailed plan.",
    "Consideras que las fechas límite son estresantes.": "You find deadlines stressful.",
    "Prefieres tener todo planeado con antelación.": "You prefer to have everything planned out in advance.",
    "Disfrutas tener una rutina clara en tu vida diaria.": "You enjoy having a clear routine in your daily life.",
    "A menudo dejas las cosas para el último minuto.": "You often leave things to the last minute.",
    "Te gusta mantener tus opciones abiertas en lugar de comprometerte con un plan rígido.": "You like to keep your options open rather than commit to a plan.",
    "Prefieres la estructura y la organización en tu entorno de trabajo.": "You prefer structure and organization in your work environment.",
    "Disfrutas explorando diferentes posibilidades antes de tomar una decisión.": "You enjoy exploring different possibilities before making a decision.",
    "Te sientes satisfecho cuando completas tus tareas antes de lo previsto.": "You feel satisfied when you complete tasks ahead of schedule.",
    "Te adaptas fácilmente a cambios inesperados en los planes.": "You adapt easily to unexpected changes in plans."
}

# ============================================================
# DEMOGRAPHIC CONFIG
# ============================================================

DEMOGRAPHIC_COLUMNS = [
    ("Correo", "por favor escribe tu correo electrónico"),
    ("Edad", "¿cuál es tu edad?"),
    ("Género", "¿cuál es tu género?"),
    ("Carrera", "¿qué carrera estás cursando?"),
    ("Semestre", "¿en qué semestre te encuentras"),
    ("¿Carrera fue primera opción?", "¿tu carrera fue tu primera opción?"),
    ("Seguridad en elección de carrera", "¿qué tan seguro(a) estás de tu elección"),
    ("Factores que influyeron en la elección", "¿qué factores influyeron más en tu elección"),
    ("Horas de estudio semanales", "¿cuántas horas estudias a la semana"),
    ("Satisfacción con desempeño académico", "¿qué tan satisfecho(a) estás con tu desempeño académico"),
    ("Nivel de motivación", "¿cómo calificarías tu nivel de motivación hacia tus estudios"),
    ("Buen rendimiento académico", "¿consideras que tienes buen rendimiento académico"),
    ("Nivel de estrés académico", "¿qué nivel de estrés académico experimentas normalmente"),
    ("Manejo de carga académica", "¿sientes que puedes manejar adecuadamente la carga académica"),
    ("Cómodo trabajando en equipo", "¿qué tan cómodo(a) te sientes trabajando en equipo"),
    ("Rol en trabajos grupales", "¿qué rol sueles asumir en trabajos grupales"),
    ("Expresar ideas en público", "¿qué tan fácil te resulta expresar tus ideas en público"),
    ("¿Personalidad encaja con la carrera?", "¿sientes que tu personalidad encaja"),
    ("¿Ha considerado cambiar de carrera?", "¿has considerado cambiar de carrera?"),
    ("Éxito percibido en la carrera", "¿qué tan exitoso(a) te consideras"),
    ("Influencia personalidad en rendimiento", "¿crees que tu forma de ser influye en tu rendimiento académico"),
    ("Comentarios libres", "expresa libremente lo que quieras respecto a tu forma de ser y el rendimiento academico"),
]

# ============================================================
# HELPERS
# ============================================================

def resolve_column(df, needle):
    needle = needle.lower()
    for col in df.columns:
        if needle in str(col).lower():
            return col
    return None


def build_demographics_dict(row, df, participant_number):
    result = {"participant_number": participant_number}

    for label, needle in DEMOGRAPHIC_COLUMNS:
        col = resolve_column(df, needle)

        if col is None:
            continue

        value = row[col]

        if pd.isna(value):
            continue

        result[label] = value

    return result

class NumpyEncoder(json.JSONEncoder):

    def default(self, obj):

        if isinstance(obj, np.integer):
            return int(obj)

        if isinstance(obj, np.floating):
            return float(obj)

        if isinstance(obj, np.bool_):
            return bool(obj)

        if isinstance(obj, np.ndarray):
            return obj.tolist()

        return super().default(obj)

def main():

    df = pd.read_excel(EXCEL_PATH)

    print(f"Processing {len(df)} participants...")

    for idx, row in df.iterrows():

        participant_number = idx + 1

        responses = {}

        for spanish_q, english_q in \
                spanish_to_english_question_mapping.items():

            if spanish_q not in row:
                continue

            if english_q not in english_question_to_info:
                continue

            try:
                value = int(row[spanish_q])

            except Exception:
                continue

            qid = english_question_to_info[
                english_q
            ]["id"]

            responses[str(qid)] = value

        if not responses:
            print(
                f"[skip] participant {participant_number}: "
                f"no MBTI responses"
            )
            continue

        demographics = build_demographics_dict(
            row,
            df,
            participant_number
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        json_output = os.path.join(
            OUTPUT_DIR,
            f"participant_{participant_number}.json"
        )

        with open(
            json_output,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                {
                    "questionnaire": {
                        "questions": reference_questions,
                        "responses": responses
                    },
                    "demographics": demographics,
                    "metadata": {
                        "version": "1.0",
                        "created_at": datetime.now().isoformat(),
                        "completed": True
                    }
                },
                f,
                indent=2,
                ensure_ascii=False,
                cls=NumpyEncoder
            )

        print(
            f"[ok] Participant "
            f"{participant_number}"
        )

    print("\nDone.")

if __name__ == "__main__":
    main()
