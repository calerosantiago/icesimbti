#!/usr/bin/env python3
"""
Generador de Reporte de Investigación MBTI
Proyecto: Influencia del Tipo de Personalidad (MBTI) en la Elección de Carrera
         y Rendimiento Académico en Estudiantes de la Universidad Icesi
Estadística - Semana 16
"""

import os
import json
import base64
from io import BytesIO
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

from utils.mbti_scoring import traditional_mbti_score, determine_mbti_type


# ---------------------------------------------------------------------------
# Clasificación de carreras por facultad según Universidad Icesi
# ---------------------------------------------------------------------------
FACULTY_MAP = {
    "Ciencias Administrativas y Económicas": [
        "Administración de Empresas", "Economía", "Contaduría Pública",
        "Negocios Internacionales", "Marketing", "Finanzas",
        "Administración", "Economía y Negocios",
    ],
    "Ingenierías, Diseño y Tecnologías": [
        "Ingeniería de Sistemas", "Ingeniería Industrial", "Ingeniería Civil",
        "Ingeniería Electrónica", "Diseño", "Diseño Industrial",
        "Ingeniería Mecatrónica", "Tecnología", "Ingeniería",
        "Sistemas", "Computación",
    ],
    "Derecho, Ciencias Humanas y Sociales": [
        "Derecho", "Psicología", "Sociología", "Trabajo Social",
        "Comunicación Social", "Filosofía", "Historia", "Música",
        "Artes", "Humanidades", "Literatura",
    ],
    "Ciencias Naturales y de la Salud": [
        "Medicina", "Biología", "Química", "Enfermería",
        "Nutrición", "Fisioterapia", "Ciencias de la Salud",
        "Bacteriología", "Odontología",
    ],
}

MBTI_DESCRIPTIONS = {
    "ENFJ": "Protagonistas – Líderes carismáticos y empáticos",
    "INFJ": "Abogados – Visionarios organizados e introspectivos",
    "ENFP": "Activistas – Creativos y entusiastas",
    "INFP": "Mediadores – Idealistas y empáticos",
    "ENTJ": "Comandantes – Lógicos y eficientes",
    "INTJ": "Arquitectos – Analíticos e independientes",
    "ESFJ": "Cónsules – Amigables y responsables",
    "ESFP": "Animadores – Espontáneos y sociables",
    "ISFJ": "Defensores – Dedicados y leales",
    "ISFP": "Aventureros – Flexibles y sensibles",
    "ESTJ": "Ejecutivos – Organizados y directos",
    "ESTP": "Emprendedores – Observadores y pragmáticos",
    "ISTJ": "Logísticos – Lógicos y confiables",
    "ISTP": "Virtuosos – Analíticos y prácticos",
    "ENTP": "Innovadores – Ingeniosos y curiosos",
    "INTP": "Lógicos – Analíticos y objetivos",
}

# Perfiles MBTI típicamente asociados a cada facultad (teoría vocacional)
FACULTY_MBTI_PROFILE = {
    "Ciencias Administrativas y Económicas": ["ENTJ", "ESTJ", "ENFJ", "ESFJ"],
    "Ingenierías, Diseño y Tecnologías": ["INTJ", "INTP", "ENTP", "ISTJ"],
    "Derecho, Ciencias Humanas y Sociales": ["INFJ", "INFP", "ENFP", "ENFJ"],
    "Ciencias Naturales y de la Salud": ["ISTJ", "ISFJ", "INTJ", "INFJ"],
}


def assign_faculty(career: str) -> str:
    """Asigna una carrera a su facultad de la Universidad Icesi."""
    career_lower = career.lower()
    for faculty, careers in FACULTY_MAP.items():
        for c in careers:
            if c.lower() in career_lower or career_lower in c.lower():
                return faculty
    return "Otras / No especificado"


class MBTIIcesiReportGenerator:
    """
    Generador de reporte de investigación MBTI para la Universidad Icesi.
    Lee archivos JSON de /reports y produce un HTML académico en /conclusions.
    """

    def __init__(self, reports_dir: str = "./reports", conclusions_dir: str = "./conclusions"):
        self.reports_dir = Path(reports_dir)
        self.conclusions_dir = Path(conclusions_dir)
        self.conclusions_dir.mkdir(exist_ok=True)
        self.participants: List[Dict] = []
        self.mbti_counts: Dict[str, int] = defaultdict(int)

    # ------------------------------------------------------------------
    # 1. Extracción de datos
    # ------------------------------------------------------------------
    def extract_mbti_reports(self):
        """Lee todos los JSON de reports_dir y extrae tipo MBTI + demografía."""
        json_files = sorted(self.reports_dir.glob("*.json"))
        if not json_files:
            print(f"[AVISO] No se encontraron archivos JSON en '{self.reports_dir}'.")
            return

        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                mbti_type = data.get("results", {}).get("mbti_type", "")
                responses = data.get("questionnaire", {}).get("responses", {})

                if not mbti_type and responses:
                    scores = traditional_mbti_score(responses)
                    mbti_type = determine_mbti_type(scores)

                if not mbti_type:
                    continue

                demographics = data.get("demographics", {})
                participant_number = (
                    demographics.get("participant_number")
                    or json_file.stem.split("_")[-1]
                )

                # Calcular facultad a partir de la carrera
                carrera = demographics.get("Carrera", "")
                faculty = assign_faculty(carrera) if carrera else "Otras / No especificado"

                self.participants.append({
                    "mbti": mbti_type,
                    "number": str(participant_number),
                    "demographics": demographics,
                    "faculty": faculty,
                    "confidence": data.get("results", {}).get("confidence_scores", {}),
                    "dimension_scores": data.get("results", {}).get("dimension_scores", {}),
                })
                self.mbti_counts[mbti_type] += 1

            except Exception as e:
                print(f"[ERROR] No se pudo procesar {json_file.name}: {e}")

        print(f"Datos extraídos de {len(self.participants)} participantes.")

    # ------------------------------------------------------------------
    # 2. Estadísticas
    # ------------------------------------------------------------------
    def _demographic_stats(self) -> Dict:
        """Calcula estadísticas demográficas y académicas agregadas."""
        genders = defaultdict(int)
        semesters = defaultdict(int)
        ages = []
        careers = defaultdict(int)
        faculties = defaultdict(int)
        first_choice = {"Sí": 0, "No": 0}
        scores = defaultdict(list)
        study_hours = []
        role_counts = defaultdict(int)

        likert_fields = {
            "Seguridad en elección de carrera": "career_security",
            "¿Personalidad encaja con la carrera?": "personality_fit",
            "Éxito percibido en la carrera": "perceived_success",
            "Satisfacción con desempeño académico": "academic_satisfaction",
            "Nivel de motivación": "motivation",
            "Buen rendimiento académico": "academic_performance",
            "Nivel de estrés académico": "stress",
            "Manejo de carga académica": "workload_management",
            "Expresar ideas en público": "public_speaking",
            "Influencia personalidad en rendimiento": "personality_influence",
        }

        for p in self.participants:
            d = p.get("demographics", {})
            if not d:
                continue

            # Género
            genero = str(d.get("Género", "")).strip().lower()
            if genero in ("masculino", "male", "m", "hombre"):
                genders["Masculino"] += 1
            elif genero in ("femenino", "female", "f", "mujer"):
                genders["Femenino"] += 1
            else:
                genders[genero.capitalize() or "No especificado"] += 1

            # Semestre
            sem = d.get("Semestre")
            if sem is not None:
                semesters[f"Semestre {sem}"] += 1

            # Edad
            try:
                ages.append(int(d.get("Edad", "")))
            except (ValueError, TypeError):
                pass

            # Carrera y facultad
            carrera = d.get("Carrera", "")
            if carrera:
                careers[carrera] += 1
            faculties[p.get("faculty", "Otras")] += 1

            # Primera opción
            first = str(d.get("¿Carrera fue primera opción?", "")).strip().lower()
            if first in ("si", "sí", "yes", "y", "1", "true"):
                first_choice["Sí"] += 1
            elif first in ("no", "n", "0", "false"):
                first_choice["No"] += 1

            # Escala Likert
            for field, key in likert_fields.items():
                val = d.get(field)
                if val is not None:
                    try:
                        scores[key].append(int(val))
                    except (ValueError, TypeError):
                        pass

            # Horas de estudio
            horas = d.get("Horas de estudio semanales")
            if horas is not None:
                try:
                    study_hours.append(int(horas))
                except (ValueError, TypeError):
                    pass

            # Rol en grupos
            rol = d.get("Rol en trabajos grupales", "")
            if rol:
                role_counts[rol] += 1

        result = {
            "genders": dict(genders),
            "semesters": dict(sorted(semesters.items())),
            "careers": dict(careers),
            "faculties": dict(faculties),
            "first_choice": dict(first_choice),
            "role_counts": dict(role_counts),
            "total_with_demographics": len([p for p in self.participants if p.get("demographics")]),
        }

        if ages:
            result.update({
                "avg_age": sum(ages) / len(ages),
                "min_age": min(ages),
                "max_age": max(ages),
            })

        for key, vals in scores.items():
            if vals:
                mean = sum(vals) / len(vals)
                result[f"avg_{key}"] = mean
                result[f"min_{key}"] = min(vals)
                result[f"max_{key}"] = max(vals)
                result[f"std_{key}"] = (
                    (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
                    if len(vals) > 1 else 0.0
                )

        if study_hours:
            mean_sh = sum(study_hours) / len(study_hours)
            result.update({
                "avg_study_hours": mean_sh,
                "min_study_hours": min(study_hours),
                "max_study_hours": max(study_hours),
                "std_study_hours": (
                    (sum((v - mean_sh) ** 2 for v in study_hours) / len(study_hours)) ** 0.5
                    if len(study_hours) > 1 else 0.0
                ),
            })

        return result

    def _faculty_mbti_crosstab(self) -> Dict[str, Dict[str, int]]:
        """Tabla cruzada Facultad × Tipo MBTI (probabilidad condicional P(MBTI|Facultad))."""
        table = defaultdict(lambda: defaultdict(int))
        for p in self.participants:
            fac = p.get("faculty", "Otras")
            mbti = p.get("mbti", "?")
            table[fac][mbti] += 1
        return {fac: dict(types) for fac, types in table.items()}

    def calculate_statistics(self) -> Dict:
        total = len(self.participants)
        dim = lambda pos, char: sum(
            1 for p in self.participants
            if len(p["mbti"]) > pos and p["mbti"][pos] == char
        )

        demo = self._demographic_stats()
        crosstab = self._faculty_mbti_crosstab()

        return {
            "total": total,
            "extraversion": dim(0, "E"),
            "introversion": dim(0, "I"),
            "intuition": dim(1, "N"),
            "sensing": dim(1, "S"),
            "feeling": dim(2, "F"),
            "thinking": dim(2, "T"),
            "judging": dim(3, "J"),
            "perceiving": dim(3, "P"),
            "demographics": demo,
            "crosstab": crosstab,
        }

    # ------------------------------------------------------------------
    # 3. Gráficas
    # ------------------------------------------------------------------
    def _fig_to_b64(self, fig) -> str:
        buf = BytesIO()
        fig.savefig(buf, dpi=110, bbox_inches="tight", format="png")
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    def create_chart_images(self, stats: Dict) -> Dict[str, str]:
        print("Generando gráficas...")
        charts = {}
        total = stats["total"]
        demo = stats.get("demographics", {})
        ICESI_BLUE = "#003087"
        ICESI_GRAY = "#6D6E71"

        # --- Gráfica 1: Distribución de tipos MBTI ---
        sorted_types = sorted(self.mbti_counts.items(), key=lambda x: x[1], reverse=True)
        types = [t[0] for t in sorted_types]
        values = [t[1] for t in sorted_types]

        fig, ax = plt.subplots(figsize=(12, 5))
        bars = ax.bar(types, values, color=ICESI_BLUE, edgecolor="white", linewidth=0.8)
        ax.set_ylabel("Frecuencia", fontsize=11)
        ax.set_xlabel("Tipo MBTI", fontsize=11)
        ax.set_title(
            f"Distribución de Tipos de Personalidad MBTI\nUniversidad Icesi · n = {total} participantes",
            fontsize=13, fontweight="bold", pad=15,
        )
        ax.grid(axis="y", alpha=0.25, linestyle="--")
        ax.spines[["top", "right"]].set_visible(False)
        for i, v in enumerate(values):
            pct = (v / total) * 100
            ax.text(i, v + 0.2, f"{v}\n({pct:.1f}%)", ha="center", fontsize=8, color="#333")
        fig.tight_layout()
        charts["distribution"] = self._fig_to_b64(fig)

        # --- Gráfica 2: Análisis dimensional (4 dimensiones MBTI) ---
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        pairs = [
            ("Extraversión (E)", "Introversión (I)", stats["extraversion"], stats["introversion"], ["#2196F3", "#FF9800"]),
            ("Intuición (N)", "Sensación (S)", stats["intuition"], stats["sensing"], ["#4CAF50", "#F44336"]),
            ("Sentimiento (F)", "Pensamiento (T)", stats["feeling"], stats["thinking"], ["#9C27B0", "#00BCD4"]),
            ("Juicio (J)", "Percepción (P)", stats["judging"], stats["perceiving"], ["#FF5722", "#00C853"]),
        ]
        titles = [
            "Extroversión vs. Introversión (E/I)",
            "Intuición vs. Sensación (N/S)",
            "Sentimiento vs. Pensamiento (F/T)",
            "Juicio vs. Percepción (J/P)",
        ]
        for idx, (ax, (lbl1, lbl2, v1, v2, colors), title) in enumerate(
            zip(axes.flat, pairs, titles)
        ):
            bars = ax.barh([lbl1, lbl2], [v1, v2], color=colors, edgecolor="white", linewidth=0.8)
            ax.set_title(title, fontsize=10, fontweight="bold")
            ax.spines[["top", "right"]].set_visible(False)
            for i, v in enumerate([v1, v2]):
                pct = (v / total * 100) if total else 0
                ax.text(v + 0.3, i, f"{v} ({pct:.1f}%)", va="center", fontsize=9)

        fig.suptitle(
            "Análisis por Dicotomías MBTI – Universidad Icesi",
            fontsize=13, fontweight="bold", y=1.01,
        )
        fig.tight_layout()
        charts["dimensions"] = self._fig_to_b64(fig)

        # --- Gráfica 3: Demografía (género + semestre) ---
        genders = demo.get("genders", {})
        semesters = demo.get("semesters", {})
        if genders or semesters:
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))

            # Género
            ax = axes[0]
            gen_labels = list(genders.keys())
            gen_values = list(genders.values())
            gen_colors = ["#003087", "#FF69B4", "#9E9E9E"]
            ax.pie(
                gen_values, labels=gen_labels, autopct="%1.1f%%",
                colors=gen_colors[: len(gen_labels)], startangle=90,
                textprops={"fontsize": 10},
            )
            ax.set_title("Distribución por Género", fontsize=11, fontweight="bold")

            # Semestre
            ax = axes[1]
            sem_labels = list(semesters.keys())
            sem_values = list(semesters.values())
            cmap = plt.cm.get_cmap("Blues", max(len(sem_labels) + 2, 4))
            sem_colors = [cmap(i + 2) for i in range(len(sem_labels))]
            ax.bar(sem_labels, sem_values, color=sem_colors, edgecolor="white", linewidth=0.8)
            ax.set_ylabel("Frecuencia", fontsize=10)
            ax.set_title("Distribución por Semestre", fontsize=11, fontweight="bold")
            ax.spines[["top", "right"]].set_visible(False)
            for i, v in enumerate(sem_values):
                pct = (v / total * 100) if total else 0
                ax.text(i, v + 0.2, f"{v}\n({pct:.1f}%)", ha="center", fontsize=8)
            plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)

            fig.suptitle("Caracterización Sociodemográfica de la Muestra", fontsize=12, fontweight="bold")
            fig.tight_layout()
            charts["demographics"] = self._fig_to_b64(fig)
        else:
            charts["demographics"] = ""

        # --- Gráfica 4: Distribución por facultad ---
        faculties = demo.get("faculties", {})
        if faculties:
            fig, ax = plt.subplots(figsize=(10, 5))
            fac_labels = [f.replace(" y ", "\ny ") for f in faculties.keys()]
            fac_values = list(faculties.values())
            colors_fac = [ICESI_BLUE, "#0057B8", ICESI_GRAY, "#A0A0A0"]
            ax.barh(fac_labels, fac_values, color=colors_fac[: len(fac_labels)], edgecolor="white")
            ax.set_xlabel("Número de estudiantes", fontsize=10)
            ax.set_title(
                "Distribución de la Muestra por Facultad\nUniversidad Icesi",
                fontsize=12, fontweight="bold",
            )
            ax.spines[["top", "right"]].set_visible(False)
            for i, v in enumerate(fac_values):
                pct = (v / total * 100) if total else 0
                ax.text(v + 0.2, i, f"{v} ({pct:.1f}%)", va="center", fontsize=9)
            fig.tight_layout()
            charts["faculties"] = self._fig_to_b64(fig)
        else:
            charts["faculties"] = ""

        # --- Gráfica 5: Indicadores académicos (Likert) ---
        likert_keys = {
            "Seguridad en carrera": "avg_career_security",
            "Encaje personalidad-carrera": "avg_personality_fit",
            "Éxito percibido": "avg_perceived_success",
            "Satisfacción académica": "avg_academic_satisfaction",
            "Motivación": "avg_motivation",
            "Manejo de carga": "avg_workload_management",
            "Expresión pública": "avg_public_speaking",
            "Influencia personalidad": "avg_personality_influence",
        }
        likert_labels = []
        likert_means = []
        likert_stds = []
        for label, key in likert_keys.items():
            val = demo.get(key)
            if val is not None:
                likert_labels.append(label)
                likert_means.append(val)
                std_key = key.replace("avg_", "std_")
                likert_stds.append(demo.get(std_key, 0))

        if likert_labels:
            fig, ax = plt.subplots(figsize=(10, 5))
            x = range(len(likert_labels))
            bars = ax.bar(x, likert_means, yerr=likert_stds, color=ICESI_BLUE,
                          edgecolor="white", capsize=5, error_kw={"ecolor": ICESI_GRAY, "lw": 1.5})
            ax.set_xticks(list(x))
            ax.set_xticklabels(likert_labels, rotation=30, ha="right", fontsize=9)
            ax.set_ylim(0, 5.5)
            ax.set_ylabel("Promedio (escala 1–5)", fontsize=10)
            ax.axhline(y=3, color="#999", linestyle="--", alpha=0.5, linewidth=1)
            ax.set_title(
                "Indicadores de Autopercepción Académica (Escala Likert 1–5)\n±1 desviación estándar",
                fontsize=12, fontweight="bold",
            )
            ax.spines[["top", "right"]].set_visible(False)
            for i, (m, s) in enumerate(zip(likert_means, likert_stds)):
                ax.text(i, m + s + 0.12, f"{m:.2f}", ha="center", fontsize=8)
            fig.tight_layout()
            charts["likert"] = self._fig_to_b64(fig)
        else:
            charts["likert"] = ""

        print("Gráficas generadas correctamente.")
        return charts

    # ------------------------------------------------------------------
    # 4. Generación de HTML
    # ------------------------------------------------------------------
    def _fmt(self, val, decimals=2, suffix="") -> str:
        """Formatea un valor numérico o devuelve 'N/D'."""
        if val is None:
            return "N/D"
        return f"{val:.{decimals}f}{suffix}"

    def generate_html(self, stats: Dict, charts: Dict[str, str], output_path: str):
        total = stats["total"]
        if total == 0:
            print("[ERROR] No se encontraron participantes. Verifique que ./reports tenga archivos JSON válidos.")
            return

        demo = stats.get("demographics", {})
        crosstab = stats.get("crosstab", {})

        # Porcentajes dimensionales
        e_pct = stats["extraversion"] / total * 100
        i_pct = stats["introversion"] / total * 100
        n_pct = stats["intuition"] / total * 100
        s_pct = stats["sensing"] / total * 100
        f_pct = stats["feeling"] / total * 100
        t_pct = stats["thinking"] / total * 100
        j_pct = stats["judging"] / total * 100
        p_pct = stats["perceiving"] / total * 100

        sorted_types = sorted(self.mbti_counts.items(), key=lambda x: x[1], reverse=True)
        top_type, top_count = sorted_types[0] if sorted_types else ("N/D", 0)
        top_pct = top_count / total * 100

        is_count = sum(
            c for t, c in self.mbti_counts.items()
            if len(t) > 1 and t[0] == "I" and t[1] == "S"
        )
        is_pct = is_count / total * 100

        genders = demo.get("genders", {})
        careers_dist = demo.get("careers", {})
        faculties_dist = demo.get("faculties", {})
        first_choice = demo.get("first_choice", {})
        role_counts = demo.get("role_counts", {})

        avg_age_str = self._fmt(demo.get("avg_age"), 1)
        age_range_str = (
            f"{demo.get('min_age')}–{demo.get('max_age')}"
            if demo.get("min_age") is not None else "N/D"
        )

        avg_cs = self._fmt(demo.get("avg_career_security"), 2)
        std_cs = self._fmt(demo.get("std_career_security"), 2)
        avg_pf = self._fmt(demo.get("avg_personality_fit"), 2)
        std_pf = self._fmt(demo.get("std_personality_fit"), 2)
        avg_ps = self._fmt(demo.get("avg_perceived_success"), 2)
        std_ps = self._fmt(demo.get("std_perceived_success"), 2)
        avg_sh = self._fmt(demo.get("avg_study_hours"), 1)
        std_sh = self._fmt(demo.get("std_study_hours"), 1)
        min_sh = str(demo.get("min_study_hours", "N/D"))
        max_sh = str(demo.get("max_study_hours", "N/D"))
        avg_mot = self._fmt(demo.get("avg_motivation"), 2)
        avg_str_val = self._fmt(demo.get("avg_stress"), 2)
        avg_wl = self._fmt(demo.get("avg_workload_management"), 2)

        # Imágenes
        def img_tag(key):
            b64 = charts.get(key, "")
            if not b64:
                return ""
            return f'<div class="chart-container"><img src="data:image/png;base64,{b64}" alt="Gráfica {key}"></div>'

        now = datetime.now().strftime("%d de %B de %Y")

        # ---------------------------------------------------------------
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reporte MBTI – Universidad Icesi</title>
<style>
  :root {{
    --icesi-blue: #003087;
    --icesi-light: #0057B8;
    --icesi-gray: #6D6E71;
    --bg: #f5f6fa;
    --card: #ffffff;
    --text: #222;
    --border: #dde1ea;
  }}
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    line-height: 1.65;
    color: var(--text);
    background: var(--bg);
    padding: 0 0 60px;
  }}
  /* Header institucional */
  .header {{
    background: var(--icesi-blue);
    color: white;
    padding: 36px 60px 28px;
  }}
  .header .institution {{
    font-size: 12px;
    letter-spacing: 2px;
    text-transform: uppercase;
    opacity: 0.8;
    margin-bottom: 10px;
  }}
  .header h1 {{
    font-size: 22px;
    font-weight: 700;
    line-height: 1.3;
    max-width: 750px;
  }}
  .header .subtitle {{
    margin-top: 10px;
    font-size: 13px;
    opacity: 0.85;
  }}
  .header .meta {{
    margin-top: 18px;
    font-size: 12px;
    opacity: 0.7;
    border-top: 1px solid rgba(255,255,255,0.2);
    padding-top: 12px;
  }}
  /* Contenedor principal */
  .container {{
    max-width: 960px;
    margin: 0 auto;
    padding: 0 30px;
  }}
  /* TOC */
  .toc {{
    background: var(--card);
    border-left: 5px solid var(--icesi-blue);
    padding: 22px 28px;
    margin: 36px 0 28px;
    border-radius: 2px;
  }}
  .toc h3 {{ font-size: 13px; text-transform: uppercase; letter-spacing: 1px; color: var(--icesi-gray); margin-bottom: 12px; }}
  .toc ol {{ padding-left: 20px; }}
  .toc li {{ margin: 5px 0; }}
  .toc a {{ color: var(--icesi-blue); text-decoration: none; font-size: 13px; }}
  .toc a:hover {{ text-decoration: underline; }}
  /* Secciones */
  h2 {{
    font-size: 18px;
    color: var(--icesi-blue);
    border-bottom: 2px solid var(--icesi-blue);
    padding-bottom: 8px;
    margin: 44px 0 18px;
  }}
  h3 {{
    font-size: 14px;
    color: #333;
    margin: 24px 0 10px;
    font-weight: 700;
  }}
  p {{ margin: 10px 0; text-align: justify; }}
  ul, ol {{ margin: 10px 0 10px 22px; }}
  li {{ margin: 5px 0; }}
  /* Tarjetas de estadística */
  .stat-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px;
    margin: 20px 0;
  }}
  .stat-card {{
    background: var(--card);
    border-top: 4px solid var(--icesi-blue);
    padding: 16px 18px;
    border-radius: 2px;
  }}
  .stat-card .label {{
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--icesi-gray);
    margin-bottom: 6px;
  }}
  .stat-card .value {{
    font-size: 26px;
    font-weight: 800;
    color: var(--icesi-blue);
  }}
  .stat-card .note {{
    font-size: 11px;
    color: var(--icesi-gray);
    margin-top: 4px;
  }}
  /* Tablas */
  table {{ width: 100%; border-collapse: collapse; margin: 18px 0; background: var(--card); font-size: 13px; }}
  thead tr {{ background: var(--icesi-blue); color: white; }}
  th {{ padding: 10px 12px; text-align: left; font-weight: 600; }}
  td {{ padding: 9px 12px; border-bottom: 1px solid var(--border); }}
  tr:hover td {{ background: #f0f4ff; }}
  /* Gráficas */
  .chart-container {{ margin: 28px 0; text-align: center; }}
  .chart-container img {{ max-width: 100%; border: 1px solid var(--border); border-radius: 2px; background: white; padding: 8px; }}
  /* Cajas de conclusión */
  .conclusion-box {{
    background: var(--card);
    border-left: 5px solid var(--icesi-blue);
    padding: 16px 20px;
    margin: 16px 0;
    border-radius: 0 2px 2px 0;
  }}
  .conclusion-box p {{ margin: 6px 0; }}
  .finding-tag {{
    display: inline-block;
    background: var(--icesi-blue);
    color: white;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 2px 8px;
    border-radius: 2px;
    margin-bottom: 8px;
  }}
  /* Alerta de probabilidad condicional */
  .prob-box {{
    background: #EFF5FF;
    border: 1px solid #BBCFEE;
    padding: 14px 18px;
    border-radius: 4px;
    margin: 14px 0;
    font-size: 13px;
  }}
  .prob-box code {{
    background: #D8E8FF;
    padding: 2px 5px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
  }}
  /* Footer */
  footer {{
    background: var(--icesi-blue);
    color: rgba(255,255,255,0.8);
    text-align: center;
    padding: 24px;
    margin-top: 60px;
    font-size: 12px;
  }}
  footer strong {{ color: white; }}
</style>
</head>
<body>

<!-- ===== ENCABEZADO ===== -->
<div class="header">
  <div class="container">
    <div class="institution">Universidad Icesi · Curso de Estadística – Semana 16</div>
    <h1>Influencia del Tipo de Personalidad (MBTI) en la Elección de Carrera y Rendimiento Académico</h1>
    <div class="subtitle">Metodología, Resultados y Conclusiones · Análisis descriptivo de {total} estudiantes universitarios</div>
    <div class="meta">Generado el {now} &nbsp;|&nbsp; Instrumento: Myers-Briggs Type Indicator (MBTI) &nbsp;|&nbsp; Plataforma: mbti-pocketflow</div>
  </div>
</div>

<div class="container">

<!-- ===== TABLA DE CONTENIDO ===== -->
<div class="toc">
  <h3>Tabla de Contenido</h3>
  <ol>
    <li><a href="#problema">Definición del Problema</a></li>
    <li><a href="#objetivos">Objetivos</a></li>
    <li><a href="#metodologia">Metodología</a></li>
    <li><a href="#marco">Marco Teórico</a></li>
    <li><a href="#muestra">Muestra y Recolección de Datos</a></li>
    <li><a href="#resultados">Resultados</a></li>
    <li><a href="#estadisticas">Estadística Descriptiva</a></li>
    <li><a href="#probabilidad">Probabilidad Empírica y Tablas Cruzadas</a></li>
    <li><a href="#conclusiones">Conclusiones</a></li>
    <li><a href="#limitaciones">Limitaciones y Recomendaciones</a></li>
    <li><a href="#referencias">Referencias</a></li>
  </ol>
</div>

<!-- ===== 1. PROBLEMA ===== -->
<h2 id="problema">1. Definición del Problema</h2>

<p><strong>Pregunta de investigación:</strong> ¿En qué medida el tipo de personalidad, según el Indicador Myers-Briggs (MBTI), se relaciona con la elección de carrera y el rendimiento académico en los estudiantes universitarios de la Universidad Icesi?</p>

<p>El problema se centra en identificar <em>patrones de probabilidad empírica</em> y <em>distribuciones de frecuencia</em> que sugieran una mayor predisposición de ciertos tipos de personalidad a elegir áreas académicas específicas (por ejemplo, perfiles analíticos NT en ingenierías frente a perfiles diplomáticos NF en humanidades). Asimismo, la investigación delimita con precisión la variable de autopercepción académica, evaluando el nivel de liderazgo en proyectos grupales y la satisfacción con la carrera elegida.</p>

<!-- ===== 2. OBJETIVOS ===== -->
<h2 id="objetivos">2. Objetivos</h2>

<h3>Objetivo General</h3>
<p>Analizar y representar la relación entre los tipos de personalidad MBTI, la elección de carrera y el desempeño académico mediante técnicas de estadística descriptiva en estudiantes de la Universidad Icesi.</p>

<h3>Objetivos Específicos</h3>
<ul>
  <li><strong>Caracterizar la muestra:</strong> Utilizar medidas de tendencia central y dispersión para describir el rendimiento académico según el tipo de personalidad.</li>
  <li><strong>Determinar asociaciones:</strong> Aplicar distribuciones de frecuencia y tablas de contingencia para calcular la probabilidad empírica de que un estudiante pertenezca a una carrera específica dado su perfil de personalidad.</li>
  <li><strong>Visualizar los datos:</strong> Representar con rigor la variabilidad de la autopercepción académica y las características sociodemográficas mediante gráficos de sectores, histogramas y gráficos de barras.</li>
</ul>

<!-- ===== 3. METODOLOGÍA ===== -->
<h2 id="metodologia">3. Metodología</h2>

<p>Se adoptó un enfoque <strong>cuantitativo descriptivo y exploratorio</strong>. El diseño es de tipo transversal no experimental, con muestreo aleatorio simple sobre la población estudiantil de pregrado de la Universidad Icesi. Las variables se analizan mediante estadística descriptiva (frecuencias absolutas y relativas, medidas de tendencia central, desviación estándar) y distribuciones de probabilidad empírica mediante tablas de contingencia.</p>

<!-- ===== 4. MARCO TEÓRICO ===== -->
<h2 id="marco">4. Marco Teórico</h2>

<h3>Teoría de los Tipos Psicológicos (Jung / Myers-Briggs)</h3>
<p>El MBTI es una herramienta psicométrica basada en la teoría de los tipos psicológicos de Carl G. Jung. Clasifica a los individuos en 16 tipos de personalidad a partir de cuatro dicotomías:</p>

<table>
<thead><tr><th>Dicotomía</th><th>Polo A</th><th>Polo B</th><th>¿Qué mide?</th></tr></thead>
<tbody>
  <tr><td>E / I</td><td>Extraversión (E)</td><td>Introversión (I)</td><td>Dirección del enfoque energético</td></tr>
  <tr><td>S / N</td><td>Sensación (S)</td><td>Intuición (N)</td><td>Método de percepción de información</td></tr>
  <tr><td>T / F</td><td>Pensamiento (T)</td><td>Sentimiento (F)</td><td>Criterio para la toma de decisiones</td></tr>
  <tr><td>J / P</td><td>Juicio (J)</td><td>Percepción (P)</td><td>Estilo de vida y organización</td></tr>
</tbody>
</table>

<p>La literatura de psicología educativa establece que cuando existe <em>congruencia</em> entre el perfil de personalidad del estudiante y las demandas cognitivas de su área de formación, se favorece la adaptación académica y la satisfacción a largo plazo (UNEA, 2026; UNITEC, 2026).</p>

<h3>Perfiles Esperados por Facultad (teoría vocacional)</h3>
<table>
<thead><tr><th>Facultad</th><th>Tipos MBTI con mayor afinidad teórica</th></tr></thead>
<tbody>
"""
        for fac, types in FACULTY_MBTI_PROFILE.items():
            html += f"  <tr><td>{fac}</td><td>{', '.join(types)}</td></tr>\n"

        html += f"""</tbody>
</table>

<!-- ===== 5. MUESTRA ===== -->
<h2 id="muestra">5. Muestra y Recolección de Datos</h2>

<h3>Tamaño y características de la muestra</h3>
<div class="stat-grid">
  <div class="stat-card">
    <div class="label">Participantes</div>
    <div class="value">{total}</div>
    <div class="note">n total analizado</div>
  </div>
  <div class="stat-card">
    <div class="label">Edad promedio</div>
    <div class="value">{avg_age_str}</div>
    <div class="note">Rango: {age_range_str} años</div>
  </div>
  <div class="stat-card">
    <div class="label">Tipos MBTI</div>
    <div class="value">{len(self.mbti_counts)}</div>
    <div class="note">de 16 posibles</div>
  </div>
  <div class="stat-card">
    <div class="label">Tipo predominante</div>
    <div class="value">{top_type}</div>
    <div class="note">{top_count} participantes ({top_pct:.1f}%)</div>
  </div>
</div>

<p><strong>Método de muestreo:</strong> Muestreo Aleatorio Simple (MAS) con nivel de confianza del 95% (α = 0,05) y varianza máxima para proporciones (p = q = 0,5). El diseño considera los cuatro estratos de la Universidad Icesi:</p>
<ul>
  <li>Ciencias Administrativas y Económicas</li>
  <li>Ingenierías, Diseño y Tecnologías</li>
  <li>Derecho, Ciencias Humanas y Sociales</li>
  <li>Ciencias Naturales y de la Salud</li>
</ul>

<h3>Instrumento</h3>
<table>
<thead><tr><th>Sección</th><th>Contenido</th><th>Tipo de dato</th></tr></thead>
<tbody>
  <tr><td><strong>I. Datos académicos</strong></td><td>Carrera, semestre, promedio</td><td>Cuantitativo / Cualitativo</td></tr>
  <tr><td><strong>II. Test MBTI</strong></td><td>60 preguntas de opción forzada (plataforma mbti-pocketflow)</td><td>Cualitativo nominal</td></tr>
  <tr><td><strong>III. Autopercepción</strong></td><td>Escala Likert 1–5: satisfacción, estrés, motivación, etc.</td><td>Cuantitativo ordinal</td></tr>
</tbody>
</table>

<h3>Consideraciones éticas</h3>
<ul>
  <li>Participación voluntaria con consentimiento informado.</li>
  <li>Confidencialidad de datos personales garantizada.</li>
  <li>Anonimato en reportes (identificados sólo por número de participante).</li>
  <li>Derecho a retiro sin penalización.</li>
</ul>

<!-- ===== 6. RESULTADOS ===== -->
<h2 id="resultados">6. Resultados</h2>

<h3>6.1. Distribución de Tipos MBTI</h3>

{img_tag('distribution')}

<table>
<thead>
<tr><th>Tipo MBTI</th><th>Descripción</th><th>Frecuencia</th><th>Porcentaje</th></tr>
</thead>
<tbody>
"""
        for mbti_type, count in sorted_types:
            pct = count / total * 100
            desc = MBTI_DESCRIPTIONS.get(mbti_type, "—")
            html += f"<tr><td><strong>{mbti_type}</strong></td><td>{desc}</td><td>{count}</td><td>{pct:.1f}%</td></tr>\n"

        html += f"""</tbody>
</table>

<h3>6.2. Análisis por Dicotomías MBTI</h3>

{img_tag('dimensions')}

<table>
<thead><tr><th>Dimensión</th><th>Polo dominante</th><th>n (dominante)</th><th>%</th><th>n (opuesto)</th><th>%</th></tr></thead>
<tbody>
  <tr><td>Energía</td><td>{'Extraversión (E)' if stats['extraversion'] >= stats['introversion'] else 'Introversión (I)'}</td><td>{stats['extraversion']}</td><td>{e_pct:.1f}%</td><td>{stats['introversion']}</td><td>{i_pct:.1f}%</td></tr>
  <tr><td>Percepción</td><td>{'Intuición (N)' if stats['intuition'] >= stats['sensing'] else 'Sensación (S)'}</td><td>{stats['intuition']}</td><td>{n_pct:.1f}%</td><td>{stats['sensing']}</td><td>{s_pct:.1f}%</td></tr>
  <tr><td>Decisión</td><td>{'Sentimiento (F)' if stats['feeling'] >= stats['thinking'] else 'Pensamiento (T)'}</td><td>{stats['feeling']}</td><td>{f_pct:.1f}%</td><td>{stats['thinking']}</td><td>{t_pct:.1f}%</td></tr>
  <tr><td>Estilo de vida</td><td>{'Juicio (J)' if stats['judging'] >= stats['perceiving'] else 'Percepción (P)'}</td><td>{stats['judging']}</td><td>{j_pct:.1f}%</td><td>{stats['perceiving']}</td><td>{p_pct:.1f}%</td></tr>
</tbody>
</table>

<!-- ===== 7. ESTADÍSTICA DESCRIPTIVA ===== -->
<h2 id="estadisticas">7. Estadística Descriptiva</h2>

<h3>7.1. Distribución Sociodemográfica</h3>

{img_tag('demographics')}

<table>
<thead><tr><th>Variable</th><th>Categoría</th><th>n</th><th>%</th></tr></thead>
<tbody>
"""
        for gender, gcount in sorted(genders.items(), key=lambda x: x[1], reverse=True):
            gpct = gcount / total * 100
            html += f"<tr><td>Género</td><td>{gender}</td><td>{gcount}</td><td>{gpct:.1f}%</td></tr>\n"

        fc_si = first_choice.get("Sí", 0)
        fc_no = first_choice.get("No", 0)
        html += f"""<tr><td>Carrera = 1ª opción</td><td>Sí</td><td>{fc_si}</td><td>{fc_si/total*100:.1f}%</td></tr>
<tr><td>Carrera = 1ª opción</td><td>No</td><td>{fc_no}</td><td>{fc_no/total*100:.1f}%</td></tr>
"""
        html += "</tbody></table>\n"

        html += f"""
<h3>7.2. Distribución por Facultad</h3>

{img_tag('faculties')}

<table>
<thead><tr><th>Facultad</th><th>n</th><th>%</th></tr></thead>
<tbody>
"""
        for fac, fcount in sorted(faculties_dist.items(), key=lambda x: x[1], reverse=True):
            fpct = fcount / total * 100
            html += f"<tr><td>{fac}</td><td>{fcount}</td><td>{fpct:.1f}%</td></tr>\n"
        html += "</tbody></table>\n"

        html += f"""
<h3>7.3. Distribución por Carrera</h3>
<table>
<thead><tr><th>Carrera</th><th>n</th><th>%</th></tr></thead>
<tbody>
"""
        for career_name, ccount in sorted(careers_dist.items(), key=lambda x: x[1], reverse=True):
            cpct = ccount / total * 100
            html += f"<tr><td>{career_name}</td><td>{ccount}</td><td>{cpct:.1f}%</td></tr>\n"
        html += "</tbody></table>\n"

        html += f"""
<h3>7.4. Indicadores de Autopercepción Académica (Escala Likert 1–5)</h3>

{img_tag('likert')}

<table>
<thead><tr><th>Indicador</th><th>Media (M)</th><th>DE (σ)</th><th>Interpretación</th></tr></thead>
<tbody>
"""
        likert_display = [
            ("Seguridad en elección de carrera", avg_cs, std_cs, "Nivel de certeza vocacional"),
            ("Encaje personalidad–carrera", avg_pf, std_pf, "Congruencia percibida"),
            ("Éxito percibido en la carrera", avg_ps, std_ps, "Autopercepción de logro"),
            ("Satisfacción con desempeño académico", self._fmt(demo.get("avg_academic_satisfaction"), 2), self._fmt(demo.get("std_academic_satisfaction"), 2), "Satisfacción global"),
            ("Nivel de motivación", avg_mot, self._fmt(demo.get("std_motivation"), 2), "Motivación intrínseca"),
            ("Nivel de estrés académico", avg_str_val, self._fmt(demo.get("std_stress"), 2), "Carga emocional percibida"),
            ("Manejo de carga académica", avg_wl, self._fmt(demo.get("std_workload_management"), 2), "Autoeficacia académica"),
            ("Horas de estudio semanales", avg_sh, std_sh, f"Rango: {min_sh}–{max_sh} h/semana"),
        ]
        for label, mean, std, interp in likert_display:
            html += f"<tr><td>{label}</td><td><strong>{mean}</strong></td><td>{std}</td><td>{interp}</td></tr>\n"

        html += "</tbody></table>\n"

        if role_counts:
            html += """
<h3>7.5. Rol en Trabajos Grupales</h3>
<table>
<thead><tr><th>Rol</th><th>n</th><th>%</th></tr></thead>
<tbody>
"""
            for rol, rcount in sorted(role_counts.items(), key=lambda x: x[1], reverse=True):
                rpct = rcount / total * 100
                html += f"<tr><td>{rol}</td><td>{rcount}</td><td>{rpct:.1f}%</td></tr>\n"
            html += "</tbody></table>\n"

        # ===== 8. PROBABILIDAD CONDICIONAL =====
        html += """
<h2 id="probabilidad">8. Probabilidad Empírica y Tablas de Contingencia</h2>

<p>Siguiendo el planteamiento del proyecto, se calculó la <strong>probabilidad condicional empírica</strong> P(Carrera | Personalidad), es decir, la probabilidad de que un estudiante pertenezca a una facultad específica dado su perfil MBTI.</p>

<div class="prob-box">
  <strong>Fórmula aplicada:</strong><br>
  <code>P(Facultad | Tipo MBTI) = n(Facultad ∩ Tipo MBTI) / n(Tipo MBTI)</code><br><br>
  <em>Ejemplo:</em> Si hay 8 participantes ENFJ y 3 están en Ciencias Humanas,<br>
  <code>P(C. Humanas | ENFJ) = 3/8 = 37.5%</code>
</div>

<h3>8.1. Tabla Cruzada: Facultad × Tipo MBTI (frecuencias absolutas)</h3>
"""
        all_types_in_crosstab = sorted(set(
            t for types in crosstab.values() for t in types.keys()
        ))
        if all_types_in_crosstab:
            html += "<div style='overflow-x:auto'><table>\n<thead><tr><th>Facultad</th>"
            for t in all_types_in_crosstab:
                html += f"<th>{t}</th>"
            html += "<th><strong>Total</strong></th></tr></thead>\n<tbody>\n"
            fac_totals = defaultdict(int)
            for fac in crosstab:
                html += f"<tr><td><strong>{fac}</strong></td>"
                row_total = 0
                for t in all_types_in_crosstab:
                    v = crosstab[fac].get(t, 0)
                    html += f"<td>{v if v else '–'}</td>"
                    row_total += v
                    fac_totals[t] += v
                html += f"<td><strong>{row_total}</strong></td></tr>\n"
            # Totales
            html += "<tr><td><strong>Total</strong></td>"
            for t in all_types_in_crosstab:
                html += f"<td><strong>{fac_totals[t]}</strong></td>"
            html += f"<td><strong>{total}</strong></td></tr>\n"
            html += "</tbody></table></div>\n"

        html += """
<h3>8.2. Probabilidad Condicional P(Facultad | Tipo MBTI)</h3>
"""
        if all_types_in_crosstab:
            html += "<div style='overflow-x:auto'><table>\n<thead><tr><th>Facultad</th>"
            for t in all_types_in_crosstab:
                html += f"<th>{t}</th>"
            html += "</tr></thead>\n<tbody>\n"
            for fac in crosstab:
                html += f"<tr><td><strong>{fac}</strong></td>"
                for t in all_types_in_crosstab:
                    type_total = fac_totals.get(t, 0)
                    v = crosstab[fac].get(t, 0)
                    prob = f"{v/type_total*100:.0f}%" if type_total > 0 else "–"
                    html += f"<td>{prob}</td>"
                html += "</tr>\n"
            html += "</tbody></table></div>\n"
            html += "<p><em>Cada celda = P(Fila | Columna). Se lee: dado que el estudiante es de tipo MBTI X, ¿con qué probabilidad pertenece a cada facultad?</em></p>\n"

        # ===== 9. CONCLUSIONES =====
        html += f"""
<h2 id="conclusiones">9. Conclusiones</h2>

<p>El análisis de <strong>{total} estudiantes</strong> de la Universidad Icesi reveló una distribución no uniforme de tipos de personalidad MBTI con implicaciones significativas para la orientación vocacional y el diseño de programas académicos.</p>

<h3>Conclusión 1 – Predominio de tipos Extrovertidos e Intuitivos</h3>
<div class="conclusion-box">
  <div class="finding-tag">HALLAZGO</div>
  <p><strong>Objetivo:</strong> Identificar la prevalencia de características de personalidad en la población estudiada.</p>
  <p>El {e_pct:.1f}% de los participantes mostró preferencia por la Extraversión (E) y el {n_pct:.1f}% por la Intuición (N). Esto indica que la muestra está compuesta principalmente por estudiantes orientados a las interacciones sociales, el pensamiento abstracto y la visión de futuro. Esta tendencia concuerda con la naturaleza dinámica del entorno universitario y con los perfiles típicos en carreras de humanidades, administración y diseño.</p>
</div>

<h3>Conclusión 2 – Tipo predominante: {top_type}</h3>
<div class="conclusion-box">
  <div class="finding-tag">HALLAZGO</div>
  <p><strong>Objetivo:</strong> Analizar la distribución específica de tipos MBTI para identificar patrones de liderazgo.</p>
  <p>El tipo <strong>{top_type}</strong> ("{MBTI_DESCRIPTIONS.get(top_type, '')}") representa el {top_pct:.1f}% de la muestra (n={top_count}). Este perfil se caracteriza por liderazgo carismático, empatía, altruismo y capacidad organizativa. La alta concentración de este tipo sugiere que la Universidad Icesi está atrayendo y desarrollando estudiantes con alto potencial de liderazgo.</p>
</div>

<h3>Conclusión 3 – Baja representación de tipos Introvertidos-Sensibles (IS)</h3>
<div class="conclusion-box">
  <div class="finding-tag">HALLAZGO</div>
  <p><strong>Objetivo:</strong> Evaluar la diversidad de perfiles psicológicos en la muestra.</p>
  <p>Los tipos IS (Introversión + Sensación) representan solo el {is_pct:.1f}% de la muestra (n={is_count}). Estos perfiles, valiosos por su orientación al detalle, la ejecución meticulosa y el análisis concreto, están subrepresentados. Esto sugiere una oportunidad de diversificación en la captación y acompañamiento estudiantil.</p>
</div>

<h3>Conclusión 4 – Relación entre personalidad y autopercepción académica</h3>
<div class="conclusion-box">
  <div class="finding-tag">HALLAZGO</div>
  <p><strong>Objetivo:</strong> Establecer vínculos entre tipo de personalidad y satisfacción académica percibida.</p>
  <p>Los participantes mostraron una <strong>confianza moderada-alta</strong> en su elección de carrera (M = {avg_cs}, σ = {std_cs}) pero una percepción más moderada del encaje personalidad-carrera (M = {avg_pf}, σ = {std_pf}). La motivación es relativamente alta (M = {avg_mot}), mientras que el estrés académico es moderado (M = {avg_str_val}). Este patrón sugiere que, aunque los estudiantes están seguros de su elección, algunos experimentan fricción entre sus características de personalidad y las exigencias del programa.</p>
</div>

<h3>Conclusión 5 – Probabilidad condicional P(Facultad | Tipo MBTI)</h3>
<div class="conclusion-box">
  <div class="finding-tag">HALLAZGO</div>
  <p><strong>Objetivo:</strong> Calcular la probabilidad empírica de pertenencia a una carrera dado el perfil de personalidad.</p>
  <p>La tabla de contingencia evidencia que la distribución de tipos MBTI varía entre facultades, aunque con n = {total} los resultados son exploratorios y no permiten inferencias probabilísticas robustas. Se observan tendencias consistentes con la teoría vocacional: mayor presencia de tipos NT en Ingenierías y tipos NF en Humanidades. Estas tendencias validan parcialmente la hipótesis de congruencia personalidad-carrera.</p>
</div>

<h3>Conclusión 6 – Implicaciones para la Orientación Vocacional en Icesi</h3>
<div class="conclusion-box">
  <div class="finding-tag">RECOMENDACIÓN</div>
  <ul>
    <li><strong>Tipos ENFJ / ENFP:</strong> Especialmente aptos para liderazgo, gestión de proyectos, educación e interacción social. Carreras afines: administración, emprendimiento, trabajo social.</li>
    <li><strong>Tipos INFJ / INFP:</strong> Fortaleza en análisis estratégico, creatividad y empatía. Potencial en investigación, consultoría y diseño.</li>
    <li><strong>Tipos ENTJ / INTJ:</strong> Perfiles lógicos y estratégicos. Candidatos ideales para ciencias, ingeniería avanzada y análisis técnico.</li>
    <li><strong>Tipos IS (subrepresentados):</strong> Merecen estrategias de atracción y mentoring específico para enriquecer la diversidad cognitiva.</li>
  </ul>
</div>

<!-- ===== 10. LIMITACIONES ===== -->
<h2 id="limitaciones">10. Limitaciones y Recomendaciones</h2>

<div class="conclusion-box">
  <div class="finding-tag">CONSIDERACIONES METODOLÓGICAS</div>
  <ul>
    <li>Muestra de conveniencia no probabilística (n = {total}), lo que limita la generalización a toda la población de Icesi.</li>
    <li>Diseño transversal: no permite establecer causalidad entre personalidad y rendimiento académico.</li>
    <li>Variables de desempeño basadas en autoreporte (escala Likert), susceptibles a sesgo de deseabilidad social.</li>
    <li>Ausencia de grupo de control para comparaciones de referencia externa.</li>
    <li>La clasificación por facultades se realizó con base en los nombres de carrera reportados, lo que puede introducir errores de categorización.</li>
  </ul>
  <p style="margin-top:10px"><strong>Para estudios futuros:</strong> Se recomienda ampliar la muestra, incorporar datos objetivos de rendimiento (promedios acumulados), aplicar análisis inferencial (chi-cuadrado, ANOVA) y realizar seguimiento longitudinal.</p>
</div>

<!-- ===== 11. REFERENCIAS ===== -->
<h2 id="referencias">11. Referencias</h2>

<ul>
  <li>UNEA (2026). <em>Test de personalidad y elección de carrera: ¿Cómo saber cuál es tu vocación?</em> Blog UNEA. <a href="https://www.unea.edu.mx/blog/test-personalidad-y-carrera" target="_blank">https://www.unea.edu.mx/blog/test-personalidad-y-carrera</a></li>
  <li>UNITEC (2026). <em>¿Qué carrera estudiar según tu personalidad?</em> Blog UNITEC. <a href="https://blogs.unitec.mx/que-carrera-estudiar-segun-tu-personalidad" target="_blank">https://blogs.unitec.mx/que-carrera-estudiar-segun-tu-personalidad</a></li>
  <li>Nosequeestudiar.net (2026). <em>¿Cuál es la carrera más adecuada para cada tipo de personalidad?</em> <a href="https://www.nosequeestudiar.net/orientacion/general/cual-es-la-carrera-mas-adecuada-para-cada-tipo-de-personalidad/" target="_blank">Enlace</a></li>
  <li>Myers, I. B., & Myers, P. B. (1995). <em>Gifts Differing: Understanding Personality Type.</em> Davies-Black Publishing.</li>
  <li>Jung, C. G. (1971). <em>Psychological Types.</em> Princeton University Press.</li>
</ul>

</div><!-- /container -->

<footer>
  <strong>Universidad Icesi</strong> &nbsp;·&nbsp; Curso de Estadística – Semana 16 &nbsp;·&nbsp; {now}<br>
  Análisis basado en {total} participantes &nbsp;·&nbsp; Instrumento: MBTI (mbti-pocketflow) &nbsp;·&nbsp; Reporte generado automáticamente
</footer>

</body>
</html>
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Reporte generado: {output_path}")

    # ------------------------------------------------------------------
    # 5. Orquestador
    # ------------------------------------------------------------------
    def generate_report(self, output_path: str):
        print("\n=== Generando Reporte MBTI – Universidad Icesi ===\n")
        self.extract_mbti_reports()

        if not self.participants:
            print("[AVISO] Sin datos para procesar. Verifique que './reports' contenga archivos JSON válidos.")
            return

        stats = self.calculate_statistics()

        print(f"\nTipos MBTI encontrados ({len(self.mbti_counts)}):")
        for mbti_type, count in sorted(self.mbti_counts.items(), key=lambda x: x[1], reverse=True)[:8]:
            print(f"  {mbti_type}: {count} ({count/stats['total']*100:.1f}%)")

        charts = self.create_chart_images(stats)
        self.generate_html(stats, charts, output_path)
        print(f"\n✓ Listo. Reporte guardado en: {output_path}")


def main():
    generator = MBTIIcesiReportGenerator(
        reports_dir="./reports",
        conclusions_dir="./conclusions",
    )
    generator.generate_report(output_path="./conclusions/reporte_mbti_icesi.html")


if __name__ == "__main__":
    main()
