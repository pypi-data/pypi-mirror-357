import os
import requests
import google.generativeai as genai

class AI:
    """
    Simple AI class for text and image generation
    Uses Google Gemini for text and Hugging Face for images
    """
    
    def __init__(self, gemini_api_key=None, hf_api_key=None):
        # Gemini setup
        self.gemini_api_key = gemini_api_key or os.environ.get('GEMINI_API_KEY')
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
        # Hugging Face setup
        self.hf_api_key = hf_api_key or os.environ.get('HF_API_KEY')
    
    def answer(self, question):
        """Get text response from AI"""
        try:
            response = self.model.generate_content(question)
            return response.text
        except:
            return "Error generating response"
    
    def image(self, prompt, save_path):
        """Generate and save image"""
        models = [
            "black-forest-labs/FLUX.1-dev",
            "runwayml/stable-diffusion-v1-5",
            "stabilityai/stable-diffusion-2-1"
        ]
        
        for model in models:
            if self._try_generate_image(model, prompt, save_path):
                return save_path
        
        return "Error: Could not generate image"
    
    def _try_generate_image(self, model, prompt, save_path):
        """Try to generate image with specific model"""
        try:
            url = f"https://api-inference.huggingface.co/models/{model}"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            response = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=60)
            
            if response.status_code == 200 and len(response.content) > 1000:
                # Create directory if needed
                os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
                
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return True
        except:
            pass
        return False





#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
#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
#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
#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
#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
#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
#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
#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
#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
#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
#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
#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