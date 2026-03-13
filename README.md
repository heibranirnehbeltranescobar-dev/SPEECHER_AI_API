# SPEECHER - Virtual AI Assistant API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![pip](https://img.shields.io/badge/pip-3775A9?style=for-the-badge&logo=pypi&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![WhatsApp API](https://img.shields.io/badge/WhatsApp%20API-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-007800?style=for-the-badge&logo=ffmpeg&logoColor=white)
![ngrok](https://img.shields.io/badge/ngrok-1F1E37?style=for-the-badge&logo=ngrok&logoColor=white)

## 📋 Project Overview

**SPEECHER - RESTful API** is a high-performance backend service built with Python and FastAPI, designed to serve as the core engine for a multimodal Virtual AI Assistant. By integrating Google's GenAI capabilities, this API is built to handle complex, human-like interactions.

## 🚀 Key Features

- **Scalable AI Brain**: A modular foundation built to easily integrate future capabilities (e.g., Vision, NLP, Contextual Memory).
- **RESTful Architecture**: Fully compliant REST API with proper HTTP methods, status codes, and strict JSON payloads.
- **Multimodal Conversational Flow**: Automatically detects if a user sends a text message or a voice note via WhatsApp.
- **Advanced Speech-to-Text (STT)**: Transcribes incoming WhatsApp audio notes using Gemini 1.5 Flash, supporting multiple languages within the same audio.
- **Native AI Voice Generation (TTS)**: Converts AI text responses into high-fidelity audio streams using Gemini’s multimodal capabilities.
- **In-Memory Audio Processing**: Utilizes **FFmpeg** to normalize incoming audio (16kHz mono) and encode outgoing responses to `.ogg` (Opus) for native WhatsApp compatibility without disk latency.
- **Intent Analysis**: Uses AI to determine if the user is implicitly or explicitly asking for a voice response, adapting the output format dynamically.

## 🛠️ Technology Stack

| Component            | Technology                |
| -------------------- | ------------------------- |
| **Framework**        | FastAPI                   |
| **Language**         | Python 3.10+              |
| **AI SDK**           | `google-genai`            |
| **Tunneling**        | `ngrok`                   |
| **Audio Processing** | `FFmpeg` (via Subprocess) |
| **Documentation**    | Swagger UI / ReDoc        |

## 🏗️ Project Architecture

SPEECHER is built using a **Modular Feature-Based Architecture** (Domain-Driven Design). This ensures that as the Virtual Assistant gains new "senses" or skills, the codebase remains clean and maintainable.

```bash
SPEECHER/
├── app/
│   ├── main.py              # Root module & application entry point
│   ├── core/                # Global configurations & shared utilities
│   │   │
│   │   └── providers.py     # Dependency Injection (e.g., GenAI Client)
│   └── api/                 # Assistant's Skills (Feature modules)
│       │
│       └── speech/          # Speech generation module (Skill 1)
│       └── whatsapp/        # AI chat (Skill 2)
├── .env                     # Environment variables
└── requirements.txt         # Project dependencies
```

## 📖 API Documentation (Swagger)

FastAPI automatically generates interactive API documentation based on OpenAPI standards. Once the server is running, you can explore the assistant's growing list of capabilities directly from your browser:

<ul>
<li> <strong>Swagger UI:</strong> Navigate to http://127.0.0.1:8000/docs for an interactive, graphical interface where you can execute requests and test payload structures.</li>
<li> <strong>ReDoc:</strong> Navigate to http://127.0.0.1:8000/redoc for a more detailed, linear documentation format.</li>
</ul>

## 🚀 Installation & Setup

### Prerequisites

<ul>
<li>🚀 <strong>Python 3.10+</strong> - Core programming language</li>
<li>📦 <strong>pip</strong> - Python package manager</li>
<li>🔑 <strong>Google API Key</strong> - Active billing account for Gemini 2.0 multimodal features</li>
</ul>
<li>💬 <strong>Meta for Developers Account</strong> - Access to WhatsApp Cloud API test numbers</li>
<li>🌐 <strong>ngrok</strong> - Secure tunneling tool to expose the local webhook</li>
<li>🔊 <strong>FFmpeg</strong> - Installed and added to the system PATH.</li>
</ul>

## 🤖 AI-Generated Modular Documentation (Skills)

To maintain the project's architecture and seamlessly onboard new AI coding agents or developers, this repository utilizes an automated CLI pipeline to generate modular documentation (often referred to as "Skills").
Instead of writing static guides, you can generate dynamic, up-to-date documentation directly from the current codebase using Google Gemini and CLI tools.

#### Prerequisites for AI Documentation

Ensure you have the following CLI tools installed in your virtual environment:

```bash
pip install files-to-prompt llm llm-gemini
llm keys set gemini # Enter your Google AI Studio API Key when prompted
```

### Generating the Skills Documentation

To scan the core application logic (e.g., endpoints, webhook handlers, and AI integrations) and generate a structured Markdown file containing the project's rules, run the following pipeline in your terminal:

```bash
files-to-prompt app/ main.py | llm -m gemini-1.5-pro "Act as a software architect. I have passed you the source code of my project. Analyze it and generate modular documentation files (AI 'Skills' style). Create a separate Markdown block for each major flow (e.g., how to create new endpoints, how the virtual assistant logic is structured, and how external connections are handled). Document the project rules strictly based on the code you are reading. The resulting documentation must be in English."
```

This command packages the source code, sends it to Gemini, and generates de markdown on the console.

### Environment Configuration

Create a `.env` file in the root directory:

```bash
# AI Provider Configuration
GEMINI_API_KEY=your_google_api_key_here
GEMINI_VOICE_MODEL_AI=voice_model_ai
GEMINI_TEXT_MODEL_AI=text_model_ai

# Meta / WhatsApp API Configuration
META_ACCESS_TOKEN=your_temporary_or_permanent_access_token
META_PHONE_NUMBER_ID=your_phone_number_id
META_WEBHOOK_VERIFY_TOKEN=your_custom_secure_password
```

### Running the Project

<ol>
<li> <strong>Create and activate a virtual environment:</strong>

```bash
py -m venv .venv

# Windows:
.venv\Scripts\activate
```

</li>

<li> <strong>Install dependencies:</strong>

```bash
pip install -r requirements.txt
```

</li>
<li> <strong>Start the development server:</strong>

```bash
uvicorn app.main:app --reload
```

</li>
<li> <strong>Expose the local server to the internet (Terminal 2):</strong>

```bash
ngrok http 8000
```

<em>Note: Copy the https://...ngrok-free.app URL provided by ngrok and use it in your Meta Developer console with the /webhook/ path appended to register your callback URL.</em>

</ol>
