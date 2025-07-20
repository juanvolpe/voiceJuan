from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio
import torchaudio
import os
import time
import torch
import json
from pathlib import Path
import numpy as np

class SpanishTTSColab:
    def __init__(self, voice_dir='voices/custom_voice'):
        """Initialize TTS with Colab optimizations"""
        print("Initializing Spanish TTS system...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        self.tts = TextToSpeech(
            use_deepspeed=False,
            kv_cache=True,
            half=True,
            device=self.device
        )
        self.voice_dir = voice_dir
        self.load_metadata()
        
    def load_metadata(self):
        """Load or create metadata for voice samples"""
        metadata_path = os.path.join(self.voice_dir, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            # Create metadata for samples
            samples_dir = os.path.join(self.voice_dir, "samples")
            self.metadata = {
                "language": "es",
                "sampling_rate": 22050,
                "samples": [
                    {
                        "file": f"samples/{f}",
                        "language": "es",
                        "use_phonemes": True
                    }
                    for f in os.listdir(samples_dir)
                    if f.endswith('.wav')
                ]
            }
            # Save metadata
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
    
    def preprocess_spanish_text(self, text):
        """Optimize text for Spanish TTS"""
        # Common Spanish abbreviations
        abbreviations = {
            'Sr.': 'Señor',
            'Sra.': 'Señora',
            'Dr.': 'Doctor',
            'Dra.': 'Doctora',
            'Ud.': 'Usted',
            'Uds.': 'Ustedes',
        }
        
        # Replace abbreviations
        for abbr, full in abbreviations.items():
            text = text.replace(abbr, full)
        
        # Add spaces around punctuation
        text = text.replace(".", " . ")
        text = text.replace(",", " , ")
        text = text.replace(";", " ; ")
        text = text.replace(":", " : ")
        text = text.replace("?", " ? ")
        text = text.replace("¿", " ¿ ")
        text = text.replace("!", " ! ")
        text = text.replace("¡", " ¡ ")
        
        # Clean up spaces
        return " ".join(text.split())
    
    def load_voice_samples(self):
        """Load voice samples with Colab optimization"""
        voice_samples = []
        print("Loading voice samples...")
        
        for sample in self.metadata["samples"]:
            try:
                file_path = os.path.join(self.voice_dir, sample["file"])
                if os.path.exists(file_path):
                    audio = load_audio(file_path, 22050)
                    voice_samples.append(audio)
                    print(f"Loaded {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Error loading {sample['file']}: {str(e)}")
        
        return voice_samples
    
    def generate_speech(self, text, preset='fast', output_file=None, **kwargs):
        """Generate Spanish speech with Colab optimization"""
        # Process text
        text = self.preprocess_spanish_text(text)
        print(f"\nProcessing text: '{text}'")
        
        # Load samples
        voice_samples = self.load_voice_samples()
        if not voice_samples:
            raise ValueError("No voice samples loaded!")
        
        # Set output filename
        if output_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = f"spanish_output_{timestamp}.wav"
        elif not output_file.endswith('.wav'):
            output_file += '.wav'
        
        # Generate speech
        print(f"\nGenerating speech with '{preset}' preset...")
        start_time = time.time()
        
        try:
            # Default parameters optimized for Spanish
            params = {
                'k': 2,
                'temperature': 0.8,
                'length_penalty': 1.0,
            }
            params.update(kwargs)  # Update with any custom parameters
            
            gen = self.tts.tts_with_preset(
                text,
                voice_samples=voice_samples,
                preset=preset,
                **params
            )
            
            # Process output
            if isinstance(gen, list):
                gen = gen[0]
            
            # Save audio
            torchaudio.save(
                output_file,
                gen.squeeze(0).cpu(),
                24000
            )
            
            duration = time.time() - start_time
            print(f"\nGeneration completed in {duration:.1f} seconds")
            print(f"Saved to: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"Error generating speech: {str(e)}")
            return None

def generate_sample_colab(text, voice_dir='voices/custom_voice', preset='fast', output_file=None):
    """Helper function for easy Colab usage"""
    tts = SpanishTTSColab(voice_dir)
    return tts.generate_speech(text, preset, output_file) 