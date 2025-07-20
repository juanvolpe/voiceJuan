import os
import json
from pathlib import Path
from dotenv import load_dotenv
from TTS.api import TTS

class SpanishTTS:
    def __init__(self):
        """Initialize Spanish TTS with voice samples."""
        # Get HF token from environment (set by notebook)
        self.hf_token = os.getenv('HF_TOKEN')
        if not self.hf_token:
            raise ValueError(
                "HF_TOKEN not found. Please make sure it's set in:\n"
                "1. Colab Secrets as 'HF_TOKEN' (recommended)\n"
                "2. Or in a .env file with: HF_TOKEN=your_token_here"
            )

        # Setup paths
        self.voice_dir = "tortoise/voices/juan_es"
        self.samples_dir = os.path.join(self.voice_dir, "samples")
        self.cache_dir = os.path.join(self.voice_dir, "cache")
        
        # Create directories if they don't exist
        os.makedirs(self.voice_dir, exist_ok=True)
        os.makedirs(self.samples_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)

        # Load or create metadata
        self.metadata = self.load_or_create_metadata()
        
        # Initialize TTS with token
        self.tts = TTS(
            "tts_models/multilingual/multi-dataset/xtts_v2",
            progress_bar=True,
            gpu=True
        ).to("cuda")

    def load_or_create_metadata(self):
        """Load metadata if exists, create default if not."""
        metadata_path = os.path.join(self.voice_dir, "metadata.json")
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Create default metadata
        default_metadata = {
            "name": "juan_es",
            "language": "es",
            "description": "Spanish male voice samples",
            "speaker_id": "juan_es",
            "samples_dir": "samples",
            "version": "1.0",
            "settings": {
                "conditioning_latents_cache_path": os.path.join("cache", "conditioning_latents.pth"),
                "use_cache": True,
                "presets": {
                    "ultra_fast": {
                        "num_autoregressive_samples": 1,
                        "diffusion_iterations": 30,
                        "cond_free": False
                    },
                    "fast": {
                        "num_autoregressive_samples": 2,
                        "diffusion_iterations": 50,
                        "cond_free": False
                    },
                    "standard": {
                        "num_autoregressive_samples": 4,
                        "diffusion_iterations": 100,
                        "cond_free": True
                    },
                    "high_quality": {
                        "num_autoregressive_samples": 8,
                        "diffusion_iterations": 200,
                        "cond_free": True
                    }
                }
            }
        }
        
        # Save default metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(default_metadata, f, indent=2)
        
        return default_metadata

    def generate_speech(self, text, preset="standard"):
        """Generate speech from text using specified preset."""
        if not os.listdir(self.samples_dir):
            raise ValueError(
                f"No voice samples found in {self.samples_dir}. "
                "Please upload WAV files using the upload interface."
            )

        # Get preset settings
        settings = self.metadata["settings"]["presets"].get(preset)
        if not settings:
            raise ValueError(
                f"Invalid preset '{preset}'. Available presets: " +
                ", ".join(self.metadata["settings"]["presets"].keys())
            )

        # Generate speech
        output_path = os.path.join(self.voice_dir, "output.wav")
        self.tts.tts_to_file(
            text=text,
            file_path=output_path,
            speaker_wav=os.path.join(self.samples_dir, os.listdir(self.samples_dir)[0]),
            language="es"
        )
        
        return output_path 