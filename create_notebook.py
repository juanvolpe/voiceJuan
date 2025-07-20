import json

notebook = {
    "nbformat": 4,
    "nbformat_minor": 0,
    "metadata": {
        "colab": {
            "name": "Spanish Voice Cloning with Tortoise TTS",
            "provenance": [],
            "collapsed_sections": [],
            "toc_visible": True
        },
        "kernelspec": {
            "name": "python3",
            "display_name": "Python 3"
        },
        "language_info": {
            "name": "python"
        },
        "accelerator": "GPU"
    },
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {
                "id": "intro"
            },
            "source": [
                "# Spanish Voice Cloning with Tortoise TTS\n",
                "\n",
                "[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/juanvolpe/voiceJuan/blob/main/colab_spanish_tts.ipynb)\n",
                "\n",
                "This notebook will help you:\n",
                "1. Set up the Spanish voice cloning system\n",
                "2. Upload your voice samples\n",
                "3. Generate Spanish speech with your voice"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {
                "id": "token_setup"
            },
            "source": [
                "## Hugging Face Token Setup\n",
                "\n",
                "This notebook uses your Hugging Face token to download models. The token can be set in any of these ways:\n",
                "\n",
                "1. **Colab Secrets (Recommended)**: \n",
                "   - Already set up as \"HF_TOKEN\" in your Colab secrets ✅\n",
                "   - No additional setup needed!\n",
                "\n",
                "2. Environment File:\n",
                "   - Create a `.env` file with `HF_TOKEN=your_token_here`\n",
                "\n",
                "3. Environment Variable:\n",
                "   - Set `HF_TOKEN` directly in your environment\n",
                "\n",
                "First, let's install required packages and check for the token:"
            ]
        },
        {
            "cell_type": "code",
            "metadata": {
                "id": "token_check"
            },
            "source": [
                "# Install required packages\n",
                "!pip install -q python-dotenv\n",
                "\n",
                "# Check for HF token in Colab secrets or .env file\n",
                "import os\n",
                "from dotenv import load_dotenv\n",
                "\n",
                "def get_hf_token():\n",
                "    \"\"\"Get HF token from Colab secrets or .env file\"\"\"\n",
                "    # First try environment variable (could be set directly)\n",
                "    token = os.getenv('HF_TOKEN')\n",
                "    if token:\n",
                "        print(\"✅ Found HF token in environment!\")\n",
                "        return token\n",
                "        \n",
                "    try:\n",
                "        # Try Colab secrets if available\n",
                "        try:\n",
                "            from google.colab import userdata\n",
                "            token = userdata.get('HF_TOKEN')\n",
                "            print(\"✅ Found HF token in Colab secrets!\")\n",
                "            return token\n",
                "        except ImportError:\n",
                "            # Not running in Colab\n",
                "            pass\n",
                "            \n",
                "        # If not in Colab or secrets, try .env file\n",
                "        print(\"⚠️ Checking .env file...\")\n",
                "        load_dotenv()\n",
                "        token = os.getenv('HF_TOKEN')\n",
                "        if not token:\n",
                "            raise ValueError(\n",
                "                \"❌ HF_TOKEN not found! Please either:\\n\"\n",
                "                \"1. Set it in Colab secrets as 'HF_TOKEN'\\n\"\n",
                "                \"2. Create a .env file with HF_TOKEN=your_token_here\\n\"\n",
                "                \"3. Set HF_TOKEN environment variable\"\n",
                "            )\n",
                "        print(\"✅ Found HF token in .env file!\")\n",
                "        return token\n",
                "    except Exception as e:\n",
                "        print(f\"❌ Error getting token: {str(e)}\")\n",
                "        raise\n",
                "\n",
                "# Set the token for use in the TTS system\n",
                "try:\n",
                "    os.environ['HF_TOKEN'] = get_hf_token()\n",
                "    print(\"🚀 Token set successfully! Ready to proceed.\")\n",
                "except Exception as e:\n",
                "    print(f\"❌ Error setting token: {str(e)}\")\n",
                "    raise  # Re-raise to stop execution"
            ],
            "execution_count": None,
            "outputs": []
        },
        {
            "cell_type": "code",
            "metadata": {
                "id": "setup"
            },
            "source": [
                "# Clone repository and install dependencies\n",
                "!git clone https://github.com/juanvolpe/voiceJuan.git\n",
                "%cd voiceJuan\n",
                "\n",
                "print(\"\\n📦 Installing dependencies...\")\n",
                "!pip install -r requirements.txt\n",
                "\n",
                "print(\"\\n✨ Setup complete! Ready to start voice cloning.\")"
            ],
            "execution_count": None,
            "outputs": []
        },
        {
            "cell_type": "markdown",
            "metadata": {
                "id": "upload_intro"
            },
            "source": [
                "## Upload Voice Samples\n",
                "\n",
                "Please prepare your WAV files with these requirements:\n",
                "- Clear Spanish speech\n",
                "- WAV format (22050 Hz)\n",
                "- Good quality audio (no background noise)\n",
                "- 3-10 seconds per sample\n",
                "\n",
                "Use the \"Choose Files\" button below to upload your samples:"
            ]
        },
        {
            "cell_type": "code",
            "metadata": {
                "id": "upload"
            },
            "source": [
                "from google.colab import files\n",
                "import os\n",
                "\n",
                "# Create directories\n",
                "!mkdir -p tortoise/voices/juan_es/samples\n",
                "\n",
                "# Upload interface\n",
                "print(\"📂 Please upload your WAV files...\")\n",
                "uploaded = files.upload()\n",
                "\n",
                "# Save files\n",
                "for filename in uploaded.keys():\n",
                "    if filename.endswith('.wav'):\n",
                "        path = f'tortoise/voices/juan_es/samples/{filename}'\n",
                "        with open(path, 'wb') as f:\n",
                "            f.write(uploaded[filename])\n",
                "        print(f'✅ Saved {filename}')\n",
                "    else:\n",
                "        print(f'❌ Skipped {filename} - not a WAV file')\n",
                "\n",
                "# List all uploaded samples\n",
                "print(\"\\n📊 Uploaded voice samples:\")\n",
                "!ls tortoise/voices/juan_es/samples/"
            ],
            "execution_count": None,
            "outputs": []
        },
        {
            "cell_type": "markdown",
            "metadata": {
                "id": "generate_intro"
            },
            "source": [
                "## Generate Speech\n",
                "\n",
                "Ready to generate speech with your voice samples! You will have two options:\n",
                "1. Use existing voice cache (faster)\n",
                "2. Reprocess voice samples (choose this if you added new samples)\n",
                "\n",
                "Available quality presets:\n",
                "- `ultra_fast`: Quick results, lower quality\n",
                "- `fast`: Good balance of speed/quality\n",
                "- `standard`: Better quality, slower\n",
                "- `high_quality`: Best quality, slowest\n",
                "\n",
                "Run the code below to begin:"
            ]
        },
        {
            "cell_type": "code",
            "metadata": {
                "id": "generate"
            },
            "source": [
                "from spanish_tortoise import SpanishTTS\n",
                "from IPython.display import Audio\n",
                "\n",
                "# Initialize TTS\n",
                "print(\"🎙️ Initializing TTS system...\")\n",
                "tts = SpanishTTS()  # Will ask about cache usage\n",
                "\n",
                "# Get text input\n",
                "text = input(\"✍️ Enter Spanish text: \")\n",
                "\n",
                "# Available presets\n",
                "presets = ['ultra_fast', 'fast', 'standard', 'high_quality']\n",
                "print(\"\\n⚙️ Available quality presets:\")\n",
                "for i, p in enumerate(presets, 1):\n",
                "    print(f\"{i}. {p}\")\n",
                "\n",
                "# Get preset choice\n",
                "while True:\n",
                "    choice = input(\"\\n🎚️ Select quality (1-4) [default=2]: \").strip()\n",
                "    if not choice:\n",
                "        preset = 'fast'\n",
                "        break\n",
                "    try:\n",
                "        idx = int(choice) - 1\n",
                "        if 0 <= idx < len(presets):\n",
                "            preset = presets[idx]\n",
                "            break\n",
                "    except ValueError:\n",
                "        pass\n",
                "    print(\"❌ Please enter a number between 1 and 4\")\n",
                "\n",
                "print(f\"\\n🎵 Generating speech with '{preset}' preset...\")\n",
                "output_file = tts.generate_speech(text, preset=preset)\n",
                "\n",
                "print(\"\\n🔊 Playing generated audio:\")\n",
                "Audio(output_file)"
            ],
            "execution_count": None,
            "outputs": []
        },
        {
            "cell_type": "markdown",
            "metadata": {
                "id": "download_intro"
            },
            "source": [
                "## Download Generated Audio\n",
                "\n",
                "Click below to save the generated audio file to your computer:"
            ]
        },
        {
            "cell_type": "code",
            "metadata": {
                "id": "download"
            },
            "source": [
                "print(\"💾 Starting download...\")\n",
                "files.download(output_file)\n",
                "print(\"✅ Download complete!\")"
            ],
            "execution_count": None,
            "outputs": []
        }
    ]
}

with open('colab_spanish_tts.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2) 