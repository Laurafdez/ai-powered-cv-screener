import os
import json
import boto3
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from PIL import Image as PILImage
import random
import logging
import requests
from config.settings import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BEDROCK_MODEL

# ===== AWS CREDENTIAL CONFIGURATION =====
os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
os.environ['AWS_DEFAULT_REGION'] = AWS_REGION

# ===== CONFIGURATION =====
NOVA_MODEL = BEDROCK_MODEL

# AWS Bedrock client
bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_REGION)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load profiles from a JSON file
def load_profiles_json(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

# -------------------- Photo Generation --------------------
def generate_ai_photo(cv_number, gender=None):
    """Generates a professional photo using a free external API."""
    try:
        logger.info(f"Generating photo #{cv_number} with AI...")
        response = requests.get(
            'https://thispersondoesnotexist.com/',
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=10
        )
        if response.status_code == 200:
            photo_path = f'generated_cvs/photo_{cv_number}.png'
            os.makedirs('generated_cvs', exist_ok=True)
            image = PILImage.open(BytesIO(response.content))
            image = image.resize((150, 150), PILImage.Resampling.LANCZOS)
            image.save(photo_path)
            logger.info(f"Photo generated: {photo_path}")
            return photo_path
        else:
            return generate_placeholder_photo(cv_number)
    except Exception as e:
        logger.warning(f"Could not generate AI photo: {e}. Using placeholder.")
        return generate_placeholder_photo(cv_number)

def generate_placeholder_photo(cv_number):
    """Generates a professional style avatar."""
    try:
        seed = f"cv{cv_number}{random.randint(1000, 9999)}"
        styles = ['avataaars', 'bottts', 'personas', 'lorelei', 'notionists']
        style = random.choice(styles)
        url = f'https://api.dicebear.com/7.x/{style}/png?seed={seed}&size=150'
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            photo_path = f'generated_cvs/photo_{cv_number}.png'
            with open(photo_path, 'wb') as f:
                f.write(response.content)
            return photo_path
    except:
        pass
    from PIL import ImageDraw
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    background_color = random.choice(colors)
    img = PILImage.new('RGB', (150, 150), background_color)
    draw = ImageDraw.Draw(img)
    draw.ellipse([40, 30, 110, 100], fill='white')
    draw.ellipse([60, 90, 90, 130], fill='white')
    photo_path = f'generated_cvs/photo_{cv_number}.png'
    img.save(photo_path)
    return photo_path

# -------------------- Content Generation with Nova --------------------
def generate_cv_content_with_nova(profile, language='en'):
    """Generates CV content using Amazon Nova Pro, adapted to the profile from the JSON."""
    try:
        name = profile['name']
        role = profile['role']
        level = profile['level']
        
        # Use the profile to create the prompt
        prompt = f"""Generate a complete and realistic CV content in {language}.
Return ONLY a valid JSON object (no markdown, no code blocks, just pure JSON):

{{
  "name": "{name}",
  "email": "professional.email@company.com",
  "phone": "phone with country code",
  "address": "Complete address with city and country",
  "linkedin": "linkedin.com/in/{name.replace(' ', '-').lower()}",
  "summary": "Professional summary for a {role} at {level} level.",
  "experience": [
    {{
      "position": "{role}",
      "company": "Company X",
      "start": "01/2015",
      "end": "Present",
      "description": "Responsible for leading security efforts."
    }}
  ],
  "education": [
    {{
      "degree": "PhD in {role}",
      "university": "University X",
      "year": "2013",
      "specialty": "Computer Science"
    }}
  ],
  "skills": ["Skill1", "Skill2", "Skill3", "Skill4", "Skill5"],
  "languages": [
    {{"language": "English", "level": "Fluent"}}
  ],
  "certifications": ["Cert 1", "Cert 2"]
}}

Requirements:
- Use the provided name, role, and level in the CV content. You can invent details but keep them realistic.
- Ensure the JSON is well-formed and can be parsed without errors.
- The CV should reflect a professional with experience in the specified role and level.
- Invent Company and university names; avoid using placeholders like Company X. Use names such as Apple, Tesla, or universities like UPC, UPM, Harvard, Stanford.
"""

        body = json.dumps({
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {"max_new_tokens": 3000, "temperature": 1, "top_p": 0.95}
        })

        logger.info(f"Calling Amazon Nova Pro EU to generate CV for {name}...")
        response = bedrock_runtime.invoke_model(
            modelId=NOVA_MODEL,
            body=body,
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response['body'].read())
        logger.info(f"API response: {response_body}")

        content_text = response_body['output']['message']['content'][0]['text'].strip()
        
        # Clean up any code block markers
        if content_text.startswith('```'):
            content_text = content_text.strip('`').strip()
        cv_data = json.loads(content_text)
        return cv_data

    except Exception as e:
        logger.error(f"Error generating content with Nova Pro: {e}")
        raise

# -------------------- JSON Normalization --------------------
def normalize_cv(cv_data):
    """Ensures that all required keys exist and are lists/strings."""
    defaults = {
        "name": "Full Name",
        "email": "email@company.com",
        "phone": "+00 000000000",
        "address": "City, Country",
        "linkedin": "linkedin.com/in/user",
        "summary": "Professional summary not provided.",
        "experience": [],
        "education": [],
        "skills": [],
        "languages": [],
        "certifications": []
    }

    for key, default in defaults.items():
        if key not in cv_data or cv_data[key] is None:
            cv_data[key] = default

    # Convert descriptions to text
    for exp in cv_data.get('experience', []):
        desc = exp.get('description', '')
        if isinstance(desc, list):
            exp['description'] = "\n".join([f"• {d}" for d in desc])
        else:
            exp['description'] = str(desc)
    return cv_data

# -------------------- PDF Creation --------------------
def create_cv_pdf(cv_number, profile, language='en'):
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"Generating CV #{cv_number} for {profile['name']} in {language.upper()}...")
        logger.info(f"{'='*60}")

        cv_data = generate_cv_content_with_nova(profile, language)
        cv_data = normalize_cv(cv_data)
        photo_path = generate_ai_photo(cv_number)

        clean_name = cv_data.get("name", "Full_Name").replace(" ", "_").replace("/", "-")
        file_name = f'generated_cvs/CV_{cv_number:03d}_{clean_name}.pdf'

        doc = SimpleDocTemplate(file_name, pagesize=A4,
                                leftMargin=0.75*inch, rightMargin=0.75*inch,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)

        elements = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=26,
                                       textColor=colors.HexColor('#1a1a1a'), spaceAfter=8,
                                       alignment=1, fontName='Helvetica-Bold')
        section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=13,
                                        textColor=colors.HexColor('#2c3e50'), spaceAfter=8,
                                        spaceBefore=16, fontName='Helvetica-Bold')
        subsection_style = ParagraphStyle('Subsection', parent=styles['Heading3'], fontSize=11,
                                           textColor=colors.HexColor('#34495e'), spaceAfter=2,
                                           fontName='Helvetica-Bold')
        normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10,
                                      leading=13, textColor=colors.HexColor('#2c3e50'))

        # Photo
        if os.path.exists(photo_path):
            img = Image(photo_path, width=1.2*inch, height=1.2*inch)
            elements.append(img)
            elements.append(Spacer(1, 10))

        # Name
        elements.append(Paragraph(cv_data.get('name'), title_style))
        elements.append(Spacer(1, 2))

        # Contact info
        contact = f"""
        <b>Email:</b> {cv_data.get('email')} | <b>Phone:</b> {cv_data.get('phone')}<br/>
        <b>Address:</b> {cv_data.get('address')}<br/>
        <b>LinkedIn:</b> {cv_data.get('linkedin')}
        """
        elements.append(Paragraph(contact, normal_style))
        elements.append(Spacer(1, 16))

        # Titles based on language
        titles = {
            'en': {'summary': 'PROFESSIONAL SUMMARY', 'experience': 'WORK EXPERIENCE',
                   'education': 'EDUCATION', 'skills': 'SKILLS',
                   'languages': 'LANGUAGES', 'certifications': 'CERTIFICATIONS'},
            'es': {'summary': 'RESUMEN PROFESIONAL', 'experience': 'EXPERIENCIA LABORAL',
                   'education': 'EDUCACIÓN', 'skills': 'HABILIDADES',
                   'languages': 'IDIOMAS', 'certifications': 'CERTIFICACIONES'}
        }
        t = titles.get(language, titles['en'])

        # Summary
        elements.append(Paragraph(t['summary'], section_style))
        elements.append(Paragraph(cv_data.get('summary'), normal_style))
        elements.append(Spacer(1, 12))

        # Experience
        elements.append(Paragraph(t['experience'], section_style))
        for exp in cv_data.get('experience', []):
            elements.append(Paragraph(f"<b>{exp.get('position')}</b> | {exp.get('company')}", subsection_style))
            elements.append(Paragraph(f"<i>{exp.get('start')} - {exp.get('end')}</i>", normal_style))
            elements.append(Spacer(1, 4))
            elements.append(Paragraph(exp.get('description'), normal_style))
            elements.append(Spacer(1, 10))

        # Education
        elements.append(Paragraph(t['education'], section_style))
        for edu in cv_data.get('education', []):
            edu_title = f"<b>{edu.get('degree')}</b>"
            if edu.get('specialty'):
                edu_title += f" | {edu.get('specialty')}"
            elements.append(Paragraph(edu_title, subsection_style))
            elements.append(Paragraph(f"{edu.get('university')} | {edu.get('year')}", normal_style))
            elements.append(Spacer(1, 8))

        # Skills
        elements.append(Paragraph(t['skills'], section_style))
        skills_text = " • ".join(cv_data.get('skills', []))
        elements.append(Paragraph(skills_text, normal_style))
        elements.append(Spacer(1, 10))

        # Languages
        if cv_data.get('languages'):
            elements.append(Paragraph(t['languages'], section_style))
            languages_text = " | ".join([f"<b>{lang.get('language')}</b>: {lang.get('level')}" for lang in cv_data['languages']])
            elements.append(Paragraph(languages_text, normal_style))
            elements.append(Spacer(1, 10))

        # Certifications
        if cv_data.get('certifications'):
            elements.append(Paragraph(t['certifications'], section_style))
            cert_text = " • ".join(cv_data['certifications'])
            elements.append(Paragraph(cert_text, normal_style))

        # Build PDF
        doc.build(elements)
        logger.info(f"CV #{cv_number} completed: {file_name}")
        return file_name
    except Exception as e:
        logger.error(f"Error generating CV #{cv_number}: {e}")
        raise

# -------------------- Batch Generation --------------------
def generate_cvs_batch(count=1, languages=['en'], profiles_json_path="profiles.json"):
    print(f"\n{'='*70}")
    print(f"🚀 AI CV GENERATOR")
    print(f"{'='*70}")
    print(f"📍 AWS Region: {AWS_REGION}")
    print(f"🤖 Model: Amazon Nova Pro (EU)")
    print(f"📊 Count: {count} CVs")
    print(f"🌍 Languages: {', '.join([i.upper() for i in languages])}")
    print(f"{'='*70}\n")

    os.makedirs('generated_cvs', exist_ok=True)
    successes, failures = [], []

    profiles = load_profiles_json(profiles_json_path)

    for i, profile in enumerate(profiles[:count], 1):
        try:
            language = random.choice(languages)
            file = create_cv_pdf(i, profile, language)
            successes.append(file)
            print(f"✓ Progress: {i}/{count} | ✅ {len(successes)} | ❌ {len(failures)}")
        except Exception as e:
            logger.error(f"Error in CV #{i}: {str(e)[:100]}")
            failures.append(i)
            print(f"✗ Progress: {i}/{count} | ✅ {len(successes)} | ❌ {len(failures)}")

    print(f"\n{'='*70}")
    print(f"📊 FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Successful CVs: {len(successes)}/{count} ({len(successes)/count*100:.1f}%)")
    print(f"❌ Failed CVs: {len(failures)}/{count}")
    if failures:
        print(f"   Failed numbers: {failures}")
    print(f"📁 Folder: generated_cvs/")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    generate_cvs_batch(count=2, languages=['en'])
