# Voice Assistant with Ollama and Yapper-TTS
Supported TTS languages, check [YapperTTS Enums](https://github.com/n1teshy/yapper-tts/blob/main/yapper/enums.py) 

A complete voice assistant system that uses Whisper for speech recognition, Ollama for AI responses, and Yapper-TTS for natural Portuguese speech synthesis.

## Features

- 🎤 **Real-time Speech Recognition** using Whisper
- 🧠 **AI-Powered Responses** using Ollama with custom model
- 🗣️ **Natural Portuguese TTS** using Yapper-TTS with Piper voices
- 🔇 **Smart Voice Activity Detection** to detect speech and silence
- 🚫 **Anti-feedback System** prevents listening while speaking
- ⚡ **Optimized Performance** with token limiting and response cleaning

## Prerequisites

- Python 3.8+
- Ollama installed and running
- Microphone access

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ifpi
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install and setup Ollama**
   ```bash
   # Install Ollama from https://ollama.ai/
   ollama serve
   ```

4. **Create the custom Ollama model**
   ```bash
   ollama create meu-assistente -f ./Modelfile
   ```

## Usage

Run the voice assistant:
```bash
python main.py
```

The assistant will:
1. Start and greet you with "Olá, em que posso ajudar?"
2. Listen for your voice commands
3. Process your speech and generate AI responses
4. Speak the responses back in natural Portuguese

## Controls

- **Speak naturally** - The system detects speech automatically
- **Press Ctrl+C** - To stop the assistant
- **Silence detection** - Stops listening after 0.5 seconds of silence

## Project Structure

```
ifpi/
├── main.py                 # Main voice assistant application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── Modelfile              # Ollama custom model configuration
└── include/               # TEN VAD library files
    └── ten_vad.py         # Voice Activity Detection
```

## Customization

### Modifying the AI Model
Edit the `Modelfile` to change the system prompt and model parameters.

### Changing TTS Voice
Modify the `YapperTTS` class in `main.py` to use different Piper voices.

### Adjusting VAD Settings
Change the parameters in the `VoiceAssistant` initialization:
- `threshold`: VAD sensitivity (0.1-1.0)
- `silence_duration`: Seconds of silence to end speech
- `min_speech_duration`: Minimum speech length to process

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check if models are available: `ollama list`

### Audio Issues
- Check microphone permissions
- Verify PyAudio installation
- Ensure no other applications are using the microphone

### TTS Problems
- Verify Yapper-TTS installation: `pip show yapper-tts`
- Check available Piper voices in the Yapper documentation
