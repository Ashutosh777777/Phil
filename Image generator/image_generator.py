#!/usr/bin/env python3
"""
Background Image Generator for Author Debate Videos
Supports multiple open-source GenAI services for image generation
"""

import os
import requests
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import time


class ImageGenerator:
    """
    Unified interface for generating images using various open-source GenAI services
    """
    
    def __init__(self, service: str = "stability", api_key: Optional[str] = None, 
                 output_dir: str = "./background_images"):
        """
        Initialize the image generator
        
        Args:
            service: GenAI service to use ('stability', 'replicate', 'huggingface', 'local')
            api_key: API key for the service (if required)
            output_dir: Directory to store generated images
        """
        self.service = service.lower()
        self.api_key = api_key or os.getenv(f"{service.upper()}_API_KEY")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Service configurations
        self.service_configs = {
            'stability': {
                'url': 'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image',
                'headers': lambda: {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            },
            'replicate': {
                'url': 'https://api.replicate.com/v1/predictions',
                'headers': lambda: {
                    'Authorization': f'Token {self.api_key}',
                    'Content-Type': 'application/json'
                }
            },
            'huggingface': {
                'url': 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0',
                'headers': lambda: {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
            },
            'pollinations': {
                # Free, no API key required
                'url': 'https://image.pollinations.ai/prompt/{prompt}',
                'headers': lambda: {}
            }
        }
    
    def generate_image(self, prompt: str, negative_prompt: str = "", 
                      width: int = 1024, height: int = 768,
                      filename: Optional[str] = None) -> str:
        """
        Generate an image based on the prompt
        
        Args:
            prompt: Text description of the desired image
            negative_prompt: Things to avoid in the image
            width: Image width in pixels
            height: Image height in pixels
            filename: Custom filename (auto-generated if None)
            
        Returns:
            Path to the saved image file
        """
        print(f"Generating image using {self.service}...")
        print(f"Prompt: {prompt}")
        
        if self.service == 'stability':
            return self._generate_stability(prompt, negative_prompt, width, height, filename)
        elif self.service == 'replicate':
            return self._generate_replicate(prompt, negative_prompt, width, height, filename)
        elif self.service == 'huggingface':
            return self._generate_huggingface(prompt, negative_prompt, width, height, filename)
        elif self.service == 'pollinations':
            return self._generate_pollinations(prompt, width, height, filename)
        elif self.service == 'local':
            return self._generate_local(prompt, negative_prompt, width, height, filename)
        else:
            raise ValueError(f"Unsupported service: {self.service}")
    
    def _generate_stability(self, prompt: str, negative_prompt: str, 
                           width: int, height: int, filename: Optional[str]) -> str:
        """Generate image using Stability AI"""
        config = self.service_configs['stability']
        
        payload = {
            "text_prompts": [
                {"text": prompt, "weight": 1},
            ],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 30,
        }
        
        if negative_prompt:
            payload["text_prompts"].append({"text": negative_prompt, "weight": -1})
        
        response = requests.post(
            config['url'],
            headers=config['headers'](),
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"Stability AI error: {response.text}")
        
        data = response.json()
        image_data = base64.b64decode(data["artifacts"][0]["base64"])
        
        return self._save_image(image_data, filename, prompt)
    
    def _generate_replicate(self, prompt: str, negative_prompt: str, 
                           width: int, height: int, filename: Optional[str]) -> str:
        """Generate image using Replicate"""
        config = self.service_configs['replicate']
        
        payload = {
            "version": "stability-ai/sdxl:latest",
            "input": {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height
            }
        }
        
        response = requests.post(
            config['url'],
            headers=config['headers'](),
            json=payload
        )
        
        if response.status_code != 201:
            raise Exception(f"Replicate error: {response.text}")
        
        prediction = response.json()
        prediction_url = prediction['urls']['get']
        
        # Poll for completion
        while True:
            response = requests.get(prediction_url, headers=config['headers']())
            prediction = response.json()
            
            if prediction['status'] == 'succeeded':
                image_url = prediction['output'][0]
                image_data = requests.get(image_url).content
                return self._save_image(image_data, filename, prompt)
            elif prediction['status'] == 'failed':
                raise Exception("Image generation failed")
            
            time.sleep(1)
    
    def _generate_huggingface(self, prompt: str, negative_prompt: str, 
                             width: int, height: int, filename: Optional[str]) -> str:
        """Generate image using HuggingFace Inference API"""
        config = self.service_configs['huggingface']
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height
            }
        }
        
        response = requests.post(
            config['url'],
            headers=config['headers'](),
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"HuggingFace error: {response.text}")
        
        return self._save_image(response.content, filename, prompt)
    
    def _generate_pollinations(self, prompt: str, width: int, height: int, 
                               filename: Optional[str]) -> str:
        """Generate image using Pollinations AI (Free, no API key)"""
        # URL encode the prompt
        from urllib.parse import quote
        encoded_prompt = quote(prompt)
        
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
        
        response = requests.get(url)
        
        if response.status_code != 200:
            raise Exception(f"Pollinations error: {response.status_code}")
        
        return self._save_image(response.content, filename, prompt)
    
    def _generate_local(self, prompt: str, negative_prompt: str, 
                       width: int, height: int, filename: Optional[str]) -> str:
        """
        Generate image using local Stable Diffusion installation
        Assumes you have automatic1111 or similar running locally
        """
        url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
        
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": 30,
            "cfg_scale": 7,
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Local SD error: {response.text}")
        
        data = response.json()
        image_data = base64.b64decode(data["images"][0])
        
        return self._save_image(image_data, filename, prompt)
    
    def _save_image(self, image_data: bytes, filename: Optional[str], prompt: str) -> str:
        """Save image data to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Create a safe filename from prompt
            safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_prompt = safe_prompt.replace(' ', '_')
            filename = f"{timestamp}_{safe_prompt}.png"
        
        if not filename.endswith('.png'):
            filename += '.png'
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        print(f"✓ Image saved to: {filepath}")
        return str(filepath)
    
    def generate_debate_background(self, author1: str, author2: str, 
                                   topic: str, style: str = "professional") -> str:
        """
        Generate a background image for an author debate
        
        Args:
            author1: Name of first author
            author2: Name of second author
            topic: Debate topic
            style: Visual style (professional, artistic, minimalist, etc.)
            
        Returns:
            Path to generated image
        """
        # Craft a prompt optimized for debate backgrounds
        prompts_by_style = {
            'professional': f"Professional debate stage background, {author1} vs {author2} discussing {topic}, "
                          f"modern conference room, subtle lighting, podiums, sophisticated atmosphere, "
                          f"4K quality, photorealistic",
            
            'artistic': f"Artistic representation of intellectual debate, {author1} and {author2} discussing {topic}, "
                       f"abstract thought bubbles, philosophical atmosphere, warm colors, painting style",
            
            'minimalist': f"Minimalist debate background, clean design, {topic} theme, "
                         f"simple geometric shapes, professional colors, modern aesthetic",
            
            'classical': f"Classical debate hall, {author1} vs {author2}, {topic} discussion, "
                        f"library setting, books in background, vintage atmosphere, academic style",
            
            'futuristic': f"Futuristic debate interface, {author1} and {author2} discussing {topic}, "
                         f"holographic elements, modern technology, sleek design, sci-fi aesthetic"
        }
        
        prompt = prompts_by_style.get(style, prompts_by_style['professional'])
        
        negative_prompt = "text, words, letters, watermark, logo, signature, people, faces, crowd, ugly, distorted"
        
        filename = f"debate_{author1}_{author2}_{topic[:20]}.png"
        filename = filename.replace(' ', '_').replace('/', '_')
        
        return self.generate_image(prompt, negative_prompt, filename=filename)


def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate background images for author debates')
    parser.add_argument('--service', type=str, default='pollinations',
                       choices=['stability', 'replicate', 'huggingface', 'pollinations', 'local'],
                       help='GenAI service to use')
    parser.add_argument('--api-key', type=str, help='API key for the service')
    parser.add_argument('--prompt', type=str, help='Custom image generation prompt')
    parser.add_argument('--author1', type=str, help='First author name')
    parser.add_argument('--author2', type=str, help='Second author name')
    parser.add_argument('--topic', type=str, help='Debate topic')
    parser.add_argument('--style', type=str, default='professional',
                       choices=['professional', 'artistic', 'minimalist', 'classical', 'futuristic'],
                       help='Background style')
    parser.add_argument('--output-dir', type=str, default='./background_images',
                       help='Output directory for images')
    parser.add_argument('--width', type=int, default=1024, help='Image width')
    parser.add_argument('--height', type=int, default=768, help='Image height')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = ImageGenerator(
        service=args.service,
        api_key=args.api_key,
        output_dir=args.output_dir
    )
    
    # Generate image
    if args.prompt:
        # Custom prompt
        image_path = generator.generate_image(
            prompt=args.prompt,
            width=args.width,
            height=args.height
        )
    elif args.author1 and args.author2 and args.topic:
        # Debate background
        image_path = generator.generate_debate_background(
            author1=args.author1,
            author2=args.author2,
            topic=args.topic,
            style=args.style
        )
    else:
        parser.error("Either --prompt or (--author1, --author2, --topic) must be provided")
    
    print(f"\n🎨 Successfully generated image: {image_path}")


if __name__ == "__main__":
    main()