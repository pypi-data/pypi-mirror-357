# Slide Stream

🎬 An AI-powered tool to automatically create video presentations from Markdown files.

[![PyPI version](https://badge.fury.io/py/slide-stream.svg)](https://badge.fury.io/py/slide-stream)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Transform your Markdown documents into professional video presentations with AI-powered content enhancement, automatic image sourcing, and natural text-to-speech narration.

## ✨ Features

- 📝 **Markdown to Video**: Convert Markdown files into professional video presentations
- 🤖 **AI Enhancement**: Improve content using OpenAI, Gemini, Claude, Groq, or Ollama
- 🖼️ **Smart Images**: Automatic image sourcing from Unsplash or generate text-based slides
- 🎙️ **Text-to-Speech**: Natural narration using Google Text-to-Speech
- 🎨 **Customizable**: Professional video output with configurable settings
- ⚡ **Modern CLI**: Built with Typer and Rich for excellent user experience

## 🚀 Quick Start

### Installation

```bash
pip install slide-stream
```

### Basic Usage

Create a simple Markdown file:

```markdown
# Welcome to My Presentation

- This is the first point
- Here's another important point
- And a final thought

# Second Slide

- More content here
- Additional information
- Conclusion
```

Generate your video:

```bash
slide-stream create -i presentation.md -o my-video.mp4
```

## 🔧 Installation Options

### Core Installation
```bash
pip install slide-stream
```

### With AI Providers
```bash
# For OpenAI GPT models
pip install slide-stream[openai]

# For Google Gemini
pip install slide-stream[gemini]

# For Anthropic Claude
pip install slide-stream[claude]

# For Groq (fast inference)
pip install slide-stream[groq]

# For all AI providers
pip install slide-stream[all-ai]
```

## 🎯 Usage Examples

### Basic video creation
```bash
slide-stream create -i slides.md -o presentation.mp4
```

### With AI enhancement
```bash
# Set your API key
export OPENAI_API_KEY="your-api-key-here"

# Create enhanced video
slide-stream create \
  -i slides.md \
  -o presentation.mp4 \
  --llm-provider openai \
  --image-source unsplash
```

### Text-only slides (no internet required)
```bash
slide-stream create \
  -i slides.md \
  -o presentation.mp4 \
  --image-source text
```

## 🔑 Environment Variables

Set these environment variables for AI providers:

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-key"

# Google Gemini
export GEMINI_API_KEY="your-gemini-key"

# Anthropic Claude
export ANTHROPIC_API_KEY="your-claude-key"

# Groq
export GROQ_API_KEY="your-groq-key"

# Ollama (local)
export OLLAMA_BASE_URL="http://localhost:11434"
```

## 📋 Requirements

- Python 3.10+
- FFmpeg (for video processing)
- Internet connection (for Unsplash images and AI providers)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- [MoviePy](https://moviepy.readthedocs.io/) for video processing
- [Pillow](https://pillow.readthedocs.io/) for image handling