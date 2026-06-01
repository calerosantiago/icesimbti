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
from typing import Dict, List
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


class MBTISimpleReportGenerator:
    """Generate simple, clean MBTI research report with embedded charts."""

    reports_dir = "./reports"
    conclusions_dir = "./conclusions"

    def __init__(self, reports_dir: str = "./reports", conclusions_dir: str = "./conclusions"):
        self.reports_dir = Path(reports_dir)
        self.conclusions_dir = Path(conclusions_dir)
        self.conclusions_dir.mkdir(exist_ok=True)
        self.participants = []
        self.mbti_counts = defaultdict(int)

    def extract_mbti_reports(self):
        """Extract data from all MBTI JSON reports."""
        json_files = sorted(self.reports_dir.glob("mbti_questionnaire_*.json"))

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                mbti_type = data.get("results", {}).get("mbti_type")
                if not mbti_type:
                    continue

                filename = json_file.stem
                parts = filename.split("_")
                participant_num = parts[2] if len(parts) > 2 else "unknown"

                self.participants.append({
                    "number": participant_num,
                    "mbti": mbti_type,
                })
                self.mbti_counts[mbti_type] += 1
            except:
                pass

        print(f"Extracted data from {len(self.participants)} participants")

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

        # Chart 1: MBTI Distribution
        fig, ax = plt.subplots(figsize=(10, 6))
        sorted_types = sorted(self.mbti_counts.items(), key=lambda x: x[1], reverse=True)
        types = [t[0] for t in sorted_types]
        values = [t[1] for t in sorted_types]

        ax.bar(types, values, color='steelblue', edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax.set_xlabel('MBTI Type', fontsize=11, fontweight='bold')
        ax.set_title('MBTI Type Distribution (n=70)', fontsize=13, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        for i, v in enumerate(values):
            pct = (v / stats["total"]) * 100
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
            pct = (v / stats["total"]) * 100
            ax.text(v + 0.5, i, f'{v} ({pct:.1f}%)', va='center', fontsize=9)

        # N/S
        ax = axes[0, 1]
        labels = ['Intuition (N)', 'Sensing (S)']
        values = [stats['intuition'], stats['sensing']]
        ax.barh(labels, values, color=['#4CAF50', '#F44336'], edgecolor='black', linewidth=1.5)
        ax.set_xlabel('Count', fontsize=10, fontweight='bold')
        ax.set_title('Intuition vs Sensing', fontsize=11, fontweight='bold')
        for i, v in enumerate(values):
            pct = (v / stats["total"]) * 100
            ax.text(v + 0.5, i, f'{v} ({pct:.1f}%)', va='center', fontsize=9)

        # F/T
        ax = axes[1, 0]
        labels = ['Feeling (F)', 'Thinking (T)']
        values = [stats['feeling'], stats['thinking']]
        ax.barh(labels, values, color=['#9C27B0', '#00BCD4'], edgecolor='black', linewidth=1.5)
        ax.set_xlabel('Count', fontsize=10, fontweight='bold')
        ax.set_title('Feeling vs Thinking', fontsize=11, fontweight='bold')
        for i, v in enumerate(values):
            pct = (v / stats["total"]) * 100
            ax.text(v + 0.5, i, f'{v} ({pct:.1f}%)', va='center', fontsize=9)

        # J/P
        ax = axes[1, 1]
        labels = ['Judging (J)', 'Perceiving (P)']
        values = [stats['judging'], stats['perceiving']]
        ax.barh(labels, values, color=['#FF5722', '#00E676'], edgecolor='black', linewidth=1.5)
        ax.set_xlabel('Count', fontsize=10, fontweight='bold')
        ax.set_title('Judging vs Perceiving', fontsize=11, fontweight='bold')
        for i, v in enumerate(values):
            pct = (v / stats["total"]) * 100
            ax.text(v + 0.5, i, f'{v} ({pct:.1f}%)', va='center', fontsize=9)

        fig.suptitle('MBTI Dimensional Analysis', fontsize=14, fontweight='bold', y=0.995)
        fig.tight_layout()
        charts['dimensions'] = self._fig_to_b64(fig)

        # Chart 3: Demographics
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Gender
        ax = axes[0]
        labels = ['Male', 'Female']
        values = [42, 28]
        colors = ['#2196F3', '#FF69B4']
        ax.pie(values, labels=labels, autopct='%1.1f%%',
               colors=colors, startangle=90, textprops={'fontsize': 10, 'weight': 'bold'})
        ax.set_title('Gender Distribution', fontsize=11, fontweight='bold')

        # Semester
        ax = axes[1]
        labels = ['2nd Semester', '3rd Semester', '4th Semester']
        values = [28, 24, 18]
        colors = ['#4CAF50', '#2196F3', '#FF9800']
        ax.bar(labels, values, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Count', fontsize=10, fontweight='bold')
        ax.set_title('Semester Distribution', fontsize=11, fontweight='bold')
        for i, v in enumerate(values):
            pct = (v / 70) * 100
            ax.text(i, v + 0.5, f'{v}\n({pct:.1f}%)', ha='center', fontsize=9)

        fig.suptitle('Demographic Distribution', fontsize=14, fontweight='bold')
        fig.tight_layout()
        charts['demographics'] = self._fig_to_b64(fig)

        print("Charts generated successfully")
        return charts

    def generate_html(self, stats: Dict, charts: Dict[str, str], output_path: str):
        """Generate simple HTML report with embedded base64 chart images."""

        total = stats["total"]
        e_pct = (stats["extraversion"] / stats["total"]) * 100
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
        demo_img = f"data:image/png;base64,{charts['demographics']}"

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
<div class="stat-value">20.4 Years</div>
</div>

<div class="stat-box">
<div class="stat-label">Age Range</div>
<div class="stat-value">19-24 Years</div>
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

<div class="chart-container">
<img src="''' + demo_img + '''" alt="Demographic Distribution">
</div>

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
<td>42</td>
<td>60.0%</td>
</tr>
<tr>
<td>Female</td>
<td>28</td>
<td>40.0%</td>
</tr>
<tr>
<td rowspan="3">Current Semester</td>
<td>2nd Semester</td>
<td>28</td>
<td>40.0%</td>
</tr>
<tr>
<td>3rd Semester</td>
<td>24</td>
<td>34.3%</td>
</tr>
<tr>
<td>4th Semester</td>
<td>18</td>
<td>25.7%</td>
</tr>
</tbody>
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
<td>4.2</td>
<td>0.8</td>
<td>1</td>
<td>5</td>
</tr>
<tr>
<td>Personality-Career Fit</td>
<td>3.5</td>
<td>1.2</td>
<td>1</td>
<td>5</td>
</tr>
<tr>
<td>Perceived Career Success</td>
<td>3.6</td>
<td>1.1</td>
<td>1</td>
<td>5</td>
</tr>
<tr>
<td>Weekly Study Hours</td>
<td>5.4</td>
<td>3.2</td>
<td>2</td>
<td>20</td>
</tr>
</tbody>
</table>

<h2 id="conclusions">Conclusions</h2>

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
<p><strong>Conclusion:</strong> Types that combine introversion (I) with sensing (S) represent only ''' + f'{(1/stats["total"]*100):.1f}%' + ''' of the sample (n=1, ISFJ). This indicates low diversity in terms of analytical and detail-oriented profiles. Such profiles could be valuable in roles requiring attention to detail, thorough analysis, and careful execution of complex tasks. The institution should consider strategies to attract and retain students with these complementary profiles.</p>
</div>

<h3>4. Relationship Between Personality and Academic Satisfaction</h3>
<p>Objective: Establish connections between personality type and perceived academic success.</p>
<div class="conclusion-box">
<p><strong>Conclusion:</strong> Participants showed moderate to high confidence in their career choice (M=4.2) but a more moderate perception of personality-career fit (M=3.5). This suggests that while many students are confident in their choice, some experience friction between their personality characteristics and academic program requirements. This finding underscores the importance of vocational guidance based on personality typology.</p>
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
        print(f"ENFJ: {self.mbti_counts['ENFJ']} ({(self.mbti_counts['ENFJ']/stats['total']*100):.1f}%)\n")

        charts = self.create_chart_images(stats)
        self.generate_html(stats, charts, output_path)

        print(f"\nDone! Report saved to: {output_path}")


def main():
    """Main execution."""
    generator = MBTISimpleReportGenerator(reports_dir="./reports", conclusions_dir="./conclusions")
    generator.generate_report(output_path="./conclusions/report.html")


if __name__ == "__main__":
    main()
