[Model Context Protocol (MCP)](https://github.com/modelcontextprotocol) server for the [Groq](https://groq.com) API. Fast inference and low latency for multimodal models with vision capabilities for understanding and interpreting visual data from images, instantly generating text to speech, transcribing speech to text, and access to [batch](https://console.groq.com/docs/batch) processing for larger workloads.


## Quickstart with Claude Desktop

1. Get your API key from [Groq Console](https://console.groq.com/home). We have a free tier with generous limits!
2. Install `uv` (Python package manager), install with `curl -LsSf https://astral.sh/uv/install.sh | sh` or see the `uv` [repo](https://github.com/astral-sh/uv) for additional install methods.
3. Go to Claude > Settings > Developer > Edit Config > claude_desktop_config.json to include the following:

```
{
  "mcpServers": {
    "groq": {
      "command": "uvx",
      "args": ["groq-mcp"],
      "env": {
        "GROQ_API_KEY": "your_groq_api_key",
        "BASE_OUTPUT_PATH": "/path/to/output/directory"  # Optional: Where to save generated files (default: ~/Desktop)
      }
    }
  }
}

```

If you're using Windows, you will have to enable "Developer Mode" in Claude Desktop to use the MCP server. Click "Help" in the hamburger menu in the top left and select "Enable Developer Mode".


## Other MCP Clients

For other clients like Cursor and Windsurf:

1. Install the package:
   ```bash
   # Using UV (recommended)
   uvx install groq-mcp

   # Or using pip
   pip install groq-mcp
   ```

2. Generate configuration:
   ```bash
   # Print config to screen
   groq-mcp-config --api-key=your_groq_api_key --print

   # Or save directly to config file (auto-detects location)
   groq-mcp-config --api-key=your_groq_api_key

   # Optional: Specify custom output path
   groq-mcp-config --api-key=your_groq_api_key --output-path=/path/to/outputs
   ```

That's it! Your MCP client can now use these Groq capabilities:

- 🗣️ Text-to-Speech (TTS): Fast, natural-sounding speech synthesis
- 👂 Speech-to-Text (STT): Accurate transcription and translation
- 🖼️ Vision: Advanced image analysis and understanding
- 💬 Chat: Ultra-fast LLM inference with Llama 4 and more
- 📦 Batch: Process large workloads efficiently


## Example Usage

Try asking Claude to use Groq's capabilities:

### Vision & Understanding
- "What's in this image?" (Add a URL)
- "Look at this image and describe what you see in detail"
- "Analyze this image and extract key information as JSON"
- "Examine this diagram and explain its components"

### Speech & Audio
- "Convert this text to speech using the Arista-PlayAI voice"
- "Read this text aloud in Arabic using playai-tts-arabic"
- "Transcribe this audio file using whisper-large-v3"
- "Translate this foreign language audio to English"

## Contributing

If you want to contribute or run from source:

### Installation Options

#### Option 1: Quick Setup (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/groq/groq-mcp
   cd groq-mcp
   ```

2. Run the setup script:
   ```bash
   ./scripts/setup.sh
   ```
   This will:
   - Create a Python virtual environment using `uv`
   - Install all dependencies
   - Set up pre-commit hooks
   - Activate the virtual environment

3. Copy `.env.example` to `.env` and add your Groq API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

#### Option 2: Manual Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/groq/groq-mcp
   cd groq-mcp
   ```

2. Create a virtual environment and install dependencies [using uv](https://github.com/astral-sh/uv):
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

3. Copy `.env.example` to `.env` and add your Groq API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

### Available Scripts

The `scripts` directory contains several utility scripts for different Groq API functionalities:

#### Vision & Image Analysis
```bash
./scripts/groq_vision.sh <image_file> [prompt] [temperature] [max_tokens] [output_directory]
# Example:
./scripts/groq_vision.sh "./input/image.jpg" "What is in this image?"
```

#### Text-to-Speech (TTS)
```bash
./scripts/groq_tts.sh "Your text" [voice_name] [model] [output_directory]
# Example:
./scripts/groq_tts.sh "Hello, world!" "Arista-PlayAI"
```

#### Speech-to-Text (STT)
```bash
./scripts/groq_stt.sh <audio_file> [model] [output_directory]
```

#### Utility Scripts
- `list_groq_voices.sh`: Display available TTS voices
- `list_groq_stt_models.sh`: Show available STT models
- `groq_batch.sh`: Process batch operations
- `groq_translate.sh`: Translate text or audio

#### Development Scripts
```bash
# Run tests
./scripts/test.sh
# Run with options
./scripts/test.sh --verbose --fail-fast
# Run integration tests
./scripts/test.sh --integration

# Debug and test locally
mcp install server.py
mcp dev server.py
```
```

## Troubleshooting

Logs when running with Claude Desktop can be found at:

- **Windows**: `%APPDATA%\Claude\logs\groq-mcp.log`
- **macOS**: `~/Library/Logs/Claude/groq-mcp.log`


## Acknowledgments

This project is inspired by the [ElevenLabs MCP Server](https://github.com/elevenlabs/elevenlabs-mcp). Thanks!