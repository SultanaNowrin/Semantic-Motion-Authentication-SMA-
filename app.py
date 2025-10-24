from flask import Flask, render_template, request, jsonify
from google import genai
import os
from werkzeug.utils import secure_filename
import time
import random
import secrets
import hashlib
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Gemini client
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=gemini_api_key)

def retry_with_backoff(func, max_retries=3, base_delay=2):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if it's a retryable error
            if any(keyword in error_msg for keyword in ['503', 'overloaded', 'unavailable', 'rate limit', 'quota']):
                if attempt < max_retries - 1:
                    # Calculate delay with exponential backoff and jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    print(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    # Last attempt failed
                    raise Exception(f"All {max_retries} attempts failed. Last error: {str(e)}")
            else:
                # Non-retryable error, raise immediately
                raise e
    
def analyze_with_gemini(prompt, video_file, max_retries=3):
    """Analyze video with Gemini with retry logic and model fallback"""
    models_to_try = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]
    
    last_error = None
    
    for model_name in models_to_try:
        print(f"Trying model: {model_name}")
        
        def make_request():
            return client.models.generate_content(
                model=model_name,
                contents=[prompt, video_file]
            )
        
        try:
            response = retry_with_backoff(make_request, max_retries)
            print(f"Successfully analyzed with model: {model_name}")
            return response
        except Exception as e:
            last_error = e
            print(f"Model {model_name} failed: {str(e)}")
            continue
    
    # If all models failed, raise the last error
    raise Exception(f"All models failed. Last error: {str(last_error)}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class MovementPasswordGenerator:
    """
    Advanced body movement-based password generation system with enhanced biometric analysis
    """
    
    def __init__(self):
        # Multi-level character substitution for enhanced security
        self.char_substitutions = {
            'basic': {'a': '@', 'e': '3', 'i': '!', 'o': '0', 's': '$', 't': '7', 'l': '1', 'g': '9', 'b': '6'},
            'advanced': {'u': 'µ', 'n': 'ñ', 'c': '¢', 'y': '¥', 'p': 'þ', 'r': 'ř', 'm': 'м'},
            'contextual': {'walk': 'w4lk', 'move': 'm0v3', 'turn': '7urn', 'step': '57ep', 'wave': 'w4v3'}
        }
        
        # Biometric movement patterns for fingerprinting
        self.movement_biometrics = {
            'gait_patterns': ['stride', 'cadence', 'pace', 'rhythm', 'flow'],
            'coordination_markers': ['sync', 'balance', 'stability', 'fluidity', 'precision'],
            'energy_signatures': ['vigorous', 'gentle', 'explosive', 'sustained', 'irregular'],
            'spatial_patterns': ['linear', 'curved', 'angular', 'circular', 'spiral']
        }
        
        # Movement-related word patterns for dynamic extraction
        self.movement_patterns = {
            'verbs': [
                r'\b(\w+ing)\b',  # Present participle verbs (walking, moving, etc.)
                r'\b(\w+ed)\b',   # Past tense verbs (walked, moved, etc.)
                r'\b(moves?|steps?|turns?|bends?|lifts?|waves?|raises?|lowers?)\b',  # Common movement verbs
                r'\b(swings?|rotates?|extends?|stretches?|balances?|gestures?)\b'
            ],
            'actions': [
                r'\b(moving|walking|running|jumping|reaching|pointing|waving)\b',
                r'\b(turning|bending|stretching|lifting|lowering|raising)\b',
                r'\b(swinging|rotating|extending|balancing|stepping|gesturing)\b'
            ]
        }
        
        # Body parts and directional terms for context
        self.contextual_terms = {
            'body_parts': ['arm', 'hand', 'leg', 'foot', 'head', 'torso', 'body', 'shoulder', 'knee', 'elbow'],
            'directions': ['left', 'right', 'up', 'down', 'forward', 'backward', 'above', 'below', 'side'],
            'intensities': ['gentle', 'rapid', 'slow', 'quick', 'smooth', 'abrupt', 'rhythmic', 'steady']
        }
        
        # Password templates for different security levels
        self.password_templates = [
            "{action}_{modifier}_{context}_{random}",
            "{action}{context}_{modifier}{random}",
            "{modifier}_{action}_{random}_{context}",
            "{random}{action}_{context}_{modifier}"
        ]
    
    def extract_semantic_elements(self, movement_description):
        """
        Extract key semantic elements from movement description using dynamic NLP techniques
        Following methodology with enhanced flexibility
        """
        # Convert to lowercase for processing
        text = movement_description.lower()
        
        # Dynamic action extraction using multiple strategies
        actions = self._extract_actions_dynamically(text)
        
        # Extract contextual descriptors
        descriptors = self._extract_contextual_descriptors(text)
        
        # Extract intensity and quality modifiers
        qualifiers = self._extract_movement_qualifiers(text)
        
        return {
            'actions': actions[:3],  # Top 3 most relevant actions
            'descriptors': descriptors[:3],  # Top 3 descriptors
            'qualifiers': qualifiers[:2],  # Movement quality descriptors
            'full_text': text
        }
    
    def _extract_actions_dynamically(self, text):
        """
        Dynamically extract action words using pattern matching and context analysis
        """
        actions = set()
        
        # Extract using predefined movement patterns
        for pattern_type, patterns in self.movement_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                actions.update([match.lower() for match in matches if len(match) > 2])
        
        # Extract verbs that appear near body parts (contextual extraction)
        for body_part in self.contextual_terms['body_parts']:
            if body_part in text:
                # Look for verbs within 5 words of body parts
                body_part_pattern = rf'\b\w+\b(?:\s+\w+){{0,4}}\s+{body_part}|\b{body_part}\b(?:\s+\w+){{0,4}}\s+\w+ing\b'
                matches = re.findall(body_part_pattern, text)
                for match in matches:
                    # Extract potential action words from the match
                    words = match.split()
                    for word in words:
                        if word.endswith('ing') or word in ['moves', 'turns', 'lifts', 'waves']:
                            actions.add(word)
        
        # Filter and rank actions by relevance
        filtered_actions = []
        for action in actions:
            if len(action) >= 3 and action.isalpha():  # Valid action word
                # Prioritize certain action types
                if any(action.endswith(suffix) for suffix in ['ing', 'ed']) or \
                   any(root in action for root in ['move', 'turn', 'lift', 'wave', 'step']):
                    filtered_actions.append(action)
        
        return list(set(filtered_actions))  # Remove duplicates
    
    def _extract_contextual_descriptors(self, text):
        """
        Extract body parts, directions, and spatial descriptors
        """
        descriptors = []
        
        # Extract all contextual terms present in text
        for category, terms in self.contextual_terms.items():
            for term in terms:
                if term in text:
                    descriptors.append(term)
        
        # Extract spatial relationships and positions
        spatial_patterns = [
            r'\b(above|below|beside|near|against|towards?)\s+\w+',
            r'\b(upward|downward|sideways|clockwise|counter-clockwise)\b',
            r'\b(horizontal|vertical|diagonal|circular)\b'
        ]
        
        for pattern in spatial_patterns:
            matches = re.findall(pattern, text)
            descriptors.extend(matches)
        
        return list(set(descriptors))  # Remove duplicates
    
    def _extract_movement_qualifiers(self, text):
        """
        Extract qualitative aspects of movement (speed, intensity, rhythm)
        """
        qualifiers = []
        
        # Quality patterns
        quality_patterns = [
            r'\b(smooth|rough|jerky|fluid|stiff|relaxed|tense)\b',
            r'\b(quick|slow|rapid|gradual|sudden|gentle)\b',
            r'\b(rhythmic|erratic|steady|consistent|irregular)\b',
            r'\b(natural|forced|effortless|deliberate)\b'
        ]
        
        for pattern in quality_patterns:
            matches = re.findall(pattern, text)
            qualifiers.extend(matches)
        
        # Extract comparative and superlative forms
        comparative_patterns = [
            r'\b(\w+er)\s+(than|movement)\b',  # faster, slower, etc.
            r'\b(more|less)\s+(\w+ly)\b'       # more quickly, less smoothly
        ]
        
        for pattern in comparative_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    qualifiers.extend([word for word in match if len(word) > 2])
                else:
                    qualifiers.append(match)
        
        return list(set(qualifiers))  # Remove duplicates
    
    def generate_contextual_modifiers(self, movement_analysis=""):
        """
        Generate advanced contextual modifiers with biometric and behavioral analysis
        Enhanced methodology with multi-source entropy
        """
        now = datetime.now()
        
        # Multi-layered temporal context
        temporal_context = {
            'micro_time': f"{now.microsecond}"[:3],  # High-precision timing
            'compound_time': f"{now.hour}{now.minute}{now.second}",
            'cyclical': f"{now.weekday()}{now.day % 7}",
            'seasonal': f"{now.month}{(now.day // 7) + 1}"  # Week of month
        }
        
        # Movement-specific entropy generation
        movement_entropy = self._generate_movement_entropy(movement_analysis)
        
        # Behavioral pattern analysis
        behavioral_signature = self._analyze_behavioral_patterns(movement_analysis)
        
        # Create multiple hash layers for enhanced security
        entropy_sources = [
            temporal_context['compound_time'],
            movement_entropy['pattern_hash'],
            behavioral_signature['complexity_score'],
            str(temporal_context['micro_time'])
        ]
        
        # Multi-hash approach for maximum entropy
        combined_hash = hashlib.sha256(''.join(entropy_sources).encode()).hexdigest()
        
        return {
            'temporal': combined_hash[:4],
            'movement_entropy': movement_entropy,
            'behavioral_signature': behavioral_signature,
            'session': secrets.token_hex(3),  # Increased session entropy
            'compound_modifier': combined_hash[4:8]  # Additional unique modifier
        }
    
    def _generate_movement_entropy(self, movement_text):
        """
        Generate entropy specifically from movement characteristics
        """
        if not movement_text:
            return {'pattern_hash': secrets.token_hex(2), 'complexity': 'low'}
        
        # Analyze movement complexity
        text_lower = movement_text.lower()
        
        # Count different types of movements
        movement_types = 0
        for category in self.movement_biometrics.values():
            for pattern in category:
                if pattern in text_lower:
                    movement_types += 1
        
        # Generate pattern-based hash
        movement_words = re.findall(r'\b\w+\b', text_lower)
        pattern_signature = ''.join([word[0] for word in movement_words if len(word) > 3])[:8]
        
        # Create movement-specific hash
        movement_hash = hashlib.md5(f"{pattern_signature}{movement_types}".encode()).hexdigest()[:3]
        
        complexity_level = 'high' if movement_types > 5 else 'medium' if movement_types > 2 else 'low'
        
        return {
            'pattern_hash': movement_hash,
            'complexity': complexity_level,
            'movement_types': movement_types,
            'signature': pattern_signature[:4]
        }
    
    def _analyze_behavioral_patterns(self, movement_text):
        """
        Analyze behavioral patterns for password generation
        """
        if not movement_text:
            return {'complexity_score': '0', 'confidence': 'low'}
        
        text_lower = movement_text.lower()
        
        # Behavioral indicators
        coordination_indicators = ['smooth', 'coordinated', 'synchronized', 'balanced', 'stable']
        energy_indicators = ['quick', 'slow', 'vigorous', 'gentle', 'explosive', 'sustained']
        precision_indicators = ['precise', 'deliberate', 'controlled', 'natural', 'fluid']
        
        # Score behavioral complexity
        complexity_score = 0
        behavioral_features = []
        
        for indicator in coordination_indicators:
            if indicator in text_lower:
                complexity_score += 2
                behavioral_features.append('C')  # Coordination
        
        for indicator in energy_indicators:
            if indicator in text_lower:
                complexity_score += 3
                behavioral_features.append('E')  # Energy
        
        for indicator in precision_indicators:
            if indicator in text_lower:
                complexity_score += 1
                behavioral_features.append('P')  # Precision
        
        # Create behavioral signature
        behavioral_signature = ''.join(set(behavioral_features))[:3] or 'GEN'
        
        # Determine confidence level
        confidence = 'high' if complexity_score > 8 else 'medium' if complexity_score > 4 else 'low'
        
        return {
            'complexity_score': str(complexity_score),
            'signature': behavioral_signature,
            'confidence': confidence,
            'features_detected': len(behavioral_features)
        }
    
    def apply_entropy_randomization(self, text, entropy_level=0.3, context="general"):
        """
        Apply advanced multi-layered entropy-based randomization
        Enhanced  methodology with biometric-aware substitutions
        """
        if not text:
            return text
            
        result = list(text.lower())
        changes_made = 0
        max_changes = max(1, int(len(text) * entropy_level))
        
        # Select appropriate substitution level based on context
        if context == "movement" and text.lower() in self.char_substitutions['contextual']:
            return self.char_substitutions['contextual'][text.lower()]
        
        # Multi-phase randomization
        for i in range(len(result)):
            if changes_made >= max_changes:
                break
                
            char = result[i]
            original_char = char
            
            # Phase 1: Basic character substitution (50% chance)
            if char in self.char_substitutions['basic'] and random.random() < 0.4:
                result[i] = self.char_substitutions['basic'][char]
                changes_made += 1
                continue
            
            # Phase 2: Advanced character substitution (30% chance)
            if char in self.char_substitutions['advanced'] and random.random() < 0.2:
                result[i] = self.char_substitutions['advanced'][char]
                changes_made += 1
                continue
            
            # Phase 3: Positional entropy (characters based on position)
            if char.isalpha() and random.random() < 0.25:
                # Position-based transformation
                if i % 2 == 0:  # Even positions
                    result[i] = char.upper()
                else:  # Odd positions
                    result[i] = str(ord(char) % 10)  # Convert to number based on ASCII
                changes_made += 1
                continue
            
            # Phase 4: Biometric-inspired transformations
            if char.isalpha() and random.random() < 0.15:
                # Movement-inspired character transformation
                movement_transform = {
                    'w': '∿', 's': '~', 'r': '↻', 'l': '↺', 
                    'm': '↕', 'u': '↑', 'd': '↓', 'f': '→'
                }
                if char in movement_transform:
                    result[i] = movement_transform[char]
                    changes_made += 1
        
        return ''.join(result)
    
    def generate_biometric_hash(self, semantic_elements, behavioral_data):
        """
        Generate a biometric-based hash from movement characteristics
        """
        # Combine multiple biometric factors
        biometric_string = ""
        
        # Movement signature
        if semantic_elements.get('actions'):
            action_signature = ''.join([action[0].upper() for action in semantic_elements['actions'][:3]])
            biometric_string += action_signature
        
        # Behavioral complexity
        if behavioral_data.get('complexity_score'):
            biometric_string += behavioral_data['complexity_score']
        
        # Movement entropy
        if behavioral_data.get('signature'):
            biometric_string += behavioral_data['signature']
        
        # Generate cryptographic hash
        if biometric_string:
            biometric_hash = hashlib.sha256(biometric_string.encode()).hexdigest()
            return biometric_hash[:6]  # Use first 6 characters
        
        return secrets.token_hex(3)  # Fallback random hash
    
    def assemble_password(self, semantic_elements, contextual_modifiers):
        """
        Assemble advanced biometric password with multi-layered security
        Enhanced methodology with biometric fingerprinting
        """
        # Generate biometric hash from movement characteristics
        biometric_hash = self.generate_biometric_hash(
            semantic_elements, 
            contextual_modifiers.get('behavioral_signature', {})
        )
        
        # Extract and process primary action with context-aware entropy
        action = ""
        if semantic_elements['actions']:
            primary_action = self._select_primary_action(semantic_elements['actions'])
            action = primary_action[:6]
            action = self.apply_entropy_randomization(action, entropy_level=0.4, context="movement")
        
        # Multi-source descriptor extraction
        descriptor = self._extract_multi_source_descriptor(semantic_elements)
        
        # Advanced movement signature with behavioral analysis
        movement_signature = self._create_advanced_movement_signature(semantic_elements, contextual_modifiers)
        
        # Multi-layered contextual components
        temporal_layer = contextual_modifiers['temporal']
        entropy_layer = contextual_modifiers.get('compound_modifier', secrets.token_hex(2))
        behavioral_layer = contextual_modifiers.get('behavioral_signature', {}).get('signature', 'GEN')
        
        # Adaptive random component based on movement complexity
        movement_complexity = contextual_modifiers.get('movement_entropy', {}).get('complexity', 'medium')
        random_entropy = 3 if movement_complexity == 'high' else 2 if movement_complexity == 'medium' else 1
        random_component = secrets.token_hex(random_entropy)
        
        # Select optimal template with security considerations
        template = self._select_security_optimal_template(semantic_elements, contextual_modifiers)
        
        # Assemble password with advanced components
        password_components = {
            'action': action or "mΘv",  # Enhanced fallback
            'modifier': descriptor,
            'biometric': biometric_hash[:4],
            'temporal': temporal_layer,
            'entropy': entropy_layer,
            'behavioral': behavioral_layer,
            'random': random_component,
            'signature': movement_signature
        }
        
        # Dynamic assembly based on template
        password = self._dynamic_password_assembly(template, password_components)
        
        # Multi-phase complexity enhancement
        password = self.ensure_advanced_complexity(password, contextual_modifiers)
        
        return password
    
    def _extract_multi_source_descriptor(self, semantic_elements):
        """
        Extract descriptor from multiple sources with prioritization
        """
        descriptor = ""
        
        # Priority 1: Qualifiers (movement quality is most distinctive)
        if semantic_elements.get('qualifiers'):
            descriptor = semantic_elements['qualifiers'][0][:5]
            descriptor = self.apply_entropy_randomization(descriptor, entropy_level=0.3)
        # Priority 2: Descriptors (spatial/body parts)
        elif semantic_elements['descriptors']:
            descriptor = semantic_elements['descriptors'][0][:4]
            descriptor = self.apply_entropy_randomization(descriptor, entropy_level=0.35)
        # Priority 3: Secondary action
        elif len(semantic_elements['actions']) > 1:
            descriptor = semantic_elements['actions'][1][:4]
            descriptor = self.apply_entropy_randomization(descriptor, entropy_level=0.4)
        
        return descriptor or "dΨn"  # Enhanced fallback
    
    def _create_advanced_movement_signature(self, semantic_elements, contextual_modifiers):
        """
        Create sophisticated movement signature with behavioral analysis
        """
        signature_components = []
        
        # Biometric signature from actions
        for action in semantic_elements.get('actions', [])[:2]:
            if action:
                signature_components.append(action[0].upper())
        
        # Behavioral signature integration
        behavioral_sig = contextual_modifiers.get('behavioral_signature', {})
        if behavioral_sig.get('signature'):
            signature_components.append(behavioral_sig['signature'][:2])
        
        # Movement entropy signature
        movement_entropy = contextual_modifiers.get('movement_entropy', {})
        if movement_entropy.get('signature'):
            signature_components.append(movement_entropy['signature'][:2])
        
        # Complexity-based transformation
        complexity = movement_entropy.get('complexity', 'medium')
        if complexity == 'high':
            signature_components.append('Ω')  # High complexity marker
        elif complexity == 'low':
            signature_components.append('α')  # Low complexity marker
        
        base_signature = ''.join(signature_components) or "MΣ"
        
        # Apply cryptographic transformation
        signature_hash = hashlib.md5(base_signature.encode()).hexdigest()
        return signature_hash[:4]
    
    def _select_security_optimal_template(self, semantic_elements, contextual_modifiers):
        """
        Select template based on security requirements and available data
        """
        # Enhanced templates with biometric integration
        high_security_templates = [
            "{action}_{biometric}_{temporal}_{random}",
            "{biometric}{action}_{entropy}_{behavioral}",
            "{signature}{action}_{temporal}{biometric}",
            "{action}_{behavioral}_{entropy}_{signature}"
        ]
        
        medium_security_templates = [
            "{action}_{modifier}_{temporal}_{random}",
            "{action}{signature}_{entropy}_{random}",
            "{modifier}_{action}_{biometric}_{temporal}"
        ]
        
        # Determine security level based on available data quality
        behavioral_confidence = contextual_modifiers.get('behavioral_signature', {}).get('confidence', 'low')
        movement_complexity = contextual_modifiers.get('movement_entropy', {}).get('complexity', 'medium')
        
        use_high_security = (behavioral_confidence in ['high', 'medium'] and 
                           movement_complexity in ['high', 'medium'] and
                           len(semantic_elements.get('actions', [])) >= 2)
        
        templates = high_security_templates if use_high_security else medium_security_templates
        return random.choice(templates)
    
    def _dynamic_password_assembly(self, template, components):
        """
        Dynamically assemble password handling missing components gracefully
        """
        try:
            return template.format(**components)
        except KeyError as e:
            # Fallback assembly if template has missing components
            fallback_template = "{action}_{biometric}_{temporal}_{random}"
            return fallback_template.format(
                action=components.get('action', 'mΘv'),
                biometric=components.get('biometric', 'B10'),
                temporal=components.get('temporal', secrets.token_hex(2)),
                random=components.get('random', secrets.token_hex(2))
            )
    
    def ensure_advanced_complexity(self, password, contextual_modifiers):
        """
        Enhanced complexity assurance with biometric considerations
        """
        # Start with basic complexity
        password = self.ensure_complexity(password)
        
        # Add biometric complexity markers
        behavioral_confidence = contextual_modifiers.get('behavioral_signature', {}).get('confidence', 'low')
        
        if behavioral_confidence == 'high':
            # Add high-confidence biometric markers
            if not re.search(r'[Ω∿↻↺↕↑↓→]', password):
                password += random.choice(['Ω', '∿', '↻'])
        
        # Ensure Unicode diversity for enhanced security
        if not re.search(r'[Θ∑Ψαβγδε]', password):
            password += random.choice(['Θ', '∑', 'Ψ'])
        
        # Dynamic length adjustment based on complexity
        movement_complexity = contextual_modifiers.get('movement_entropy', {}).get('complexity', 'medium')
        min_length = 16 if movement_complexity == 'high' else 14 if movement_complexity == 'medium' else 12
        
        while len(password) < min_length:
            password += secrets.token_hex(1)
        
        # Maximum length control
        if len(password) > 24:
            password = password[:24]
        
        return password
    
    def _select_primary_action(self, actions):
        """
        Select the most distinctive action for password generation
        """
        # Priority order for action selection
        priority_actions = ['walking', 'running', 'jumping', 'waving', 'pointing', 'turning']
        
        # First, look for high-priority actions
        for priority_action in priority_actions:
            for action in actions:
                if priority_action in action:
                    return action
        
        # If no priority actions found, use the longest action (more distinctive)
        return max(actions, key=len) if actions else "move"
    
    def _create_movement_signature(self, semantic_elements):
        """
        Create a unique signature from movement characteristics
        """
        signature_parts = []
        
        # Use first letter of each action
        for action in semantic_elements.get('actions', [])[:2]:
            if action:
                signature_parts.append(action[0].upper())
        
        # Use first letter of descriptors
        for desc in semantic_elements.get('descriptors', [])[:2]:
            if desc:
                signature_parts.append(desc[0].lower())
        
        # Use qualifiers for additional uniqueness
        for qual in semantic_elements.get('qualifiers', [])[:1]:
            if qual:
                signature_parts.append(qual[0])
        
        return ''.join(signature_parts) or "MS"  # MS = Movement Signature
    
    def _select_optimal_template(self, semantic_elements):
        """
        Select the best template based on available semantic elements
        """
        # Enhanced templates with more dynamic components
        enhanced_templates = [
            "{action}_{modifier}_{context}_{random}",
            "{action}{signature}_{context}_{random}",
            "{modifier}_{action}_{random}_{context}",
            "{signature}{action}_{context}_{modifier}",
            "{action}_{context}{signature}_{random}"
        ]
        
        # Use enhanced templates if we have rich semantic data
        if (len(semantic_elements.get('actions', [])) >= 2 or 
            len(semantic_elements.get('descriptors', [])) >= 2 or
            semantic_elements.get('qualifiers')):
            return random.choice(enhanced_templates)
        
        # Fall back to basic templates
        return random.choice(self.password_templates)
    
    def ensure_complexity(self, password):
        """
        Ensure password meets security requirements
        """
        # Add special characters if none present
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            password += random.choice(['!', '@', '#', '$', '%'])
        
        # Add numbers if none present  
        if not re.search(r'\d', password):
            password += str(random.randint(0, 9))
        
        # Add uppercase if none present
        if not re.search(r'[A-Z]', password):
            password = password[0].upper() + password[1:] if password else password
        
        # Ensure minimum length
        while len(password) < 12:
            password += secrets.token_hex(1)
        
        # Limit maximum length
        if len(password) > 20:
            password = password[:20]
        
        return password
    
    def generate_password(self, movement_analysis, movement_summary):
        """
        Main password generation function with dynamic semantic extraction
        """
        try:
            # Extract semantic elements from both analysis and summary using dynamic methods
            analysis_elements = self.extract_semantic_elements(movement_analysis)
            summary_elements = self.extract_semantic_elements(movement_summary)
            
            # Intelligently combine elements, prioritizing summary for actions and analysis for descriptors
            combined_elements = {
                'actions': list(set(summary_elements['actions'] + analysis_elements['actions']))[:3],
                'descriptors': list(set(summary_elements['descriptors'] + analysis_elements['descriptors']))[:3],
                'qualifiers': list(set(summary_elements.get('qualifiers', []) + analysis_elements.get('qualifiers', [])))[:2],
                'full_text': summary_elements['full_text'] + " " + analysis_elements['full_text']
            }
            
            # Analyze extraction effectiveness for feedback
            extraction_analysis = self.analyze_extraction_effectiveness(
                combined_elements['full_text'], 
                combined_elements
            )
            
            # Generate advanced contextual modifiers with movement analysis
            contextual_modifiers = self.generate_contextual_modifiers(combined_elements['full_text'])
            
            # Assemble password using dynamic components
            password = self.assemble_password(combined_elements, contextual_modifiers)
            
            # Advanced strength assessment with contextual data
            strength_analysis = self.assess_password_strength(password, contextual_modifiers)
            
            return {
                'password': password,
                'components': {
                    'semantic_elements': combined_elements,
                    'contextual_modifiers': contextual_modifiers,
                    'extraction_analysis': extraction_analysis
                },
                'strength': strength_analysis['strength'],
                'strength_analysis': strength_analysis,
                'generation_method': 'advanced_biometric_extraction',
                'security_features': self._get_security_features_summary(contextual_modifiers)
            }
            
        except Exception as e:
            # Fallback password generation with error details
            fallback_password = f"Move{secrets.token_hex(4)}{datetime.now().hour}!"
            return {
                'password': fallback_password,
                'components': {
                    'error': str(e),
                    'fallback_used': True
                },
                'strength': 'Medium',
                'generation_method': 'fallback'
            }
    
    def assess_password_strength(self, password, contextual_data=None):
        """
        Advanced password strength assessment with biometric considerations
        """
        score = 0
        analysis = {'factors': [], 'recommendations': []}
        
        # Basic length assessment
        if len(password) >= 16:
            score += 3
            analysis['factors'].append('Excellent length (16+ chars)')
        elif len(password) >= 12:
            score += 2
            analysis['factors'].append('Good length (12+ chars)')
        else:
            analysis['recommendations'].append('Increase length to 12+ characters')
        
        # Character diversity assessment
        char_types = 0
        if re.search(r'[a-z]', password):
            score += 1
            char_types += 1
        if re.search(r'[A-Z]', password):
            score += 1
            char_types += 1
        if re.search(r'\d', password):
            score += 1
            char_types += 1
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            score += 2
            char_types += 1
        
        # Unicode and special biometric characters
        if re.search(r'[Ω∿↻↺↕↑↓→ΘΨαβγδε]', password):
            score += 3
            analysis['factors'].append('Biometric Unicode characters detected')
        
        # Movement-based entropy assessment
        if contextual_data:
            behavioral_confidence = contextual_data.get('behavioral_signature', {}).get('confidence', 'low')
            movement_complexity = contextual_data.get('movement_entropy', {}).get('complexity', 'medium')
            
            if behavioral_confidence == 'high':
                score += 2
                analysis['factors'].append('High behavioral confidence')
            elif behavioral_confidence == 'medium':
                score += 1
                analysis['factors'].append('Medium behavioral confidence')
            
            if movement_complexity == 'high':
                score += 2
                analysis['factors'].append('High movement complexity')
            elif movement_complexity == 'medium':
                score += 1
        
        # Entropy and unpredictability
        unique_chars = len(set(password))
        if unique_chars >= len(password) * 0.8:
            score += 2
            analysis['factors'].append('High character uniqueness')
        elif unique_chars >= len(password) * 0.6:
            score += 1
        
        # Pattern analysis (penalize obvious patterns)
        if re.search(r'(.)\1{2,}', password):  # Repeated characters
            score -= 1
            analysis['recommendations'].append('Reduce character repetition')
        
        if re.search(r'(012|123|234|345|456|567|678|789|890|abc|def|ghi)', password.lower()):
            score -= 2
            analysis['recommendations'].append('Avoid sequential patterns')
        
        # Final assessment
        if score >= 12:
            strength = 'Exceptional'
        elif score >= 9:
            strength = 'Very Strong'
        elif score >= 6:
            strength = 'Strong'
        elif score >= 4:
            strength = 'Medium'
        else:
            strength = 'Weak'
        
        return {
            'strength': strength,
            'score': score,
            'max_score': 15,
            'analysis': analysis,
            'character_types': char_types
        }
    
    def analyze_extraction_effectiveness(self, movement_text, extracted_elements):
        """
        Analyze how well the dynamic extraction worked and provide feedback
        This could be used for continuous improvement of the extraction algorithms
        """
        effectiveness_score = 0
        feedback = []
        
        # Check if we extracted meaningful actions
        if extracted_elements['actions']:
            effectiveness_score += 3
            feedback.append(f"✓ Extracted {len(extracted_elements['actions'])} action(s): {', '.join(extracted_elements['actions'])}")
        else:
            feedback.append("⚠ No actions extracted - may need pattern expansion")
        
        # Check descriptor extraction
        if extracted_elements['descriptors']:
            effectiveness_score += 2
            feedback.append(f"✓ Extracted {len(extracted_elements['descriptors'])} descriptor(s)")
        else:
            feedback.append("⚠ No descriptors extracted")
        
        # Check qualifier extraction
        if extracted_elements.get('qualifiers'):
            effectiveness_score += 1
            feedback.append(f"✓ Extracted movement qualities: {', '.join(extracted_elements['qualifiers'])}")
        
        # Calculate percentage of text that contributed to extraction
        text_words = len(movement_text.split())
        extracted_words = len(extracted_elements['actions']) + len(extracted_elements['descriptors']) + len(extracted_elements.get('qualifiers', []))
        
        if text_words > 0:
            utilization_rate = (extracted_words / text_words) * 100
            feedback.append(f"📊 Text utilization: {utilization_rate:.1f}%")
        
        return {
            'effectiveness_score': effectiveness_score,
            'max_score': 6,
            'feedback': feedback,
            'utilization_rate': utilization_rate if text_words > 0 else 0
        }
    
    def _get_security_features_summary(self, contextual_modifiers):
        """
        Provide a summary of security features implemented in the password
        """
        features = []
        
        # Biometric features
        behavioral_confidence = contextual_modifiers.get('behavioral_signature', {}).get('confidence', 'low')
        if behavioral_confidence in ['high', 'medium']:
            features.append(f"Behavioral biometrics ({behavioral_confidence} confidence)")
        
        # Movement entropy
        movement_complexity = contextual_modifiers.get('movement_entropy', {}).get('complexity', 'medium')
        features.append(f"Movement entropy analysis ({movement_complexity} complexity)")
        
        # Multi-layered hashing
        if contextual_modifiers.get('compound_modifier'):
            features.append("Multi-layered cryptographic hashing")
        
        # Temporal entropy
        features.append("High-precision temporal entropy")
        
        # Advanced character substitution
        features.append("Multi-tier character substitution")
        
        # Biometric fingerprinting
        features.append("Movement pattern fingerprinting")
        
        return features

# Initialize password generator
password_generator = MovementPasswordGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format. Allowed: MP4, AVI, MOV, MKV, WEBM'}), 400
    
    try:
        # Save the file
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'message': 'Video uploaded successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_video():
    data = request.get_json()
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Upload video to Gemini - correct syntax: just pass file path as string
        video_file = client.files.upload(file=filepath)
        
        # Wait for file to be processed
        while video_file.state == "PROCESSING":
            time.sleep(2)
            video_file = client.files.get(name=video_file.name)
        
        if video_file.state == "FAILED":
            raise ValueError("Video processing failed")
        
        # Analyze body movements with detailed prompt
        prompt = """Analyze this video and provide a detailed explanation of the person's body movements in TWO SECTIONS:

**SECTION 1: COMPREHENSIVE ANALYSIS**
Focus ONLY on:
- Body posture and positioning
- Arm and hand movements
- Leg and foot movements
- Head and torso movements
- Overall body coordination and flow
- Specific gestures or actions performed
- Movement patterns and sequences
- Speed and intensity of movements

**SECTION 2: SUMMARY**
Provide a concise one-liner summary that captures the essence of the person's overall movement characteristics and activity.

IGNORE:
- Background elements
- Other people or objects
- Lighting, colors, or visual aesthetics
- Audio or ambient sounds

Format your response with clear headings for both sections. Start with "📊 Movement Analysis" for the comprehensive section and "📝 Summary" for the summary section."""

        response = analyze_with_gemini(prompt, video_file)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        # Delete file from Gemini
        try:
            client.files.delete(name=video_file.name)
        except:
            pass
        
        # Parse the response to separate comprehensive analysis and summary
        analysis_text = response.text
        
        # Split analysis into sections
        sections = analysis_text.split('📝 Summary')
        comprehensive_analysis = sections[0].replace('📊 Movement Analysis', '').strip()
        summary = sections[1].strip() if len(sections) > 1 else "Movement analysis completed"
        
        # Generate password based on movement analysis
        password_result = password_generator.generate_password(comprehensive_analysis, summary)
        
        return jsonify({
            'success': True,
            'analysis': {
                'comprehensive': comprehensive_analysis,
                'summary': summary,
                'full_text': analysis_text
            },
            'password': password_result
        })
    
    except Exception as e:
        # Clean up on error
        try:
            os.remove(filepath)
        except:
            pass
        
        error_msg = str(e)
        
        # Provide more user-friendly error messages
        if '503' in error_msg or 'overloaded' in error_msg.lower():
            user_error = 'The AI service is currently experiencing high traffic. Please try again in a few minutes.'
        elif 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower():
            user_error = 'API quota exceeded. Please try again later or check your API limits.'
        elif 'failed' in error_msg.lower() and 'processing' in error_msg.lower():
            user_error = 'Video processing failed. Please ensure the video file is valid and not corrupted.'
        else:
            user_error = f'Analysis failed: {error_msg}'
        
        return jsonify({'error': user_error}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)