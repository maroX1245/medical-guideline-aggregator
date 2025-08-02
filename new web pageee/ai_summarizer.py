import openai
import logging
import os
from typing import List, Optional
import json

logger = logging.getLogger(__name__)

class AISummarizer:
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai.api_key = api_key
            self.client = openai.OpenAI(api_key=api_key)
            self.enabled = True
        else:
            logger.warning("OpenAI API key not found. AI summarization will be disabled.")
            self.enabled = False
            self.client = None
    
    def summarize_guideline(self, title: str, content: str = "") -> str:
        """
        Generate a concise summary of a medical guideline using AI
        
        Args:
            title: The title of the guideline
            content: The content/description of the guideline
            
        Returns:
            A 3-5 bullet point summary of the guideline
        """
        if not self.enabled:
            return self._generate_fallback_summary(title, content)
        
        try:
            prompt = f"""
            You are a medical professional tasked with summarizing clinical practice guidelines.
            
            Please provide a concise, clinical summary of the following medical guideline in 3-5 bullet points:
            
            Title: {title}
            Content: {content[:1000] if content else title}
            
            Format your response as bullet points focusing on:
            - Key clinical recommendations
            - Target patient population
            - Important clinical outcomes
            - Any significant changes from previous guidelines
            
            Keep each bullet point concise and clinically relevant.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical professional expert in clinical practice guidelines."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated AI summary for: {title[:50]}...")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            return self._generate_fallback_summary(title, content)
    
    def extract_tags(self, title: str, content: str = "") -> List[str]:
        """
        Extract relevant medical tags/keywords from a guideline
        
        Args:
            title: The title of the guideline
            content: The content/description of the guideline
            
        Returns:
            List of relevant medical tags
        """
        if not self.enabled:
            return self._extract_fallback_tags(title, content)
        
        try:
            prompt = f"""
            You are a medical professional tasked with extracting relevant tags from clinical guidelines.
            
            Please extract 5-8 relevant medical tags/keywords from the following guideline:
            
            Title: {title}
            Content: {content[:500] if content else title}
            
            Focus on:
            - Medical specialties (e.g., Cardiology, Endocrinology, Infectious Disease)
            - Conditions (e.g., Diabetes, Hypertension, Sepsis)
            - Procedures (e.g., Screening, Treatment, Prevention)
            - Patient populations (e.g., Pediatrics, Geriatrics, Pregnant Women)
            
            Return only the tags as a comma-separated list, no explanations.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical professional expert in clinical practice guidelines."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.2
            )
            
            tags_text = response.choices[0].message.content.strip()
            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
            
            logger.info(f"Extracted tags for {title[:50]}...: {tags}")
            return tags
            
        except Exception as e:
            logger.error(f"Error extracting AI tags: {e}")
            return self._extract_fallback_tags(title, content)
    
    def _generate_fallback_summary(self, title: str, content: str = "") -> str:
        """
        Generate a fallback summary when AI is not available
        """
        # Extract key information from title
        title_lower = title.lower()
        
        summary_points = []
        
        # Identify medical specialties
        specialties = {
            'cardiology': 'Cardiovascular health guidelines',
            'diabetes': 'Diabetes management recommendations',
            'hypertension': 'Blood pressure management protocols',
            'infectious': 'Infectious disease treatment guidelines',
            'pediatric': 'Pediatric care recommendations',
            'geriatric': 'Geriatric care protocols',
            'obstetric': 'Obstetric and gynecological care',
            'emergency': 'Emergency medicine protocols',
            'oncology': 'Cancer treatment guidelines',
            'respiratory': 'Respiratory care recommendations'
        }
        
        for specialty, description in specialties.items():
            if specialty in title_lower:
                summary_points.append(f"• {description}")
                break
        
        # Add general points based on common terms
        if 'treatment' in title_lower or 'therapy' in title_lower:
            summary_points.append("• Provides evidence-based treatment recommendations")
        
        if 'diagnosis' in title_lower or 'screening' in title_lower:
            summary_points.append("• Outlines diagnostic and screening protocols")
        
        if 'prevention' in title_lower or 'preventive' in title_lower:
            summary_points.append("• Focuses on preventive care strategies")
        
        if 'management' in title_lower:
            summary_points.append("• Comprehensive management approach for healthcare providers")
        
        # Add a general point if we don't have enough
        if len(summary_points) < 2:
            summary_points.append("• Evidence-based clinical practice guideline")
            summary_points.append("• Designed for healthcare professionals")
        
        return "\n".join(summary_points[:4])  # Limit to 4 points
    
    def _extract_fallback_tags(self, title: str, content: str = "") -> List[str]:
        """
        Extract fallback tags when AI is not available
        """
        title_lower = title.lower()
        tags = []
        
        # Medical specialties
        specialty_keywords = {
            'cardiology': ['heart', 'cardiac', 'cardiovascular', 'hypertension', 'blood pressure'],
            'endocrinology': ['diabetes', 'endocrine', 'glucose', 'insulin', 'metabolic'],
            'infectious disease': ['infection', 'bacterial', 'viral', 'antibiotic', 'sepsis'],
            'pediatrics': ['pediatric', 'child', 'infant', 'neonatal', 'adolescent'],
            'geriatrics': ['geriatric', 'elderly', 'aging', 'senior'],
            'obstetrics': ['pregnancy', 'obstetric', 'maternal', 'fetal', 'gynecology'],
            'emergency medicine': ['emergency', 'urgent', 'acute', 'trauma'],
            'oncology': ['cancer', 'oncology', 'tumor', 'malignant', 'chemotherapy'],
            'respiratory': ['respiratory', 'lung', 'asthma', 'copd', 'pneumonia'],
            'neurology': ['neurological', 'brain', 'stroke', 'seizure', 'migraine']
        }
        
        # Check for specialties
        for specialty, keywords in specialty_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                tags.append(specialty.title())
                break
        
        # Common medical conditions
        conditions = [
            'diabetes', 'hypertension', 'asthma', 'depression', 'anxiety',
            'arthritis', 'osteoporosis', 'dementia', 'stroke', 'heart disease',
            'cancer', 'obesity', 'smoking', 'alcohol', 'substance abuse'
        ]
        
        for condition in conditions:
            if condition in title_lower:
                tags.append(condition.title())
                break
        
        # Procedures and interventions
        procedures = [
            'screening', 'diagnosis', 'treatment', 'prevention', 'vaccination',
            'surgery', 'medication', 'therapy', 'monitoring', 'assessment'
        ]
        
        for procedure in procedures:
            if procedure in title_lower:
                tags.append(procedure.title())
                break
        
        # If no tags found, add general ones
        if not tags:
            tags = ['Clinical Guidelines', 'Evidence-Based']
        
        return tags[:5]  # Limit to 5 tags
    
    def analyze_guideline_complexity(self, title: str, content: str = "") -> dict:
        """
        Analyze the complexity and target audience of a guideline
        """
        if not self.enabled:
            return self._analyze_fallback_complexity(title, content)
        
        try:
            prompt = f"""
            Analyze the following medical guideline for complexity and target audience:
            
            Title: {title}
            Content: {content[:500] if content else title}
            
            Provide a JSON response with:
            - complexity_level: "Basic", "Intermediate", or "Advanced"
            - target_audience: "Primary Care", "Specialists", "Nurses", "Pharmacists", etc.
            - clinical_urgency: "Routine", "Important", or "Critical"
            - evidence_strength: "Strong", "Moderate", or "Limited"
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical professional expert in clinical practice guidelines."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.2
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                analysis = json.loads(analysis_text)
                return analysis
            except json.JSONDecodeError:
                return self._analyze_fallback_complexity(title, content)
                
        except Exception as e:
            logger.error(f"Error analyzing guideline complexity: {e}")
            return self._analyze_fallback_complexity(title, content)
    
    def _analyze_fallback_complexity(self, title: str, content: str = "") -> dict:
        """
        Fallback complexity analysis when AI is not available
        """
        title_lower = title.lower()
        
        # Simple heuristics for complexity
        if any(word in title_lower for word in ['basic', 'primary', 'general']):
            complexity = "Basic"
        elif any(word in title_lower for word in ['advanced', 'specialist', 'complex']):
            complexity = "Advanced"
        else:
            complexity = "Intermediate"
        
        # Target audience
        if any(word in title_lower for word in ['pediatric', 'child', 'infant']):
            audience = "Pediatricians"
        elif any(word in title_lower for word in ['geriatric', 'elderly']):
            audience = "Geriatricians"
        elif any(word in title_lower for word in ['emergency', 'urgent']):
            audience = "Emergency Medicine"
        else:
            audience = "Primary Care"
        
        # Clinical urgency
        if any(word in title_lower for word in ['emergency', 'urgent', 'critical', 'severe']):
            urgency = "Critical"
        elif any(word in title_lower for word in ['important', 'significant']):
            urgency = "Important"
        else:
            urgency = "Routine"
        
        return {
            "complexity_level": complexity,
            "target_audience": audience,
            "clinical_urgency": urgency,
            "evidence_strength": "Moderate"  # Default assumption
        } 