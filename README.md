# Assistente de Voz com Ollama e Yapper-TTS

Linguagens TTS suportadas, verifique [YapperTTS Enums](https://github.com/n1teshy/yapper-tts/blob/main/yapper/enums.py)

Um sistema completo de assistente de voz que usa Whisper para reconhecimento de fala, Ollama para respostas de IA e Yapper-TTS para síntese de voz em português natural.

# Demo



https://github.com/user-attachments/assets/34e2e290-8f89-481c-bce1-8e2410705142





## Funcionalidades

- 🎤 **Reconhecimento de Fala em Tempo Real** usando Whisper
- 🧠 **Respostas com IA** usando Ollama com modelo personalizado
- 🗣️ **TTS em Português Natural** usando Yapper-TTS com vozes Piper
- 🔇 **Detecção Inteligente de Atividade Vocal** para detectar fala e silêncio
- 🚫 **Sistema Anti-feedback** evita escutar enquanto está falando
- ⚡ **Performance Otimizada** com limitação de tokens e limpeza de respostas

## Pré-requisitos

- Python 3.12+
- Ollama instalado e em execução
- Acesso ao microfone

## Instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/nicolaspiet/robi-assistant.git
   cd ifpi
   ```

2. **Instale as dependências Python**
   ```bash
   pip install -r requirements.txt
   ```

3. **Instale e configure o Ollama**
   ```bash
   # Instale o Ollama em https://ollama.ai/
   ollama serve
   ```

4. **Crie o modelo personalizado do Ollama**
   ```bash
   ollama create meu-assistente -f ./Modelfile
   ```

## Como Usar

Execute o assistente de voz:
```bash
python main.py
```

O assistente irá:
1. Iniciar e cumprimentar com "Olá, em que posso ajudar?"
2. Escutar seus comandos de voz
3. Processar sua fala e gerar respostas de IA
4. Falar as respostas em português natural

## Controles

- **Fale naturalmente** - O sistema detecta fala automaticamente
- **Pressione Ctrl+C** - Para parar o assistente
- **Detecção de silêncio** - Para de escutar após 0.5 segundos de silêncio

## Estrutura do Projeto

```
root/
├── main.py                 # Aplicação principal do assistente de voz
├── requirements.txt        # Dependências Python
├── README.md              # Este arquivo
├── Modelfile              # Configuração do modelo personalizado Ollama
```

## Personalização

### Modificando o Modelo de IA
Edite o `Modelfile` para alterar o prompt do sistema e parâmetros do modelo.

### Alterando a Voz TTS
Modifique a classe `YapperTTS` no `main.py` para usar diferentes vozes Piper.

### Ajustando Configurações VAD
Altere os parâmetros na inicialização do `VoiceAssistant`:
- `threshold`: Sensibilidade VAD (0.1-1.0)
- `silence_duration`: Segundos de silêncio para terminar a fala
- `min_speech_duration`: Duração mínima de fala para processar

## Solução de Problemas

### Problemas de Conexão com Ollama
- Certifique-se que o Ollama está rodando: `ollama serve`
- Verifique se os modelos estão disponíveis: `ollama list`

### Problemas de Áudio
- Verifique permissões do microfone
- Confirme a instalação do PyAudio
- Certifique-se que nenhum outro aplicativo está usando o microfone

### Problemas com TTS
- Verifique a instalação do Yapper-TTS: `pip show yapper-tts`
- Confira as vozes Piper disponíveis na documentação do Yapper
