from tortoise.api import TextToSpeech, MODELS_DIR
from tortoise.utils.audio import load_audio, load_voice, load_voices
import torchaudio
import os
import time
import torch
import json
from pathlib import Path

class SpanishTTS:
    def __init__(self):
        print("Initializing Spanish TTS system...")
        self.tts = TextToSpeech(
            models_dir=MODELS_DIR,
            use_deepspeed=False,
            kv_cache=True,
            half=True,
            device="cpu"
        )
        self.voice_dir = "tortoise/voices/juan_es"
        self.load_metadata()
        
    def load_metadata(self):
        """Load Spanish voice metadata"""
        metadata_path = os.path.join(self.voice_dir, "metadata.json")
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
            
    def load_voice_samples(self):
        """Load voice samples with Spanish conditioning"""
        voice_samples = []
        samples_dir = os.path.join(self.voice_dir, "samples")
        
        print("Loading Spanish voice samples...")
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
    
    def preprocess_spanish_text(self, text):
        """Prepare text for Spanish TTS"""
        # Add spaces around punctuation for better parsing
        text = text.replace(".", " . ")
        text = text.replace(",", " , ")
        text = text.replace(";", " ; ")
        text = text.replace(":", " : ")
        text = text.replace("?", " ? ")
        text = text.replace("¿", " ¿ ")
        text = text.replace("!", " ! ")
        text = text.replace("¡", " ¡ ")
        
        # Clean up multiple spaces
        text = " ".join(text.split())
        return text
    
    def generate_speech(self, text, preset='fast', output_file=None):
        """Generate Spanish speech"""
        # Prepare text
        text = self.preprocess_spanish_text(text)
        print(f"\nProcessing Spanish text: '{text}'")
        
        # Load voice samples
        voice_samples = self.load_voice_samples()
        if not voice_samples:
            raise ValueError("No voice samples loaded!")
        
        # Generate output filename if not provided
        if output_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = f"spanish_output_{timestamp}.wav"
        elif not output_file.endswith('.wav'):
            output_file += '.wav'
            
        # Generate speech with Spanish optimization
        print(f"\nGenerating speech with '{preset}' preset...")
        start_time = time.time()
        
        try:
            gen = self.tts.tts_with_preset(
                text,
                voice_samples=voice_samples,
                preset=preset,
                # Spanish-optimized parameters
                k=2,              # Generate more candidates
                temperature=0.8,  # Slightly higher for more natural Spanish
                length_penalty=1.0  # Helps with Spanish rhythm
            )
            
            # Process the generated audio
            if isinstance(gen, list):
                gen = gen[0]  # Take the first generated sample if multiple
            
            # Save the generated audio
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

if __name__ == "__main__":
    # Initialize Spanish TTS
    tts = SpanishTTS()
    
    # Available presets
    presets = ['ultra_fast', 'fast', 'standard', 'high_quality']
    
    print("\nSpanish Tortoise TTS System")
    print("=" * 30)
    
    # Get input text
    text = "Mi nombre es Juan Volpe"  # Using the provided text
    print(f"\nTexto a procesar: {text}")
    
    # Use 'fast' preset by default
    preset = 'fast'
    print(f"\nUsando preset: {preset}")
    
    # Generate with timestamp in filename
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"juan_volpe_{timestamp}.wav"
    
    # Generate speech
    tts.generate_speech(text, preset, output_file) 