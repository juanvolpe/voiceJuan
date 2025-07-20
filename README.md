# Spanish Voice Cloning with Tortoise TTS

This project uses Tortoise TTS to clone voices with Spanish language optimization. It includes custom handling for Spanish pronunciation and voice characteristics.

## Features

- Spanish language optimization
- Voice sample management
- Configurable quality presets
- Easy-to-use interface
- Google Colab support

## Project Structure

```
spanish-voice-clone/
├── requirements.txt        # Project dependencies
├── spanish_tortoise.py    # Main TTS script
├── colab_demo.ipynb       # Google Colab notebook
└── voices/                # Voice samples directory
    └── juan_es/          # Spanish voice example
        ├── metadata.json  # Voice metadata
        └── samples/      # Voice sample files
```

## Quick Start

1. Clone the repository:
```bash
git clone [your-repo-url]
cd spanish-voice-clone
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Place your voice samples in `voices/[voice_name]/samples/`

4. Run the script:
```bash
python spanish_tortoise.py
```

## Google Colab Usage

1. Open `colab_demo.ipynb` in Google Colab
2. Follow the notebook instructions
3. Upload your voice samples when prompted

## Voice Sample Requirements

- Format: WAV files (22050 Hz, mono)
- Duration: 5-10 seconds each
- Content: Clear Spanish speech
- Quantity: 3-6 samples recommended

## Quality Presets

- ultra_fast: Fastest generation, lower quality
- fast: Good balance of speed and quality
- standard: Better quality, slower
- high_quality: Best quality, slowest

## Spanish Optimization

The system includes:
- Spanish phoneme handling
- Natural Spanish intonation
- Spanish text preprocessing
- Spanish voice conditioning

## License

MIT License - See LICENSE file for details 