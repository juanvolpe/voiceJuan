from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio
import torchaudio
import os
import time
import torch

def generate_voice(text, preset='ultra_fast', output_filename=None, chunk_size=100):
    """
    Generate voice with different quality presets - Optimized for lower-end hardware
    
    presets:
    - ultra_fast: Fastest, lower quality (recommended)
    - fast: Good balance
    - standard: Better quality
    - high_quality: Best quality, slowest
    """
    print("\nInitializing Text-to-Speech with optimized settings...")
    
    # Free up memory
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    # Initialize TTS with optimized settings
    tts = TextToSpeech(
        kv_cache=True,    # Enable KV caching for memory efficiency
        half=True,        # Use half precision
        use_deepspeed=False,  # Disable deepspeed
        device="cpu"      # Force CPU usage
    )
    
    # Load voice samples with memory optimization
    print("Loading voice samples...")
    voice_samples = []
    voice_dir = "tortoise/voices/juan"
    for file in sorted(os.listdir(voice_dir)):
        if file.endswith('.wav'):
            try:
                audio = load_audio(os.path.join(voice_dir, file), 22050)
                voice_samples.append(audio)
                # Clear memory after each load
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception as e:
                print(f"Warning: Could not load {file}: {str(e)}")
    
    # Generate default output filename if none provided
    if output_filename is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_filename = f"output_{preset}_{timestamp}.wav"
    elif not output_filename.endswith('.wav'):
        output_filename += '.wav'
    
    # Split text into chunks if it's too long
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= chunk_size:
            current_chunk.append(word)
            current_length += len(word) + 1
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    # If text is short enough, process as single chunk
    if not chunks:
        chunks = [text]
    
    # Process each chunk
    all_audio = []
    total_start_time = time.time()
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\nProcessing chunk {i}/{len(chunks)}:")
        print(f"Text: '{chunk}'")
        chunk_start_time = time.time()
        
        try:
            gen = tts.tts_with_preset(
                chunk,
                voice_samples=voice_samples,
                preset=preset,
                k=1
            )
            all_audio.append(gen.squeeze(0).cpu())
            
            chunk_duration = time.time() - chunk_start_time
            print(f"Chunk completed in {chunk_duration:.1f} seconds")
            
            # Clear memory after each chunk
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"Error processing chunk: {str(e)}")
            continue
    
    # Combine all audio chunks and save
    if all_audio:
        final_audio = torch.cat(all_audio, dim=1)
        torchaudio.save(output_filename, final_audio, 24000)
        
        total_duration = time.time() - total_start_time
        print(f"\nTotal generation completed in {total_duration:.1f} seconds")
        print(f"Saved to: {output_filename}")
        return output_filename
    else:
        print("No audio was generated successfully")
        return None

if __name__ == "__main__":
    # Available presets
    presets = ['ultra_fast', 'fast', 'standard', 'high_quality']
    
    # Get text input
    print("\nOptimized Tortoise TTS Voice Generator")
    print("=" * 35)
    print("\nRecommended settings for your system:")
    print("- Use 'ultra_fast' preset for best performance")
    print("- Keep text length under 100 characters per generation")
    print("- Longer texts will be automatically split into chunks")
    
    text = input("\nEnter the text to speak: ").strip()
    
    # Show preset options
    print("\nAvailable quality presets:")
    for i, p in enumerate(presets, 1):
        print(f"{i}. {p}" + (" (recommended)" if p == 'ultra_fast' else ""))
    
    # Get preset choice
    while True:
        choice = input("\nSelect preset (1-4) [default=1]: ").strip()
        if not choice:
            preset = 'ultra_fast'  # default to fastest
            break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(presets):
                preset = presets[idx]
                if preset != 'ultra_fast':
                    print("\nNote: Selected preset may be slow on this system.")
                    confirm = input("Continue? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                break
            else:
                print("Please enter a number between 1 and 4")
        except ValueError:
            print("Please enter a valid number")
    
    # Get output filename (optional)
    output_file = input("\nEnter output filename (optional, press Enter for automatic name): ").strip()
    
    # Get chunk size (optional)
    chunk_size = 100  # default
    custom_chunk = input("\nEnter maximum chunk size in characters (optional, press Enter for default 100): ").strip()
    if custom_chunk.isdigit():
        chunk_size = int(custom_chunk)
    
    # Generate the voice
    generate_voice(text, preset, output_file, chunk_size) 