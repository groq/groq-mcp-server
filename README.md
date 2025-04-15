# Groq MCP Server

Query models hosted on [Groq](https://console.groq.com/docs/models) for lightning-fast inference directly from Claude and other MCP clients through the [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol).

Use MCP to access vision models for interpreting visual data from images, instantly generate speech from text, process thousands of requests through Groq's [batch processing](https://console.groq.com/docs/batch), and even build apps with full access to Groq's documentation.

With the Groq MCP server you can try tasks like:

### Agentic Tasks, Code Generation & Web Search
- What is Groq's Compound Beta? Use the compound tool. Summarize with one line then turn into voice
- Please retrieve the current Bitcoin price from CoinGecko API and calculate the value of 0.38474 bitcoins?
- What is the weather in SF right now?
- Generate and run code, which means you can make API calls, get data from webpages, and much more

### Vision & Understanding
- "Describe this image [URL to image]"
- "Analyze this image and extract key information as JSON [URL to image]"

### Speech & Audio
- "Convert this text to speech using the Arista-PlayAI voice: [text]"
- "Read this text aloud in Arabic: [text]"
- "Transcribe this audio file using whisper-large-v3: [url to mp3]"
- "Translate this foreign language audio to English [url to mp3]"

### Batch Processing
- "Process the following batch of prompts: [location of a jsonlines file]" (read more [here](https://console.groq.com/docs/batch))



## Quickstart with Claude Desktop

- Get a Groq API key for free at [console.groq.com](https://console.groq.com)
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

If you want to install the MCP from code, scroll down to "Contributing".


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


## Contributing

If you want to contribute or run from source:

### Installation Options

#### Option 1: Quick Setup (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/groq/groq-mcp-server
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

3. Run the Claude install script:
   ```bash
   ./scripts/install.sh
   ```
   On Macs, this will install the Groq MCP server in Claude Desktop, at `~/Library/Application Support/Claude/claude_desktop_config.json`. Make sure to refresh or restart Claude Desktop.

4. Copy `.env.example` to `.env` and add your Groq API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

#### Option 2: Manual Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/groq/groq-mcp-server
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

## Troubleshooting

Logs when running with Claude Desktop can be found at:

- **Windows**: `%APPDATA%\Claude\logs\groq-mcp.log`
- **macOS**: `~/Library/Logs/Claude/groq-mcp.log`


## Acknowledgments

This project is inspired by the [ElevenLabs MCP Server](https://github.com/elevenlabs/elevenlabs-mcp). Thanks!