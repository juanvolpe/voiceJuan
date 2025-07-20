import torch
import torchaudio
import numpy as np
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio, load_voice, load_voices
import os

def generate_speech(text, voice_samples=None, voice_dir=None, output_path=None):
    """
    Generate speech using Tortoise TTS
    :param text: Text to convert to speech
    :param voice_samples: List of paths to voice samples
    :param voice_dir: Directory containing voice samples
    :param output_path: Path to save the generated audio
    """
    # Initialize Tortoise TTS
    print("Initializing Tortoise TTS...")
    tts = TextToSpeech()
    
    # Load voice samples
    if voice_dir and os.path.exists(voice_dir):
        print(f"Loading voice samples from {voice_dir}")
        # Load all wav files from the directory
        voice_samples = []
        for file in sorted(os.listdir(voice_dir)):
            if file.endswith('.wav'):
                file_path = os.path.join(voice_dir, file)
                print(f"Loading {file}")
                audio = load_audio(file_path, 22050)
                voice_samples.append(audio)
        
        if not voice_samples:
            raise ValueError(f"No WAV files found in {voice_dir}")
    elif voice_samples:
        print("Using provided voice samples")
        voice_samples = [load_audio(p, 22050) for p in voice_samples]
    else:
        raise ValueError("Either voice_dir or voice_samples must be provided")
    
    # Generate speech
    print(f"Generating speech for text: '{text}'")
    gen = tts.tts_with_preset(
        text,
        voice_samples=voice_samples,
        preset='fast',
        k=1
    )
    
    # Save the generated audio
    if output_path:
        print(f"Saving audio to {output_path}")
        torchaudio.save(output_path, gen.squeeze(0).cpu(), 24000)
    
    print("Speech generation complete!")
    return gen

if __name__ == "__main__":
    # Example usage
    text = "Hola, mi nombre es Juan y soy Argentino"
    voice_dir = "tortoise/voices/juan"
    output_path = "output_spanish.wav"
    
    try:
        print("Starting speech generation process...")
        generate_speech(text, voice_dir=voice_dir, output_path=output_path)
        print(f"Speech generated successfully and saved to {output_path}")
    except Exception as e:
        print(f"Error during speech generation: {str(e)}")
        import traceback
        traceback.print_exc() 