import json
import os
from datetime import datetime

# Question sets in multiple languages
TRANSLATIONS = {
    "en": {
        "E": "Extraversion", "I": "Introversion",
        "S": "Sensing", "N": "Intuition",
        "T": "Thinking", "F": "Feeling",
        "J": "Judging", "P": "Perceiving",
        "questions": [
            # E/I
            {"id": 1, "text": "You regularly make new friends.", "dimension": "E"},
            {"id": 2, "text": "You feel comfortable just walking up to someone you find interesting and striking up a conversation.", "dimension": "E"},
            {"id": 3, "text": "At social events, you rarely try to introduce yourself to new people and mostly talk to the ones you already know.", "dimension": "I"},
            {"id": 4, "text": "You prefer to work alone rather than in a team.", "dimension": "I"},
            {"id": 5, "text": "You enjoy participating in group activities.", "dimension": "E"},
            {"id": 21, "text": "You find it easy to stay relaxed and focused even when there is some pressure.", "dimension": "I"},
            {"id": 22, "text": "You are energized by being around other people.", "dimension": "E"},
            {"id": 23, "text": "You prefer to have a few close friends rather than many acquaintances.", "dimension": "I"},
            {"id": 24, "text": "You enjoy being the center of attention.", "dimension": "E"},
            {"id": 25, "text": "You need quiet time to recharge after social activities.", "dimension": "I"},
            {"id": 41, "text": "You feel comfortable being spontaneous in social situations.", "dimension": "E"},
            {"id": 42, "text": "You prefer written communication over verbal communication.", "dimension": "I"},
            {"id": 43, "text": "You enjoy networking events and meeting new people.", "dimension": "E"},
            {"id": 44, "text": "You prefer to think things through before speaking.", "dimension": "I"},
            {"id": 45, "text": "You feel energized after attending parties or social gatherings.", "dimension": "E"},
            
            # S/N
            {"id": 6, "text": "You are not too interested in discussing various interpretations and analyses of creative works.", "dimension": "S"},
            {"id": 7, "text": "You prefer practical, concrete information over abstract theories.", "dimension": "S"},
            {"id": 8, "text": "You spend a lot of your free time exploring various random topics that pique your interest.", "dimension": "N"},
            {"id": 9, "text": "You like books and movies that make you come up with your own interpretation of the ending.", "dimension": "N"},
            {"id": 10, "text": "You enjoy exploring new ideas and possibilities.", "dimension": "N"},
            {"id": 26, "text": "You focus on the here-and-now rather than possibilities for the future.", "dimension": "S"},
            {"id": 27, "text": "You are more interested in what could be than what is.", "dimension": "N"},
            {"id": 28, "text": "You prefer to work with established methods rather than experiment with new approaches.", "dimension": "S"},
            {"id": 29, "text": "You often get so lost in thoughts that you ignore or forget your surroundings.", "dimension": "N"},
            {"id": 30, "text": "You trust experience more than theory.", "dimension": "S"},
            {"id": 46, "text": "You are more interested in the big picture than the details.", "dimension": "N"},
            {"id": 47, "text": "You prefer concrete examples over abstract concepts.", "dimension": "S"},
            {"id": 48, "text": "You enjoy brainstorming and generating new ideas.", "dimension": "N"},
            {"id": 49, "text": "You focus on facts and details rather than interpretations.", "dimension": "S"},
            {"id": 50, "text": "You are drawn to theoretical and philosophical discussions.", "dimension": "N"},
            
            # T/F
            {"id": 11, "text": "You usually stay calm, even under a lot of pressure.", "dimension": "T"},
            {"id": 12, "text": "You are more inclined to follow your head than your heart.", "dimension": "T"},
            {"id": 13, "text": "Seeing other people cry can easily make you feel like you want to cry too.", "dimension": "F"},
            {"id": 14, "text": "You are very sentimental.", "dimension": "F"},
            {"id": 15, "text": "Your happiness comes more from helping others accomplish things than your own accomplishments.", "dimension": "F"},
            {"id": 31, "text": "You consider yourself more practical than creative.", "dimension": "T"},
            {"id": 32, "text": "You find it easy to empathize with a person whose experiences are very different from yours.", "dimension": "F"},
            {"id": 33, "text": "You think that everyone's views should be respected regardless of whether they are supported by facts or not.", "dimension": "F"},
            {"id": 34, "text": "You feel more drawn to places with busy, bustling atmospheres than quiet, intimate places.", "dimension": "T"},
            {"id": 35, "text": "You are more concerned with truth than with people's feelings.", "dimension": "T"},
            {"id": 51, "text": "You make decisions based on logic rather than feelings.", "dimension": "T"},
            {"id": 52, "text": "You are sensitive to the emotions of others.", "dimension": "F"},
            {"id": 53, "text": "You value harmony and cooperation over competition.", "dimension": "F"},
            {"id": 54, "text": "You prefer objective analysis over personal considerations.", "dimension": "T"},
            {"id": 55, "text": "You find it important to maintain personal relationships even when it's inconvenient.", "dimension": "F"},
            
            # J/P
            {"id": 16, "text": "You often make a backup plan for a backup plan.", "dimension": "J"},
            {"id": 17, "text": "You prefer to completely finish one project before starting another.", "dimension": "J"},
            {"id": 18, "text": "You like to use organizing tools like schedules and lists.", "dimension": "J"},
            {"id": 19, "text": "You usually prefer just doing what you feel like at any given moment instead of planning a particular daily routine.", "dimension": "P"},
            {"id": 20, "text": "You are interested in so many things that you find it difficult to choose what to try next.", "dimension": "P"},
            {"id": 36, "text": "You prefer to improvise rather than spend time coming up with a detailed plan.", "dimension": "P"},
            {"id": 37, "text": "You find deadlines stressful.", "dimension": "P"},
            {"id": 38, "text": "You prefer to have everything planned out in advance.", "dimension": "J"},
            {"id": 39, "text": "You enjoy having a clear routine in your daily life.", "dimension": "J"},
            {"id": 40, "text": "You often leave things to the last minute.", "dimension": "P"},
            {"id": 56, "text": "You like to keep your options open rather than commit to a plan.", "dimension": "P"},
            {"id": 57, "text": "You prefer structure and organization in your work environment.", "dimension": "J"},
            {"id": 58, "text": "You enjoy exploring different possibilities before making a decision.", "dimension": "P"},
            {"id": 59, "text": "You feel satisfied when you complete tasks ahead of schedule.", "dimension": "J"},
            {"id": 60, "text": "You adapt easily to unexpected changes in plans.", "dimension": "P"}
        ]
    },
    "es": {
        "E": "Extraversión", "I": "Introversión",
        "S": "Sensación", "N": "Intuición",
        "T": "Pensamiento", "F": "Sentimiento",
        "J": "Juicio", "P": "Percepción",
        "questions": [
            # E/I
            {"id": 1, "text": "Haces nuevos amigos con regularidad.", "dimension": "E"},
            {"id": 2, "text": "Te sientes cómodo acercándote a alguien que te parece interesante para iniciar una conversación.", "dimension": "E"},
            {"id": 3, "text": "En eventos sociales, rara vez intentas presentarte a personas nuevas; prefieres hablar con quienes ya conoces.", "dimension": "I"},
            {"id": 4, "text": "Prefieres trabajar solo en lugar de hacerlo en equipo.", "dimension": "I"},
            {"id": 5, "text": "Disfrutas participar en actividades grupales.", "dimension": "E"},
            {"id": 21, "text": "Te resulta fácil mantener la calma y la concentración incluso bajo presión.", "dimension": "I"},
            {"id": 22, "text": "Te sientes con más energía cuando estás rodeado de otras personas.", "dimension": "E"},
            {"id": 23, "text": "Prefieres tener unos pocos amigos cercanos en lugar de muchos conocidos.", "dimension": "I"},
            {"id": 24, "text": "Disfrutas ser el centro de atención.", "dimension": "E"},
            {"id": 25, "text": "Necesitas tiempo a solas para recargar energías después de actividades sociales.", "dimension": "I"},
            {"id": 41, "text": "Te sientes cómodo siendo espontáneo en situaciones sociales.", "dimension": "E"},
            {"id": 42, "text": "Prefieres la comunicación escrita sobre la verbal.", "dimension": "I"},
            {"id": 43, "text": "Disfrutas de los eventos de networking y de conocer gente nueva.", "dimension": "E"},
            {"id": 44, "text": "Prefieres pensar bien las cosas antes de hablar.", "dimension": "I"},
            {"id": 45, "text": "Te sientes entusiasmado después de asistir a fiestas o reuniones sociales.", "dimension": "E"},
            
            # S/N
            {"id": 6, "text": "No te interesa mucho discutir diversas interpretaciones o análisis de obras creativas.", "dimension": "S"},
            {"id": 7, "text": "Prefieres información práctica y concreta sobre teorías abstractas.", "dimension": "S"},
            {"id": 8, "text": "Pasas mucho de tu tiempo libre explorando temas aleatorios que despiertan tu curiosidad.", "dimension": "N"},
            {"id": 9, "text": "Te gustan los libros y películas que te permiten crear tu propia interpretación del final.", "dimension": "N"},
            {"id": 10, "text": "Disfrutas explorando nuevas ideas y posibilidades.", "dimension": "N"},
            {"id": 26, "text": "Te enfocas en el 'aquí y ahora' en lugar de en las posibilidades del futuro.", "dimension": "S"},
            {"id": 27, "text": "Te interesa más lo que podría ser que lo que realmente es.", "dimension": "N"},
            {"id": 28, "text": "Prefieres trabajar con métodos establecidos en lugar de experimentar con enfoques nuevos.", "dimension": "S"},
            {"id": 29, "text": "A menudo te pierdes tanto en tus pensamientos que ignoras o olvidas lo que te rodea.", "dimension": "N"},
            {"id": 30, "text": "Confías más en la experiencia que en la teoría.", "dimension": "S"},
            {"id": 46, "text": "Te interesa más el panorama general que los detalles específicos.", "dimension": "N"},
            {"id": 47, "text": "Prefieres ejemplos concretos sobre conceptos abstractos.", "dimension": "S"},
            {"id": 48, "text": "Disfrutas de las lluvias de ideas y de generar conceptos nuevos.", "dimension": "N"},
            {"id": 49, "text": "Te enfocas en hechos y detalles en lugar de en interpretaciones.", "dimension": "S"},
            {"id": 50, "text": "Te sientes atraído por discusiones teóricas y filosóficas.", "dimension": "N"},
            
            # T/F
            {"id": 11, "text": "Sueles mantener la calma, incluso bajo mucha presión.", "dimension": "T"},
            {"id": 12, "text": "Eres más propenso a seguir a tu cabeza que a tu corazón.", "dimension": "T"},
            {"id": 13, "text": "Ver a otras personas llorar puede hacer que tú también sientas ganas de llorar.", "dimension": "F"},
            {"id": 14, "text": "Eres una persona muy sentimental.", "dimension": "F"},
            {"id": 15, "text": "Tu felicidad proviene más de ayudar a otros a lograr cosas que de tus propios logros.", "dimension": "F"},
            {"id": 31, "text": "Te consideras más práctico que creativo.", "dimension": "T"},
            {"id": 32, "text": "Te resulta fácil empatizar con alguien cuyas experiencias son muy diferentes a las tuyas.", "dimension": "F"},
            {"id": 33, "text": "Crees que las opiniones de todos deben respetarse, sin importar si están respaldadas por hechos o no.", "dimension": "F"},
            {"id": 34, "text": "Te sientes más atraído por lugares concurridos y bulliciosos que por sitios tranquilos e íntimos.", "dimension": "T"},
            {"id": 35, "text": "Te preocupa más la verdad que los sentimientos de los demás.", "dimension": "T"},
            {"id": 51, "text": "Tomas decisiones basadas en la lógica más que en las emociones.", "dimension": "T"},
            {"id": 52, "text": "Eres sensible a las emociones de los demás.", "dimension": "F"},
            {"id": 53, "text": "Valoras la armonía y la cooperación por encima de la competencia.", "dimension": "F"},
            {"id": 54, "text": "Prefieres el análisis objetivo sobre las consideraciones personales.", "dimension": "T"},
            {"id": 55, "text": "Consideras importante mantener las relaciones personales incluso cuando es inconveniente.", "dimension": "F"},
            
            # J/P
            {"id": 16, "text": "A menudo haces un plan de respaldo para tu plan de respaldo.", "dimension": "J"},
            {"id": 17, "text": "Prefieres terminar por completo un proyecto antes de comenzar otro.", "dimension": "J"},
            {"id": 18, "text": "Te gusta usar herramientas de organización como agendas y listas.", "dimension": "J"},
            {"id": 19, "text": "Sueles preferir hacer lo que sientes en cada momento en lugar de planificar una rutina diaria.", "dimension": "P"},
            {"id": 20, "text": "Te interesan tantas cosas que te resulta difícil elegir qué probar después.", "dimension": "P"},
            {"id": 36, "text": "Prefieres improvisar en lugar de dedicar tiempo a crear un plan detallado.", "dimension": "P"},
            {"id": 37, "text": "Consideras que las fechas límite son estresantes.", "dimension": "P"},
            {"id": 38, "text": "Prefieres tener todo planeado con antelación.", "dimension": "J"},
            {"id": 39, "text": "Disfrutas tener una rutina clara en tu vida diaria.", "dimension": "J"},
            {"id": 40, "text": "A menudo dejas las cosas para el último minuto.", "dimension": "P"},
            {"id": 56, "text": "Te gusta mantener tus opciones abiertas en lugar de comprometerte con un plan rígido.", "dimension": "P"},
            {"id": 57, "text": "Prefieres la estructura y la organización en tu entorno de trabajo.", "dimension": "J"},
            {"id": 58, "text": "Disfrutas explorando diferentes posibilidades antes de tomar una decisión.", "dimension": "P"},
            {"id": 59, "text": "Te sientes satisfecho cuando completas tus tareas antes de lo previsto.", "dimension": "J"},
            {"id": 60, "text": "Te adaptas fácilmente a cambios inesperados en los planes.", "dimension": "P"}
        ]
    }
}

def get_questionnaire_by_length(length=20, lang="en"):
    """Get questionnaire by length and language"""
    lang_data = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    all_questions = lang_data["questions"]
    
    # Simple filtering by ID for length
    if length == 20:
        return [q for q in all_questions if q["id"] <= 20]
    elif length == 40:
        return [q for q in all_questions if q["id"] <= 40]
    else:
        return all_questions

def load_questionnaire(file_path=None, length=20, lang="en"):
    """Load questionnaire from file or return questions by length/lang"""
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # If loading from file, use the questions in the file
            if 'questionnaire' in data and 'questions' in data['questionnaire']:
                return data['questionnaire']['questions']
            return data.get('questions', get_questionnaire_by_length(length, lang))
    return get_questionnaire_by_length(length, lang)

def save_questionnaire(questionnaire_data, file_path):
    """Save questionnaire data to JSON file in reports directory"""
    try:
        # Add timestamp
        questionnaire_data['metadata']['saved_at'] = datetime.now().isoformat()
        
        # Create reports directory in project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        reports_dir = os.path.join(project_root, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        full_path = os.path.join(reports_dir, os.path.basename(file_path))
        
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(questionnaire_data, f, indent=2, ensure_ascii=False)
        return full_path  # Return actual path used
    except Exception as e:
        print(f"Error saving questionnaire: {e}")
        return False
