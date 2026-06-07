#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver Ollama Module - Local AI Integration
Support for Ollama with various models for local AI
"""

import os
import requests
import json
from typing import Optional, Dict, Any, List

# Ollama settings
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

# Supported models
OLLAMA_MODELS = {
    "llama3.2": {
        "name": "Llama 3.2",
        "description": "Powerful model for complex dreams - runs on 8GB RAM",
        "ram_gb": 8,
        "recommended": True
    },
    "llama3.1": {
        "name": "Llama 3.1",
        "description": "Fast and capable model",
        "ram_gb": 8
    },
    "mistral": {
        "name": "Mistral",
        "description": "Fast and light model for quick responses",
        "ram_gb": 6
    },
    "gemma4:12b-it-qat": {
        "name": "Gemma 4 12B QAT",
        "description": "Memory optimized Gemma 4 (when available)",
        "ram_gb": 8,
        "future": True
    }
}

# Dream interpretation prompts optimized for Gemma 4
DREAM_PROMPTS = {
    "islamic": {
        "ar": """You are an Islamic dream interpreter specializing in Ibn Sirin's methodology.
Your analysis must include:
1. Organized symbolic interpretation
2. Relevant Quranic verses and Hadiths
3. Psychological and spiritual meanings
4. Practical future advice

Dream: {dream_text}

Provide interpretation in Arabic.""",
        "en": """You are an expert Islamic dream interpreter following Ibn Sirin's methodology.
Your analysis must include:
1. Organized symbolic interpretation
2. Relevant Quranic verses and Hadiths
3. Psychological and spiritual meanings
4. Practical future advice

Dream: {dream_text}

Provide interpretation in clear English."""
    },
    "psychological": {
        "ar": """You are a psychologist specializing in dream analysis using Freud and Jung.
Analysis must include:
1. Psychological symbol analysis
2. Unconscious experience connections
3. Emotional and fear meanings
4. Self-reflection recommendations

Dream: {dream_text}

Provide analysis in Arabic.""",
        "en": """You are a psychologist specializing in dream analysis using Freud and Jung.
Analysis must include:
1. Psychological symbol analysis
2. Unconscious experience connections
3. Emotional and fear meanings
4. Self-reflection recommendations

Dream: {dream_text}

Provide analysis in English."""
    },
    "ancient": {
        "ar": """You are an expert in ancient civilizations dream interpretation.
Interpret according to:
1. Historical symbol context
2. Cross-civilization comparisons
3. Ancient spiritual meanings
4. Contemporary relevance

Dream: {dream_text}

Provide interpretation in Arabic.""",
        "en": """You are an expert in ancient civilizations dream interpretation.
Interpret according to:
1. Historical symbol context
2. Cross-civilization comparisons
3. Ancient spiritual meanings
4. Contemporary relevance

Dream: {dream_text}"""
    },
    "general": {
        "ar": """You are a comprehensive dream interpreter combining Islamic heritage, psychology, and ancient wisdom.
Provide balanced analysis including:
1. Islamic and spiritual interpretation
2. Psychological analysis
3. Historical comparisons
4. Comprehensive practical advice

Dream: {dream_text}

Provide interpretation in Arabic.""",
        "en": """You are a comprehensive dream interpreter combining Islamic heritage, psychology, and ancient wisdom.
Provide balanced analysis including:
1. Islamic and spiritual interpretation
2. Psychological analysis
3. Historical comparisons
4. Comprehensive practical advice

Dream: {dream_text}"""
    }
}


class OllamaAI:
    """Ollama engine with local AI model support"""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = "llama3.2"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_generate = f"{self.base_url}/api/generate"
        self.api_chat = f"{self.base_url}/api/chat"
        self.api_tags = f"{self.base_url}/api/tags"
    
    def check_connection(self) -> Dict[str, Any]:
        """Check Ollama connection"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "status": "connected",
                    "models": [m.get("name") for m in models],
                    "current_model": self.model
                }
            return {"status": "error", "message": f"HTTP {response.status_code}"}
        except requests.exceptions.ConnectionError:
            return {"status": "disconnected", "message": "Ollama is not connected"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def pull_model(self, model_name: str = None) -> Dict[str, Any]:
        """Download Gemma 4 model"""
        model = model_name or self.model
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model},
                stream=True,
                timeout=3600  # 1 hour for download
            )
            
            progress = []
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        status = data.get("status", "")
                        if status == "success":
                            return {"status": "success", "model": model}
                        progress.append(status)
                    except json.JSONDecodeError:
                        continue
            
            return {"status": "downloading", "progress": progress[-5:] if progress else []}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = requests.get(self.api_tags, timeout=5)
            if response.status_code == 200:
                return [m.get("name") for m in response.json().get("models", [])]
            return []
        except:
            return []
    
    def generate(
        self, 
        prompt: str, 
        system: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        context: List[int] = None
    ) -> Optional[str]:
        """Generate text using Gemma 4"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system:
            payload["system"] = system
        if context:
            payload["context"] = context
        
        try:
            response = requests.post(
                self.api_generate,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                print(f"Ollama error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Generation error: {e}")
            return None
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Optional[str]:
        """Chat with Gemma 4"""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(
                self.api_chat,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")
            else:
                print(f"Chat error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Chat error: {e}")
            return None


def interpret_dream_local(
    dream_text: str,
    style: str = "islamic",
    language: str = "ar",
    model: str = "llama3.2"
) -> str:
    """Interpret dream using local Ollama model"""
    ollama = OllamaAI(model=model)
    
    # Check connection
    status = ollama.check_connection()
    if status["status"] != "connected":
        return f"""Warning: Ollama is not connected.

To fix:
1. Install Ollama: https://ollama.com
2. Run: ollama serve
3. Download model: ollama pull {model}

To download: ollama pull gemma4:12b-it-qat"""
    
    # Select style
    prompt_config = DREAM_PROMPTS.get(style, DREAM_PROMPTS["general"])
    system_prompt = prompt_config.get(language, prompt_config["ar"])
    user_prompt = prompt_config.get(language, prompt_config["ar"]).format(dream_text=dream_text)
    
    # Generate interpretation
    result = ollama.generate(
        prompt=user_prompt,
        system=system_prompt,
        temperature=0.7,
        max_tokens=2000
    )
    
    if result:
        return result
    else:
        return f"AI service is not available. Please try again later."


def generate_blog_article_local(
    topic: str,
    language: str = "ar",
    model: str = "llama3.2"
) -> str:
    """Generate blog article using local Ollama model"""
    ollama = OllamaAI(model=model)
    
    if language == "ar":
        system = "You are a specialist in dream interpretation and Islamic culture."
        user = f"""Write a comprehensive blog article (600-800 words) about: {topic}
Include:
1. Engaging introduction
2. Detailed explanation
3. Dream examples and interpretations
4. Valuable tips conclusion
5. SEO-friendly title"""
    else:
        system = "You are a dream interpretation and Islamic culture writer."
        user = f"""Write a comprehensive blog article (600-800 words) about: {topic}
Include:
1. Engaging introduction
2. Detailed explanation
3. Dream examples and interpretations
4. Valuable tips conclusion
5. SEO-friendly title"""
    
    result = ollama.generate(
        prompt=user,
        system=system,
        temperature=0.8,
        max_tokens=2500
    )
    
    return result if result else f"<p>Article about: {topic}</p>"


# ========== CLI Script ==========
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Weaver Ollama - Local AI Dream Interpretation")
    parser.add_argument("--model", default="llama3.2", help="Ollama model")
    parser.add_argument("--check", action="store_true", help="Check connection")
    parser.add_argument("--pull", action="store_true", help="Pull model")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--dream", type=str, help="Interpret a dream")
    parser.add_argument("--style", default="islamic", choices=["islamic", "psychological", "ancient", "general"])
    parser.add_argument("--lang", default="ar", choices=["ar", "en"])
    
    args = parser.parse_args()
    
    ollama = OllamaAI(model=args.model)
    
    if args.check:
        status = ollama.check_connection()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif args.list_models:
        models = ollama.list_models()
        print("Available models:")
        for m in models:
            print(f"  - {m}")
    
    elif args.pull:
        print(f"Downloading {args.model}...")
        result = ollama.pull_model(args.model)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.dream:
        result = interpret_dream_local(
            args.dream,
            style=args.style,
            language=args.lang,
            model=args.model
        )
        print(result)
    
    else:
        # Interactive mode
        print(" Weaver Ollama - Dream Interpretation ")
        print("=" * 40)
        
        status = ollama.check_connection()
        if status["status"] != "connected":
            print("Ollama is not connected")
            print(f"\nTo download: ollama pull {args.model}")
        else:
            print(f"Connected - Model: {args.model}")
            print()
            
            while True:
                dream = input("Enter your dream (or 'exit' to quit):\n> ")
                if dream.lower() == "exit":
                    break
                if dream.strip():
                    print("\nInterpreting...\n")
                    result = interpret_dream_local(dream, model=args.model)
                    print(result)
                    print("\n" + "=" * 40)
