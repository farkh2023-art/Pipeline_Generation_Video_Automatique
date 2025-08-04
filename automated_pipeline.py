"""
Pipeline d'automatisation complet pour création de cours interactifs
Input (transcription/texte) → Claude API → Template Engine → HTML responsive
"""

import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# ================== ÉTAPE 1: STRUCTURES DE DONNÉES ==================

@dataclass
class Section:
    id: str
    title: str
    content: str
    timestamp: Optional[str] = None

@dataclass
class Chapter:
    id: str
    title: str
    title_short: str
    timestamp: str
    sections: List[Section]
    introduction: str = ""
    conclusion: str = ""

@dataclass
class Course:
    title: str
    subtitle: str
    language: str
    chapters: List[Chapter]
    total_duration: str = ""
    metadata: Dict = None

# ================== ÉTAPE 2: CLAUDE API INTEGRATION ==================

class ClaudeProcessor:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
        
    async def analyze_structure(self, transcript: str, target_language: str = "fr") -> Course:
        """Analyser la transcription et extraire la structure"""
        
        prompt = f"""
        Analysez cette transcription et structurez-la en cours interactif.

        INSTRUCTIONS CRITIQUES:
        1. Identifiez automatiquement les chapitres principaux
        2. Extrayez les sections de chaque chapitre
        3. Créez des timestamps si présents
        4. Traduisez vers {target_language} si nécessaire
        5. Répondez UNIQUEMENT en JSON valide

        FORMAT JSON REQUIS:
        {{
            "title": "Titre principal du cours",
            "subtitle": "Sous-titre descriptif", 
            "language": "{target_language}",
            "total_duration": "1:35:26",
            "chapters": [
                {{
                    "id": "chapter-0",
                    "title": "Titre complet du chapitre",
                    "title_short": "Titre court (max 30 char)",
                    "timestamp": "00:02 - 08:11",
                    "introduction": "Introduction du chapitre",
                    "sections": [
                        {{
                            "id": "ch1-section1",
                            "title": "Titre de section",
                            "content": "Contenu détaillé en HTML avec <h4>, <p>, <ul>, <div class=\'example-box\'>",
                            "timestamp": "00:02"
                        }}
                    ],
                    "conclusion": "Conclusion du chapitre"
                }}
            ]
        }}

        TRANSCRIPTION:
        {transcript[:8000]}...
        """
        
        async with httpx.AsyncClient(timeout=120.0) as client: # Increased timeout to 120 seconds
            response = await client.post(
                self.base_url,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 4000,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            
        result = response.json()
        # print(f"DEBUG: Claude API raw response: {result}") # Removed debug print
        content = result["content"][0]["text"]
        
        # Nettoyer et parser le JSON
        json_content = self._extract_json(content)
        course_data = json.loads(json_content)
        
        return self._build_course_object(course_data)
    
    def _extract_json(self, content: str) -> str:
        """Extraire JSON propre du contenu Claude"""
        # Retirer les markdown backticks si présents
        content = re.sub(r'```json\\s*', '', content)
        content = re.sub(r'```\\s*$', '', content)
        
        # Trouver le JSON valide
        start = content.find('{')
        end = content.rfind('}') + 1
        
        if start != -1 and end != -1:
            return content[start:end]
        
        raise ValueError("JSON valide non trouvé dans la réponse Claude")
    
    def _build_course_object(self, data: Dict) -> Course:
        """Construire l'objet Course à partir des données JSON"""
        chapters = []
        
        for ch_data in data.get("chapters", []):
            sections = []
            
            for sec_data in ch_data.get("sections", []):
                section = Section(
                    id=sec_data["id"],
                    title=sec_data["title"],
                    content=sec_data["content"],
                    timestamp=sec_data.get("timestamp")
                )
                sections.append(section)
            
            chapter = Chapter(
                id=ch_data["id"],
                title=ch_data["title"],
                title_short=ch_data.get("title_short", ch_data["title"][:30]),
                timestamp=ch_data.get("timestamp", ""),
                sections=sections,
                introduction=ch_data.get("introduction", ""),
                conclusion=ch_data.get("conclusion", "")
            )
            chapters.append(chapter)
        
        return Course(
            title=data["title"],
            subtitle=data["subtitle"],
            language=data["language"],
            chapters=chapters,
            total_duration=data.get("total_duration", ""),
            metadata=data.get("metadata", {})
        )

# ================== ÉTAPE 3: TEMPLATE ENGINE ==================

class CourseTemplateEngine:
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=True
        )
        
        # Créer les templates par défaut
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Créer les templates par défaut"""
        self.templates_dir.mkdir(exist_ok=True)
        
        # Template principal
        main_template = '''<!DOCTYPE html>
<html lang="{{ course.language }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ course.title }}</title>
    <style>{{ css_content }}</style>
</head>
<body>
    <nav class="top-nav">
        <div class="nav-container">
            <div class="nav-header">
                <div class="nav-title">{{ course.title }} - Sommaire</div>
                <button class="nav-toggle" onclick="toggleNav()">☰</button>
            </div>
            <div class="chapters-nav" id="chaptersNav">
                {% for chapter in course.chapters %}
                <div class="chapter-item">
                    <div class="chapter-header" onclick="toggleChapter({{ loop.index0 }})">
                        <span class="chapter-title-short">{{ loop.index }}. {{ chapter.title_short }}</span>
                        <span class="chapter-arrow">▼</span>
                    </div>
                    <div class="chapter-content">
                        {% for section in chapter.sections %}
                        <a href="#{{ section.id }}" class="section-link">{{ section.title }}</a>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="header">
            <h1>{{ course.title }}</h1>
            <p>{{ course.subtitle }}</p>
            <div class="progress-bar">
                <div class="progress" id="progressBar"></div>
            </div>
        </div>

        {% for chapter in course.chapters %}
        <div class="content {% if loop.first %}active{% endif %}" id="{{ chapter.id }}">
            <h2>{{ chapter.title }}</h2>
            
            {% if chapter.introduction %}
            <div class="chapter-intro">{{ chapter.introduction|safe }}</div>
            {% endif %}
            
            {% for section in chapter.sections %}
            <div id="{{ section.id }}">
                <h3>{{ section.title }}</h3>
                {{ section.content|safe }}
            </div>
            {% endfor %}
            
            {% if chapter.conclusion %}
            <div class="chapter-conclusion">{{ chapter.conclusion|safe }}</div>
            {% endif %}
            
            <div class="navigation-buttons">
                <button class="nav-btn" onclick="previousChapter()" 
                        {% if loop.first %}disabled{% endif %}>Précédent</button>
                <button class="nav-btn" onclick="nextChapter()" 
                        {% if loop.last %}disabled{% endif %}>
                    {% if loop.last %}Fin{% else %}Suivant{% endif %}
                </button>
            </div>
        </div>
        {% endfor %}
    </div>

    <button class="back-to-top" id="backToTop" onclick="scrollToTop()">↑</button>
    <script>{{ js_content }}</script>
</body>
</html>'''
        
        (self.templates_dir / "course.html").write_text(main_template)
    
    def render_course(self, course: Course, theme: str = "default") -> str:
        """Rendre le cours en HTML complet"""
        
        # Charger CSS et JS
        css_content = self._load_theme_css(theme)
        js_content = self._load_course_js()
        
        template = self.env.get_template("course.html")
        
        return template.render(
            course=course,
            css_content=css_content,
            js_content=js_content
        )
    
    def _load_theme_css(self, theme: str) -> str:
        """Charger le CSS du thème"""
        css_file = self.templates_dir / f"themes/{theme}.css"
        
        if not css_file.exists():
            # CSS par défaut (repris de l'artefact)
            return '''
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6; color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; padding-top: 60px; transition: padding-top 0.3s ease;
            }
            body.nav-expanded { padding-top: 280px; }
            .top-nav {
                position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
                background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(15px);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            }
            /* ... reste du CSS ... */
            '''
        
        return css_file.read_text()
    
    def _load_course_js(self) -> str:
        """Charger le JavaScript du cours"""
        js_file = self.templates_dir / "course.js"
        
        if not js_file.exists():
            # JavaScript par défaut (repris de l'artefact)
            return '''
            let currentChapter = 0;
            const totalChapters = document.querySelectorAll('.content').length;
            let navExpanded = false;
            
            function toggleNav() { /* ... */ }
            function showChapter(index) { /* ... */ }
            function nextChapter() { /* ... */ }
            function previousChapter() { /* ... */ }
            // ... reste du JS ...
            '''
        
        return js_file.read_text()

# ================== ÉTAPE 4: PIPELINE PRINCIPAL ==================

class CourseAutomationPipeline:
    def __init__(self, claude_api_key: str, templates_dir: str = "templates"):
        self.claude = ClaudeProcessor(claude_api_key)
        self.template_engine = CourseTemplateEngine(templates_dir)
    
    async def process_transcript(
        self, 
        transcript: str, 
        target_language: str = "fr",
        theme: str = "default",
        output_file: str = None
    ) -> str:
        """Pipeline complet : Transcription → HTML"""
        
        print("🔄 Étape 1: Analyse et structuration avec Claude...")
        course = await self.claude.analyze_structure(transcript, target_language)
        
        print("🔄 Étape 2: Génération du template...")
        html_content = self.template_engine.render_course(course, theme)
        
        print("🔄 Étape 3: Finalisation...")
        
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(html_content, encoding="utf-8")
            print(f"✅ Cours généré: {output_path.absolute()}")
        
        return html_content
    
    def create_course_from_url(self, video_url: str, **kwargs):
        """Créer un cours à partir d'une URL YouTube (nécessite youtube-transcript-api)"""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            import re
            
            # Extraire l'ID vidéo
            video_id_match = re.search(r'(?:v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})', video_url)
            if not video_id_match:
                raise ValueError("Impossible d'extraire l'ID vidéo de l'URL YouTube.")
            video_id = video_id_match.group(1)
            
            # Récupérer la transcription
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = ''
            for t in transcript_list:
                if t.language_code == 'fr': # Prioriser le français
                    transcript = ' '.join([item['text'] for item in t.fetch()])
                    break
            if not transcript:
                # Si pas de français, prendre la première disponible
                transcript = ' '.join([item['text'] for item in transcript_list.find_transcript(['en', 'ar']).fetch()])

            return asyncio.run(self.process_transcript(transcript, **kwargs))
            
        except ImportError:
            print("❌ Installez youtube-transcript-api: pip install youtube-transcript-api")
        except Exception as e:
            print(f"❌ Erreur: {e}")

# ================== ÉTAPE 5: UTILISATION ==================

async def main():
    """Exemple d'utilisation du pipeline"""
    
    # Configuration
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
    if not CLAUDE_API_KEY:
        print("❌ CLAUDE_API_KEY non trouvée. Assurez-vous qu'elle est définie dans .env ou comme variable d'environnement.")
        return

    # Initialiser le pipeline
    pipeline = CourseAutomationPipeline(CLAUDE_API_KEY)
    
    # Transcription fournie par l'utilisateur
    with open("IA_chang_en_3ans.txt", "r", encoding="utf-8") as f:
        user_transcript = f.read()

    try:
        print(f"🚀 Génération du cours à partir de la transcription fournie.")
        html_result = await pipeline.process_transcript(
            transcript=user_transcript,
            target_language="fr",
            theme="default",
            output_file="output/cours_generes/ia_change_en_3ans_course.html"
        )
        
        print("🎉 Pipeline terminé avec succès!")
        # Vous pouvez ajouter ici la logique pour obtenir le rapport d'utilisation si nécessaire
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du cours: {e}")
        import traceback
        traceback.print_exc()

# Configuration pour différents cas d'usage
LANGUAGE_CONFIGS = {
    "fr": {"direction": "ltr", "font": "Segoe UI"},
    "ar": {"direction": "rtl", "font": "Cairo"},
    "en": {"direction": "ltr", "font": "Inter"},
    "es": {"direction": "ltr", "font": "Segoe UI"}
}

THEME_CONFIGS = {
    "default": {"primary": "#667eea", "secondary": "#764ba2"},
    "corporate": {"primary": "#2c3e50", "secondary": "#3498db"},
    "academic": {"primary": "#8e44ad", "secondary": "#9b59b6"},
    "tech": {"primary": "#1abc9c", "secondary": "#16a085"}
}

if __name__ == "__main__":
    asyncio.run(main())




