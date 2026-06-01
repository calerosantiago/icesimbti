#!/usr/bin/env python3
"""
MBTI Research Report Generator - Simple Version
Generates a clean, markdown-style HTML report with embedded chart images.
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


class MBTISimpleReportGenerator:
    """Generate simple, clean MBTI research report with embedded charts."""

    reports_dir = "./input"
    conclusions_dir = "./conclusions"

    def __init__(self, reports_dir: str = "./input", conclusions_dir: str = "./conclusions"):
        self.reports_dir = Path(reports_dir)
        self.conclusions_dir = Path(conclusions_dir)
        self.conclusions_dir.mkdir(exist_ok=True)
        self.participants = []
        self.mbti_counts = defaultdict(int)

    def extract_mbti_reports(self):
        """Extract data from all MBTI JSON files."""
        json_files = sorted(self.reports_dir.glob("*.json"))

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                mbti_type = data.get("results", {}).get("mbti_type")
                responses = data.get("questionnaire", {}).get("responses", {})

                if not mbti_type and responses:
                    scores = traditional_mbti_score(responses)
                    mbti_type = determine_mbti_type(scores)

                if not mbti_type:
                    continue

                filename = json_file.stem
                parts = filename.split("_")

                participant_info = {"mbti": mbti_type}
                if filename.startswith("participant") and len(parts) > 1:
                    participant_info["number"] = parts[1]
                elif len(parts) > 2:
                    participant_info["number"] = parts[2]
                else:
                    participant_info["number"] = "unknown"

                demographics = data.get("demographics", {})
                if demographics:
                    participant_info["demographics"] = demographics
                    if "participant_number" in demographics:
                        participant_info["number"] = str(demographics["participant_number"])

                self.participants.append(participant_info)
                self.mbti_counts[mbti_type] += 1
            except:
                pass

        print(f"Extracted data from {len(self.participants)} participants")

    def _demographic_stats(self) -> Dict:
        """Compute aggregate demographic statistics from participant data."""
        genders = defaultdict(int)
        semesters = defaultdict(int)
        ages = []
        careers = defaultdict(int)
        first_choice = {"Si": 0, "No": 0}
        satisfaction_scores = defaultdict(list)
        study_hours = []

        for p in self.participants:
            d = p.get("demographics", {})
            if not d:
                continue

            genero = str(d.get("G\u00e9nero", "")).strip().lower()
            if genero in ("masculino", "male", "m"):
                genders["Male"] += 1
            elif genero in ("femenino", "female", "f"):
                genders["Female"] += 1
            else:
                genders[genero.capitalize() if genero else "Unknown"] += 1

            sem = d.get("Semestre")
            if sem is not None:
                semesters[f"{sem}th Semester"] += 1

            edad = d.get("Edad")
            if edad is not None:
                try:
                    ages.append(int(edad))
                except:
                    pass

            carrera = d.get("Carrera", "")
            if carrera:
                careers[carrera] += 1

            first = d.get("\u00bfCarrera fue primera opci\u00f3n?", "")
            if first:
                key = "Si" if str(first).strip().lower() in ("si", "s\u00ed", "yes", "y") else "No"
                first_choice[key] += 1

            for field, key in [
                ("Seguridad en elecci\u00f3n de carrera", "career_security"),
                ("\u00bfPersonalidad encaja con la carrera?", "personality_fit"),
                ("\u00c9xito percibido en la carrera", "perceived_success"),
                ("Satisfacci\u00f3n con desempe\u00f1o acad\u00e9mico", "academic_satisfaction"),
                ("Nivel de motivaci\u00f3n", "motivation"),
                ("Buen rendimiento acad\u00e9mico", "academic_performance"),
                ("Nivel de estr\u00e9s acad\u00e9mico", "stress"),
                ("Manejo de carga acad\u00e9mica", "workload_management"),
                ("Expresar ideas en p\u00fablico", "public_speaking"),
                ("Influencia personalidad en rendimiento", "personality_influence"),
            ]:
                val = d.get(field)
                if val is not None:
                    try:
                        satisfaction_scores[key].append(int(val))
                    except:
                        pass

            horas = d.get("Horas de estudio semanales")
            if horas is not None:
                try:
                    study_hours.append(int(horas))
                except:
                    pass

        result = {
            "genders": dict(genders),
            "semesters": dict(sorted(semesters.items())),
            "careers": dict(careers),
            "first_choice": dict(first_choice),
            "total_with_demographics": len([p for p in self.participants if p.get("demographics")]),
        }

        if ages:
            result["avg_age"] = sum(ages) / len(ages)
            result["min_age"] = min(ages)
            result["max_age"] = max(ages)
        else:
            result["avg_age"] = None

        for key, vals in satisfaction_scores.items():
            if vals:
                result[f"avg_{key}"] = sum(vals) / len(vals)
                result[f"min_{key}"] = min(vals)
                result[f"max_{key}"] = max(vals)
                if len(vals) > 1:
                    result[f"std_{key}"] = (sum((v - sum(vals)/len(vals))**2 for v in vals) / len(vals)) ** 0.5
                else:
                    result[f"std_{key}"] = 0.0

        if study_hours:
            result["avg_study_hours"] = sum(study_hours) / len(study_hours)
            result["min_study_hours"] = min(study_hours)
            result["max_study_hours"] = max(study_hours)
            if len(study_hours) > 1:
                mean_sh = result["avg_study_hours"]
                result["std_study_hours"] = (sum((v - mean_sh)**2 for v in study_hours) / len(study_hours)) ** 0.5
            else:
                result["std_study_hours"] = 0.0

        return result

    def calculate_statistics(self) -> Dict:
        """Calculate statistical summaries."""
        total = len(self.participants)

        extraversion = sum(1 for p in self.participants if len(p["mbti"]) > 0 and p["mbti"][0] == "E")
        introversion = sum(1 for p in self.participants if len(p["mbti"]) > 0 and p["mbti"][0] == "I")

        intuition = sum(1 for p in self.participants if len(p["mbti"]) > 1 and p["mbti"][1] == "N")
        sensing = sum(1 for p in self.participants if len(p["mbti"]) > 1 and p["mbti"][1] == "S")

        feeling = sum(1 for p in self.participants if len(p["mbti"]) > 2 and p["mbti"][2] == "F")
        thinking = sum(1 for p in self.participants if len(p["mbti"]) > 2 and p["mbti"][2] == "T")

        judging = sum(1 for p in self.participants if len(p["mbti"]) > 3 and p["mbti"][3] == "J")
        perceiving = sum(1 for p in self.participants if len(p["mbti"]) > 3 and p["mbti"][3] == "P")

        demo = self._demographic_stats()

        return {
            "total": total,
            "extraversion": extraversion,
            "introversion": introversion,
            "intuition": intuition,
            "sensing": sensing,
            "feeling": feeling,
            "thinking": thinking,
            "judging": judging,
            "perceiving": perceiving,
            "demographics": demo,
        }

    def _fig_to_b64(self, fig) -> str:
        """Save a matplotlib figure to a base64 string."""
        buf = BytesIO()
        fig.savefig(buf, dpi=100, bbox_inches='tight', format='png')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

    def create_chart_images(self, stats: Dict) -> Dict[str, str]:
        """Create chart images and return as base64 strings."""
        print("Generating chart images...")
        charts = {}
        total = stats["total"]

        # Chart 1: MBTI Distribution
        fig, ax = plt.subplots(figsize=(10, 6))
        sorted_types = sorted(self.mbti_counts.items(), key=lambda x: x[1], reverse=True)
        types = [t[0] for t in sorted_types]
        values = [t[1] for t in sorted_types]

        ax.bar(types, values, color='steelblue', edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax.set_xlabel('MBTI Type', fontsize=11, fontweight='bold')
        ax.set_title(f'MBTI Type Distribution (n={total})', fontsize=13, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        for i, v in enumerate(values):
            pct = (v / total) * 100
            ax.text(i, v + 0.5, f'{v}\n({pct:.1f}%)', ha='center', fontsize=9)

        fig.tight_layout()
        charts['distribution'] = self._fig_to_b64(fig)

        # Chart 2: Dimensional Analysis
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # E/I
        ax = axes[0, 0]
        labels = ['Extraversion (E)', 'Introversion (I)']
        values = [stats['extraversion'], stats['introversion']]
        ax.barh(labels, values, color=['#2196F3', '#FF9800'], edgecolor='black', linewidth=1.5)
        ax.set_xlabel('Count', fontsize=10, fontweight='bold')
        ax.set_title('Extraversion vs Introversion', fontsize=11, fontweight='bold')
        for i, v in enumerate(values):
            pct = (v / total) * 100
            ax.text(v + 0.5, i, f'{v} ({pct:.1f}%)', va='center', fontsize=9)

        # N/S
        ax = axes[0, 1]
        labels = ['Intuition (N)', 'Sensing (S)']
        values = [stats['intuition'], stats['sensing']]
        ax.barh(labels, values, color=['#4CAF50', '#F44336'], edgecolor='black', linewidth=1.5)
        ax.set_xlabel('Count', fontsize=10, fontweight='bold')
        ax.set_title('Intuition vs Sensing', fontsize=11, fontweight='bold')
        for i, v in enumerate(values):
            pct = (v / total) * 100
            ax.text(v + 0.5, i, f'{v} ({pct:.1f}%)', va='center', fontsize=9)

        # F/T
        ax = axes[1, 0]
        labels = ['Feeling (F)', 'Thinking (T)']
        values = [stats['feeling'], stats['thinking']]
        ax.barh(labels, values, color=['#9C27B0', '#00BCD4'], edgecolor='black', linewidth=1.5)
        ax.set_xlabel('Count', fontsize=10, fontweight='bold')
        ax.set_title('Feeling vs Thinking', fontsize=11, fontweight='bold')
        for i, v in enumerate(values):
            pct = (v / total) * 100
            ax.text(v + 0.5, i, f'{v} ({pct:.1f}%)', va='center', fontsize=9)

        # J/P
        ax = axes[1, 1]
        labels = ['Judging (J)', 'Perceiving (P)']
        values = [stats['judging'], stats['perceiving']]
        ax.barh(labels, values, color=['#FF5722', '#00E676'], edgecolor='black', linewidth=1.5)
        ax.set_xlabel('Count', fontsize=10, fontweight='bold')
        ax.set_title('Judging vs Perceiving', fontsize=11, fontweight='bold')
        for i, v in enumerate(values):
            pct = (v / total) * 100
            ax.text(v + 0.5, i, f'{v} ({pct:.1f}%)', va='center', fontsize=9)

        fig.suptitle('MBTI Dimensional Analysis', fontsize=14, fontweight='bold', y=0.995)
        fig.tight_layout()
        charts['dimensions'] = self._fig_to_b64(fig)

        # Chart 3: Demographics (only if we have demographic data)
        demo = stats.get("demographics", {})
        genders = demo.get("genders", {})
        semesters = demo.get("semesters", {})

        if genders or semesters:
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))

            # Gender
            ax = axes[0]
            gen_labels = list(genders.keys())
            gen_values = list(genders.values())
            colors = ['#2196F3', '#FF69B4', '#9E9E9E']
            ax.pie(gen_values, labels=gen_labels, autopct='%1.1f%%',
                   colors=colors[:len(gen_labels)], startangle=90,
                   textprops={'fontsize': 10, 'weight': 'bold'})
            ax.set_title('Gender Distribution', fontsize=11, fontweight='bold')

            # Semester
            ax = axes[1]
            sem_labels = list(semesters.keys())
            sem_values = list(semesters.values())
            cmap = plt.cm.get_cmap('tab20', max(len(sem_labels), 1))
            sem_colors = [cmap(i) for i in range(len(sem_labels))]
            ax.bar(sem_labels, sem_values, color=sem_colors,
                   edgecolor='black', linewidth=1.5)
            ax.set_ylabel('Count', fontsize=10, fontweight='bold')
            ax.set_title('Semester Distribution', fontsize=11, fontweight='bold')
            for i, v in enumerate(sem_values):
                pct = (v / total) * 100
                ax.text(i, v + 0.5, f'{v}\n({pct:.1f}%)', ha='center', fontsize=9)

            fig.suptitle('Demographic Distribution', fontsize=14, fontweight='bold')
            fig.tight_layout()
            charts['demographics'] = self._fig_to_b64(fig)
        else:
            charts['demographics'] = ""

        print("Charts generated successfully")
        return charts

    def generate_html(self, stats: Dict, charts: Dict[str, str], output_path: str):
        """Generate simple HTML report with embedded base64 chart images."""

        total = stats["total"]
        if total == 0:
            print("Error: no participants found. Check that ./input has valid JSON files.")
            return
        e_pct = (stats["extraversion"] / total) * 100
        i_pct = (stats["introversion"] / stats["total"]) * 100
        n_pct = (stats["intuition"] / stats["total"]) * 100
        s_pct = (stats["sensing"] / stats["total"]) * 100
        f_pct = (stats["feeling"] / stats["total"]) * 100
        t_pct = (stats["thinking"] / stats["total"]) * 100
        j_pct = (stats["judging"] / stats["total"]) * 100
        p_pct = (stats["perceiving"] / stats["total"]) * 100

        sorted_types = sorted(self.mbti_counts.items(), key=lambda x: x[1], reverse=True)
        enfj_count = self.mbti_counts.get("ENFJ", 0)
        enfj_pct = (enfj_count / stats["total"]) * 100

        dist_img = f"data:image/png;base64,{charts['distribution']}"
        dim_img = f"data:image/png;base64,{charts['dimensions']}"
        demo_img = f"data:image/png;base64,{charts['demographics']}" if charts.get('demographics') else ""

        demo = stats.get("demographics", {})

        genders = demo.get("genders", {})
        semesters = demo.get("semesters", {})
        careers = demo.get("careers", {})

        male_count = genders.get("Male", 0)
        female_count = genders.get("Female", 0)
        total_demo = male_count + female_count
        male_pct = (male_count / total * 100) if total else 0
        female_pct = (female_count / total * 100) if total else 0

        avg_age = demo.get("avg_age")
        min_age = demo.get("min_age")
        max_age = demo.get("max_age")
        avg_age_str = f"{avg_age:.1f}" if avg_age is not None else "N/A"
        age_range_str = f"{min_age}-{max_age}" if (min_age is not None and max_age is not None) else "N/A"

        first_choice = demo.get("first_choice", {})

        avg_career_security = demo.get("avg_career_security")
        avg_personality_fit = demo.get("avg_personality_fit")
        avg_perceived_success = demo.get("avg_perceived_success")
        avg_study_hours = demo.get("avg_study_hours")
        min_study = demo.get("min_study_hours")
        max_study = demo.get("max_study_hours")

        avg_cs_str = f"{avg_career_security:.1f}" if avg_career_security is not None else "N/A"
        avg_pf_str = f"{avg_personality_fit:.1f}" if avg_personality_fit is not None else "N/A"
        avg_ps_str = f"{avg_perceived_success:.1f}" if avg_perceived_success is not None else "N/A"
        avg_sh_str = f"{avg_study_hours:.1f}" if avg_study_hours is not None else "N/A"
        min_sh_str = str(min_study) if min_study is not None else "N/A"
        max_sh_str = str(max_study) if max_study is not None else "N/A"

        std_cs = demo.get("std_career_security")
        std_pf = demo.get("std_personality_fit")
        std_ps = demo.get("std_perceived_success")
        std_sh = demo.get("std_study_hours")

        std_cs_str = f"{std_cs:.1f}" if std_cs is not None else "N/A"
        std_pf_str = f"{std_pf:.1f}" if std_pf is not None else "N/A"
        std_ps_str = f"{std_ps:.1f}" if std_ps is not None else "N/A"
        std_sh_str = f"{std_sh:.1f}" if std_sh is not None else "N/A"

        html = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MBTI Research Report - Methodology, Results and Conclusions</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            color: #333;
            background-color: #f9f9f9;
        }
        h1 {
            border-bottom: 3px solid #333;
            padding-bottom: 10px;
            font-size: 28px;
            margin-bottom: 30px;
        }
        h2 {
            border-bottom: 2px solid #666;
            padding-bottom: 8px;
            font-size: 22px;
            margin-top: 40px;
            margin-bottom: 20px;
        }
        h3 {
            font-size: 16px;
            margin-top: 20px;
            margin-bottom: 10px;
            color: #444;
        }
        p {
            margin: 12px 0;
            text-align: justify;
        }
        ul, ol {
            margin: 12px 0 12px 30px;
        }
        li {
            margin: 8px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }
        th {
            background-color: #333;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .stat-box {
            background-color: white;
            border-left: 4px solid #333;
            padding: 15px;
            margin: 15px 0;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }
        .chart-container {
            margin: 30px 0;
            text-align: center;
        }
        .chart-container img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            padding: 10px;
            background: white;
        }
        .toc {
            background: white;
            padding: 20px;
            border-left: 4px solid #333;
            margin: 30px 0;
        }
        .toc h3 {
            margin-top: 0;
        }
        .toc ul {
            margin: 10px 0 10px 20px;
        }
        .toc a {
            color: #0066cc;
            text-decoration: none;
        }
        .toc a:hover {
            text-decoration: underline;
        }
        footer {
            margin-top: 60px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            text-align: center;
            font-size: 12px;
            color: #666;
        }
        .conclusion-box {
            background: white;
            padding: 15px;
            border-left: 4px solid #333;
            margin: 15px 0;
        }
        .highlight {
            background-color: #fffacd;
            padding: 2px 4px;
        }
    </style>
</head>
<body>

<h1>MBTI Research Report</h1>
<p><strong>Methodology, Results and Conclusions in University Students</strong></p>
<p><em>Generated: ''' + datetime.now().strftime("%B %d, %Y") + '''</em></p>

<div class="toc">
<h3>Table of Contents</h3>
<ul>
<li><a href="#methodology">Methodology</a></li>
<li><a href="#population">Population and Sample</a></li>
<li><a href="#collection">Data Collection Process</a></li>
<li><a href="#results">Results</a></li>
<li><a href="#statistics">Descriptive Statistics</a></li>
<li><a href="#conclusions">Conclusions</a></li>
</ul>
</div>

<h2 id="methodology">Methodology</h2>

<h3 id="population">Population and Sample</h3>

<p>This study analyzed university students from an educational institution, aged 19-24 years old, from various academic programs. The sample consists mainly of students in semesters 2-4, predominantly from STEM (Science, Technology, Engineering, and Mathematics) programs.</p>

<div class="stat-box">
<div class="stat-label">Sample Size</div>
<div class="stat-value">''' + str(total) + ''' Participants</div>
</div>

<div class="stat-box">
<div class="stat-label">Average Age</div>
<div class="stat-value">''' + avg_age_str + ''' Years</div>
</div>

<div class="stat-box">
<div class="stat-label">Age Range</div>
<div class="stat-value">''' + age_range_str + ''' Years</div>
</div>

<div class="stat-box">
<div class="stat-label">MBTI Types Identified</div>
<div class="stat-value">''' + str(len(self.mbti_counts)) + ''' Types</div>
</div>

<h3>Inclusion Criteria</h3>
<ul>
<li>Active students at the educational institution</li>
<li>Age between 18 and 25 years</li>
<li>Voluntary participation willingness</li>
<li>Spanish language comprehension</li>
</ul>

<h3>Sampling Method</h3>
<p>A non-probabilistic convenience sampling method was used with n = ''' + str(total) + ''' participants. The sample size allows for robust descriptive analysis of MBTI personality type distribution in the studied population.</p>

<h3 id="collection">Data Collection Process</h3>

<h3>Measurement Instrument</h3>
<p>The MBTI (Myers-Briggs Type Indicator) questionnaire was used via the mbti-pocketflow platform (Hugging Face Spaces). This is an internationally recognized psychometric predictor that evaluates personality preferences across four dimensions.</p>

<h3>Data Collection Procedure</h3>
<ol>
<li>Project presentation and informed consent explanation</li>
<li>Access to mbti-pocketflow platform to complete the questionnaire</li>
<li>Average administration time: 15-20 minutes per participant</li>
<li>Automatic response recording and MBTI profile generation</li>
<li>Collection of additional demographic information (age, gender, major, semester)</li>
</ol>

<h3>Ethical Considerations</h3>
<ul>
<li>Voluntary participation and informed consent</li>
<li>Personal data confidentiality guaranteed</li>
<li>Anonymity in final reports (identified by participant number)</li>
<li>Right to withdraw without penalty</li>
</ul>

<h2 id="results">Results</h2>

<h3 id="statistics">Descriptive Statistics</h3>

<h3>1. MBTI Type Distribution</h3>

<table>
<thead>
<tr>
<th>MBTI Type</th>
<th>Frequency</th>
<th>Percentage</th>
<th>Description</th>
</tr>
</thead>
<tbody>
'''

        for mbti_type, count in sorted_types:
            percentage = (count / total) * 100
            descriptions = {
                "ENFJ": "Protagonists - Charismatic leaders",
                "INFJ": "Advocates - Insightful and organized",
                "ENFP": "Campaigners - Enthusiastic and creative",
                "INFP": "Mediators - Idealistic and empathetic",
                "ENTJ": "Commanders - Logical and efficient",
                "INTJ": "Architects - Analytical and independent",
                "ESFJ": "Consuls - Friendly and responsible",
                "ESFP": "Entrepreneurs - Spontaneous and sociable",
                "ISFJ": "Defenders - Dedicated and loyal",
                "ISFP": "Composers - Flexible and sensitive",
                "ESTJ": "Logisticians - Organized and responsible",
                "ESTP": "Entrepreneurs - Observant and pragmatic",
                "ISTJ": "Advocates - Logical and reliable",
                "ISTP": "Virtuosos - Analytical and practical",
            }
            description = descriptions.get(mbti_type, "")
            html += f'<tr><td>{mbti_type}</td><td>{count}</td><td>{percentage:.1f}%</td><td>{description}</td></tr>\n'

        html += '''</tbody>
</table>

<div class="chart-container">
<img src="''' + dist_img + '''" alt="MBTI Type Distribution">
</div>

<h3>2. Dimensional Analysis</h3>

<div class="stat-box">
<strong>Extraversion vs Introversion</strong><br>
E: ''' + f'{e_pct:.1f}%' + ''' | I: ''' + f'{i_pct:.1f}%' + '''
</div>

<div class="stat-box">
<strong>Intuition vs Sensing</strong><br>
N: ''' + f'{n_pct:.1f}%' + ''' | S: ''' + f'{s_pct:.1f}%' + '''
</div>

<div class="stat-box">
<strong>Feeling vs Thinking</strong><br>
F: ''' + f'{f_pct:.1f}%' + ''' | T: ''' + f'{t_pct:.1f}%' + '''
</div>

<div class="stat-box">
<strong>Judging vs Perceiving</strong><br>
J: ''' + f'{j_pct:.1f}%' + ''' | P: ''' + f'{p_pct:.1f}%' + '''
</div>

<div class="chart-container">
<img src="''' + dim_img + '''" alt="Dimensional Analysis">
</div>

<h3>3. Demographic Data</h3>
'''

        if demo_img:
            html += '''
<div class="chart-container">
<img src="''' + demo_img + '''" alt="Demographic Distribution">
</div>
'''

        html += '''
<table>
<thead>
<tr>
<th>Variable</th>
<th>Category</th>
<th>Frequency</th>
<th>Percentage</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="2">Gender</td>
<td>Male</td>
<td>''' + str(male_count) + '''</td>
<td>''' + f'{male_pct:.1f}%' + '''</td>
</tr>
<tr>
<td>Female</td>
<td>''' + str(female_count) + '''</td>
<td>''' + f'{female_pct:.1f}%' + '''</td>
</tr>
</tbody>
</table>

<h3>3b. Career Distribution</h3>

<table>
<thead>
<tr>
<th>Career / Major</th>
<th>Frequency</th>
<th>Percentage</th>
</tr>
</thead>
<tbody>
'''

        for career_name, career_count in sorted(careers.items(), key=lambda x: x[1], reverse=True):
            career_pct = (career_count / total) * 100
            html += f'<tr><td>{career_name}</td><td>{career_count}</td><td>{career_pct:.1f}%</td></tr>\n'

        html += '''</tbody>
</table>

<h3>4. Academic Satisfaction Indicators</h3>

<table>
<thead>
<tr>
<th>Indicator</th>
<th>Average</th>
<th>Std Dev</th>
<th>Min</th>
<th>Max</th>
</tr>
</thead>
<tbody>
<tr>
<td>Career Choice Security</td>
<td>''' + avg_cs_str + '''</td>
<td>''' + std_cs_str + '''</td>
<td>1</td>
<td>5</td>
</tr>
<tr>
<td>Personality-Career Fit</td>
<td>''' + avg_pf_str + '''</td>
<td>''' + std_pf_str + '''</td>
<td>1</td>
<td>5</td>
</tr>
<tr>
<td>Perceived Career Success</td>
<td>''' + avg_ps_str + '''</td>
<td>''' + std_ps_str + '''</td>
<td>1</td>
<td>5</td>
</tr>
<tr>
<td>Weekly Study Hours</td>
<td>''' + avg_sh_str + '''</td>
<td>''' + std_sh_str + '''</td>
<td>''' + min_sh_str + '''</td>
<td>''' + max_sh_str + '''</td>
</tr>
</tbody>
</table>

<h2 id="conclusions">Conclusions</h2>
'''

        # IS type counts for conclusion 3
        is_count = sum(count for mtype, count in self.mbti_counts.items() if mtype.startswith('I') and len(mtype) > 1 and mtype[1] == 'S')
        is_pct = (is_count / total) * 100

        html += '''

<h3>Main Findings</h3>
<p>The analysis of ''' + str(total) + ''' university students revealed a notable distribution of MBTI personality types with significant implications for academic and vocational guidance.</p>

<h3>1. Dominance of Extraverted and Intuitive Types</h3>
<p>Objective: Identify the prevalence of personality characteristics in the studied population.</p>
<div class="conclusion-box">
<p><strong>Conclusion:</strong> ''' + f'{e_pct:.1f}%' + ''' of participants showed a preference for extraversion (E) and ''' + f'{n_pct:.1f}%' + ''' for intuition (N). This suggests that the sample consists mainly of students oriented towards social interactions, future-focused thinking and abstract reasoning. This trend is especially pronounced in STEM careers, where long-term vision and innovation are valued.</p>
</div>

<h3>2. ENFJ Type Predominance</h3>
<p>Objective: Analyze the specific distribution of MBTI types to identify leadership patterns.</p>
<div class="conclusion-box">
<p><strong>Conclusion:</strong> The ENFJ "Protagonist" type represents ''' + f'{enfj_pct:.1f}%' + ''' of the sample (n=''' + str(enfj_count) + '''), indicating a high prevalence of individuals with charismatic leadership characteristics. This type is characterized by being tolerant, reliable, charismatic, altruistic, and natural leaders. This concentration suggests that the institution is attracting and developing students with high leadership potential, particularly in academic programs that emphasize collaboration and project management.</p>
</div>

<h3>3. Low Representation of Introverted-Sensing Types</h3>
<p>Objective: Evaluate the diversity of psychological profiles in the sample.</p>
<div class="conclusion-box">
<p><strong>Conclusion:</strong> Types that combine introversion (I) with sensing (S) represent only ''' + f'{is_pct:.1f}%' + ''' of the sample (n=''' + str(is_count) + ''', IS types). This indicates low diversity in terms of analytical and detail-oriented profiles. Such profiles could be valuable in roles requiring attention to detail, thorough analysis, and careful execution of complex tasks. The institution should consider strategies to attract and retain students with these complementary profiles.</p>
</div>

<h3>4. Relationship Between Personality and Academic Satisfaction</h3>
<p>Objective: Establish connections between personality type and perceived academic success.</p>
<div class="conclusion-box">
<p><strong>Conclusion:</strong> Participants showed moderate to high confidence in their career choice (M=''' + avg_cs_str + ''') but a more moderate perception of personality-career fit (M=''' + avg_pf_str + '''). This suggests that while many students are confident in their choice, some experience friction between their personality characteristics and academic program requirements. This finding underscores the importance of vocational guidance based on personality typology.</p>
</div>

<h3>5. Vocational Guidance Implications</h3>
<p>Objective: Provide recommendations based on identified personality profiles.</p>
<div class="conclusion-box">
<p><strong>Conclusion:</strong> Results suggest that:</p>
<ul>
<li><strong>ENFJ/ENFP types:</strong> Well-suited for leadership roles, project management, education, and roles requiring social interaction. Recommended careers: administration, entrepreneurship, team management.</li>
<li><strong>INFJ/INFP types:</strong> Strong in strategic analysis, creativity, and empathy. Could excel in research, consulting, design, and specialized roles.</li>
<li><strong>ENTJ/INTJ types:</strong> Logic and strategy-oriented profiles. Ideal candidates for science, advanced engineering, and technical analysis.</li>
</ul>
</div>

<h3>6. Recommendations for the Institution</h3>
<div class="conclusion-box">
<p><strong>Strategic Recommendations:</strong></p>
<ul>
<li>Profile Diversification: Implement admission strategies that attract students with underrepresented profiles (S-T types) to enrich cognitive diversity.</li>
<li>Personalized Guidance: Design MBTI-based mentoring and vocational guidance programs to improve alignment between personal interests and academics.</li>
<li>Complementary Training: Offer skill development workshops that compensate for typical weak areas of each personality type.</li>
<li>Group Dynamics: Use MBTI typology to optimize team formation in collaborative projects, ensuring profile balance.</li>
<li>Longitudinal Follow-up: Conduct follow-up studies to correlate MBTI types with academic performance, retention, and professional success.</li>
</ul>
</div>

<h3>7. Study Limitations</h3>
<div class="conclusion-box">
<p><strong>Methodological Considerations:</strong></p>
<ul>
<li>Non-probabilistic convenience sample, limiting generalization to other populations.</li>
<li>Cross-sectional design - does not allow establishing causality in observed relationships.</li>
<li>Dependence on self-report in academic satisfaction variables.</li>
<li>Lack of control group for reference comparisons.</li>
<li>Potential bias towards STEM program students at the institution.</li>
</ul>
</div>

<h3>Final Conclusion</h3>
<div class="conclusion-box">
<p>This study provides clear evidence that MBTI personality types are non-uniformly distributed in the studied population, with a marked preponderance of extraverted, intuitive, feeling, and judging types (ENFJ). These findings have significant practical implications for vocational guidance, team formation, and the design of educational programs that maximize student success and satisfaction.</p>

<p>These results should serve as the basis for future research examining the relationship between personality typology and factors such as academic performance, career satisfaction, and long-term professional trajectory.</p>
</div>

<footer>
<p>MBTI Research Report - University Students</p>
<p>Data analyzed: ''' + str(total) + ''' participants</p>
<p>Period: May 2026</p>
</footer>

</body>
</html>
'''

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"Report generated: {output_path}")

    def generate_report(self, output_path: str):
        """Generate the complete report."""
        print("\nGenerating MBTI Research Report (Simple)...\n")

        self.extract_mbti_reports()
        stats = self.calculate_statistics()

        print(f"Calculated statistics: {len(self.mbti_counts)} MBTI types")
        for mbti_type, count in sorted(self.mbti_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {mbti_type}: {count} ({(count/stats['total']*100):.1f}%)")
        print()

        charts = self.create_chart_images(stats)
        self.generate_html(stats, charts, output_path)

        print(f"\nDone! Report saved to: {output_path}")


def main():
    """Main execution."""
    generator = MBTISimpleReportGenerator(reports_dir="./input", conclusions_dir="./conclusions")
    generator.generate_report(output_path="./conclusions/report.html")


if __name__ == "__main__":
    main()
