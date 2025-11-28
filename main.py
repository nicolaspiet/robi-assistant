#
#  Copyright © 2025 Agora
#  This file is part of TEN Framework, an open source project.
#  Licensed under the Apache License, Version 2.0, with certain conditions.
#  Refer to the "LICENSE" file in the root directory for more information.
#
import sys
import os
import numpy as np
import pyaudio
import time
import whisper
import requests
import json
import threading
import pygame
import queue
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../include")))
from ten_vad import TenVad

class YapperTTS:
    def __init__(self):
        # Initialize Yapper with Portuguese speaker
        try:
            from yapper import Yapper, PiperSpeaker
            
            # Create a Portuguese speaker - you might need to check available Portuguese voices
            # Common Portuguese voices might be in PiperVoicePT or similar enum
            try:
                # Try to import Portuguese voice enum if available
                from yapper import PiperVoiceBrazil
                portuguese_speaker = PiperSpeaker(voice=PiperVoiceBrazil.FABER)  # or whatever Portuguese voice is available
            except ImportError:
                # If no specific Portuguese enum, try to use a Brazilian Portuguese voice name directly
                # You might need to check what Portuguese voices are available in Piper
                portuguese_speaker = PiperSpeaker(voice="pt_BR-faber-medium")  # Common Brazilian Portuguese voice
            
            self.yapper = Yapper(speaker=portuguese_speaker)
            print("✅ Yapper-TTS inicializado com sucesso (voz Português)!")
            self.yapper_available = True
            
        except ImportError as e:
            print(f"❌ Yapper-TTS não instalado ou dependências faltando: {e}")
            print("💡 Execute: pip install yapper-tts")
            self.yapper_available = False
        except Exception as e:
            print(f"❌ Erro ao inicializar Yapper-TTS com voz Português: {e}")
            # Fallback to default speaker
            try:
                from yapper import Yapper
                self.yapper = Yapper()
                print("✅ Yapper-TTS inicializado com voz padrão (fallback)")
                self.yapper_available = True
            except:
                self.yapper_available = False

    def speak(self, text):
        """Speak text using Yapper TTS with Portuguese voice"""
        if not text.strip() or not self.yapper_available:
            return False
            
        print("🔊 Convertendo em áudio com Yapper-TTS (Português)...")
        
        try:
            # Use Yapper to speak the text directly in Portuguese
            self.yapper.yap(text, plain=True)
            return True
            
        except Exception as e:
            print(f"❌ Erro no Yapper TTS: {e}")
            return False

    def stop(self):
        """Stop any ongoing playback"""
        # Yapper should handle this internally
        pass

    def cleanup(self):
        """Cleanup resources"""
        # Yapper should handle cleanup internally
        pass

class VoiceAssistant:
    def __init__(self, hop_size=256, threshold=0.5, sample_rate=16000, channels=1, 
                 silence_duration=0.5, min_speech_duration=0.5):
        self.hop_size = hop_size
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.channels = channels
        self.silence_duration = silence_duration
        self.min_speech_duration = min_speech_duration
        
        self.ten_vad = TenVad(hop_size, threshold)
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        self.format = pyaudio.paInt16
        self.chunk_size = hop_size
        
        # Speech recording state
        self.is_recording = False
        self.is_tts_speaking = False  # Track when TTS is active
        self.audio_buffer = []
        self.consecutive_silence_frames = 0
        self.silence_frames_threshold = int(silence_duration * sample_rate / hop_size)
        self.min_speech_frames = int(min_speech_duration * sample_rate / hop_size)
        
        # Load Whisper model
        print("Loading Whisper model...")
        self.model = whisper.load_model("turbo")
        print("Whisper model loaded!")
        
        # Ollama configuration
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "meu-assistente"  # Use your custom model
        
        # TTS engine using Yapper with Portuguese speaker
        print("Inicializando Yapper TTS com voz Português...")
        self.tts_engine = YapperTTS()
        if not self.tts_engine.yapper_available:
            print("❌ Yapper TTS não pôde ser inicializado")
            sys.exit(1)
        
        # Threading
        self.tts_thread = None
        self.stop_tts = threading.Event()
        self.tts_queue = queue.Queue()
        
    def start_voice_assistant(self):
        """Start continuous voice assistant"""
        print(f"Starting Voice Assistant with {self.model_name}...")
        print(f"Sample rate: {self.sample_rate}Hz")
        print(f"VAD Threshold: {self.threshold}")
        print(f"Silence timeout: {self.silence_duration}s")
        print("Press Ctrl+C to stop")
        print("-" * 60)
        
        # Start TTS handler thread
        self._start_tts_handler()
        
        # Welcome message when system starts
        self._speak_text_async("Olá, em que posso ajudar?")
        print("🎤 Fale agora...")
        
        try:
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            frame_count = 0
            
            while True:
                # Read audio data from microphone
                audio_data = stream.read(self.chunk_size, exception_on_overflow=False)
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                
                # Process with VAD
                out_probability, out_flag = self.ten_vad.process(audio_array)
                
                # Handle speech state machine
                self._handle_speech_state(audio_array, out_flag, frame_count)
                
                frame_count += 1
                
        except KeyboardInterrupt:
            print("\n\nParando assistente...")
            self.stop_tts.set()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.stop_tts.set()
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            self.audio.terminate()
            self.tts_engine.cleanup()
    
    def _start_tts_handler(self):
        """Start TTS handler thread"""
        def tts_handler():
            while not self.stop_tts.is_set():
                try:
                    text = self.tts_queue.get(timeout=1.0)
                    if text:
                        self.is_tts_speaking = True  # Set speaking flag
                        self.tts_engine.speak(text)
                        self.is_tts_speaking = False  # Clear speaking flag
                    self.tts_queue.task_done()
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"❌ Erro no handler TTS: {e}")
                    self.is_tts_speaking = False  # Clear flag on error
        
        self.tts_thread = threading.Thread(target=tts_handler)
        self.tts_thread.daemon = True
        self.tts_thread.start()
    
    def _handle_speech_state(self, audio_chunk, vad_flag, frame_count):
        """Handle the state machine for speech start/stop detection"""
        
        # Ignore all speech detection while TTS is speaking
        if self.is_tts_speaking:
            return
        
        # Stop any ongoing TTS if new speech is detected
        if vad_flag == 1 and not self.is_recording:
            self._stop_current_tts()
        
        if vad_flag == 1:  # Speech detected
            self.consecutive_silence_frames = 0
            
            if not self.is_recording:
                # Start recording
                self.is_recording = True
                self.audio_buffer = [audio_chunk]
                print(f"\n🎤 Gravando...")
            else:
                # Continue recording
                self.audio_buffer.append(audio_chunk)
                
        else:  # Silence detected
            if self.is_recording:
                self.consecutive_silence_frames += 1
                
                # Add minimal trailing silence
                if self.consecutive_silence_frames <= 2:
                    self.audio_buffer.append(audio_chunk)
                
                # Check if we've had enough silence to stop recording
                if self.consecutive_silence_frames >= self.silence_frames_threshold:
                    speech_duration = (len(self.audio_buffer) * self.hop_size) / self.sample_rate
                    
                    if speech_duration >= self.min_speech_duration:
                        print(f"💾 Processando...")
                        self._process_speech()
                    else:
                        print(f"❌ Muito curto, ignorando")
                    
                    self.is_recording = False
                    self.audio_buffer = []
                    self.consecutive_silence_frames = 0
    
    def _process_speech(self):
        """Process the captured speech and get response from Ollama"""
        if not self.audio_buffer:
            return
        
        # Convert buffer to single audio array
        full_audio = np.concatenate(self.audio_buffer)
        audio_float = full_audio.astype(np.float32) / 32768.0
        
        # Transcribe using Whisper
        try:
            result = self.model.transcribe(
                audio_float,
                language='pt',
                task='transcribe',
                fp16=False
            )
            
            user_text = result['text'].strip()
            
            if user_text:
                print(f"👤 Você: {user_text}")
                print("🤖 Pensando...")
                
                # Get response from Ollama
                response_text = self._get_ollama_response(user_text)
                print(f"🤖 Assistente: {response_text}")
                
                # Speak the response (non-blocking)
                self._speak_text_async(response_text)
                
                print("🎤 Fale agora...")
                
            else:
                print("🗣️  [Nenhum texto detectado]")
                print("🎤 Fale agora...")
                
        except Exception as e:
            print(f"❌ Erro na transcrição: {e}")
            print("🎤 Fale agora...")
    
    def _get_ollama_response(self, user_message):
        """Get response from Ollama using custom model"""
        try:
            prompt = f"""Lembre: você é um assistente de voz. Responda em texto puro, sem símbolos.

{user_message}"""
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 120
                }
            }
            
            response = requests.post(
                self.ollama_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "Desculpe, não consegui processar sua mensagem.").strip()
                
                # Aggressive cleanup of special characters
                response_text = re.sub(r'[*_#~`|\[\]\(\)]', '', response_text)
                response_text = re.sub(r'\s+', ' ', response_text).strip()
                
                return response_text
            else:
                return f"Erro no Ollama: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "Erro: Não consegui conectar ao Ollama. Verifique se está rodando."
        except requests.exceptions.Timeout:
            return "Erro: Ollama demorou muito para responder."
        except Exception as e:
            return f"Erro inesperado: {str(e)}"
    
    def _speak_text_async(self, text):
        """Add text to TTS queue for async processing"""
        try:
            self.tts_queue.put(text)
        except Exception as e:
            print(f"❌ Erro ao enfileirar TTS: {e}")
    
    def _stop_current_tts(self):
        """Stop any ongoing TTS playback"""
        self.tts_engine.stop()
        # Clear the queue
        while not self.tts_queue.empty():
            try:
                self.tts_queue.get_nowait()
                self.tts_queue.task_done()
            except queue.Empty:
                break

def main():
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama está rodando!")
            models = response.json().get("models", [])
            print("📋 Modelos disponíveis:")
            for model in models:
                print(f"   - {model['name']}")
    except:
        print("❌ Ollama não está rodando! Por favor, inicie o Ollama primeiro.")
        print("   Comando: ollama serve")
        return
    
    # VAD parameters
    hop_size = 256
    threshold = 0.5
    sample_rate = 16000
    silence_timeout = 0.5
    min_speech_duration = 0.5
    
    # Create and start voice assistant
    assistant = VoiceAssistant(
        hop_size=hop_size,
        threshold=threshold,
        sample_rate=sample_rate,
        silence_duration=silence_timeout,
        min_speech_duration=min_speech_duration
    )
    
    assistant.start_voice_assistant()

if __name__ == "__main__":
    main()