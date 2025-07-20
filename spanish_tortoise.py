from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio, load_voice, load_voices
import torchaudio
import os
import time
import torch
import json
from pathlib import Path
import numpy as np
import pickle

class SpanishTTS:
    def __init__(self, voice_dir='tortoise/voices/juan_es', use_cached=None):
        """Initialize TTS with optional voice cache"""
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
        self.voice_cache_path = os.path.join(voice_dir, "voice_cache.pkl")
        
        # Check if cache exists
        cache_exists = os.path.exists(self.voice_cache_path)
        
        # If use_cached not specified, ask user
        if use_cached is None and cache_exists:
            print("\nFound existing voice cache.")
            print("Options:")
            print("1. Use existing voice cache (faster)")
            print("2. Reprocess voice samples (use if you've added new samples)")
            while True:
                choice = input("\nEnter choice (1 or 2): ").strip()
                if choice in ['1', '2']:
                    self.use_cached = (choice == '1')
                    break
                print("Please enter 1 or 2")
        else:
            self.use_cached = use_cached if use_cached is not None else False
        
        self.load_metadata()
        
    def load_metadata(self):
        """Load voice metadata"""
        metadata_path = os.path.join(self.voice_dir, "metadata.json")
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
            
        # Check for new samples
        samples_dir = os.path.join(self.voice_dir, "samples")
        current_samples = set(os.path.basename(s['file']) for s in self.metadata['samples'])
        actual_samples = set(f for f in os.listdir(samples_dir) if f.endswith('.wav'))
        
        if actual_samples != current_samples:
            print("\nDetected changes in voice samples:")
            new_samples = actual_samples - current_samples
            removed_samples = current_samples - actual_samples
            
            if new_samples:
                print("New samples found:", ', '.join(new_samples))
            if removed_samples:
                print("Removed samples:", ', '.join(removed_samples))
            
            if self.use_cached:
                print("\nWarning: Voice samples have changed. Consider reprocessing.")
                while True:
                    choice = input("Reprocess samples? (y/n): ").strip().lower()
                    if choice in ['y', 'n']:
                        self.use_cached = (choice == 'n')
                        break
            
            # Update metadata
            self.metadata['samples'] = [
                {
                    "file": f"samples/{f}",
                    "language": "es",
                    "use_phonemes": True
                }
                for f in actual_samples
            ]
            
            # Save updated metadata
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
            
    def load_voice_samples(self):
        """Load voice samples with caching"""
        # Check for cached voice conditioning
        if self.use_cached and os.path.exists(self.voice_cache_path):
            print("Loading cached voice conditioning...")
            try:
                with open(self.voice_cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading cache: {str(e)}")
                print("Falling back to processing samples...")
                self.use_cached = False
        
        # Load and process voice samples
        voice_samples = []
        print("Processing voice samples...")
        for sample in self.metadata["samples"]:
            try:
                file_path = os.path.join(self.voice_dir, sample["file"])
                if os.path.exists(file_path):
                    audio = load_audio(file_path, 22050)
                    voice_samples.append(audio)
                    print(f"Processed {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Error processing {sample['file']}: {str(e)}")
        
        # Cache the processed samples
        if voice_samples:
            print("Saving voice conditioning cache...")
            try:
                with open(self.voice_cache_path, 'wb') as f:
                    pickle.dump(voice_samples, f)
                print("Voice cache saved successfully")
            except Exception as e:
                print(f"Error saving cache: {str(e)}")
        
        return voice_samples
    
    def preprocess_spanish_text(self, text):
        """Prepare text for Spanish TTS"""
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
    
    def generate_speech(self, text, preset='fast', output_file=None):
        """Generate Spanish speech"""
        # Process text
        text = self.preprocess_spanish_text(text)
        print(f"\nProcessing text: '{text}'")
        
        # Load samples (using cache if available)
        start_time = time.time()
        voice_samples = self.load_voice_samples()
        load_time = time.time() - start_time
        print(f"Voice loading time: {load_time:.1f} seconds")
        
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
        gen_start_time = time.time()
        
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
            
            # Process output
            if isinstance(gen, list):
                gen = gen[0]
            
            # Save audio
            torchaudio.save(
                output_file,
                gen.squeeze(0).cpu(),
                24000
            )
            
            gen_time = time.time() - gen_start_time
            total_time = time.time() - start_time
            print(f"\nGeneration time: {gen_time:.1f} seconds")
            print(f"Total processing time: {total_time:.1f} seconds")
            print(f"Saved to: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"Error generating speech: {str(e)}")
            return None

if __name__ == "__main__":
    # Initialize Spanish TTS
    tts = SpanishTTS()  # Will ask about cache usage
    
    # Available presets
    presets = ['ultra_fast', 'fast', 'standard', 'high_quality']
    
    print("\nSpanish Tortoise TTS System")
    print("=" * 30)
    
    # Get input text
    text = input("\nIngrese el texto en español: ").strip()
    
    # Show preset options
    print("\nNiveles de calidad disponibles:")
    for i, p in enumerate(presets, 1):
        print(f"{i}. {p}")
    
    # Get preset choice
    while True:
        choice = input("\nSeleccione calidad (1-4) [default=2]: ").strip()
        if not choice:
            preset = 'fast'
            break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(presets):
                preset = presets[idx]
                break
            else:
                print("Por favor ingrese un número entre 1 y 4")
        except ValueError:
            print("Por favor ingrese un número válido")
    
    # Get output filename (optional)
    output_file = input("\nNombre del archivo de salida (opcional, Enter para nombre automático): ").strip()
    
    # Generate speech
    tts.generate_speech(text, preset, output_file) 