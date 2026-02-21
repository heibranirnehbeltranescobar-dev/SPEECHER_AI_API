# SPEECHER - Virtual AI Assistant API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)

## 📋 Project Overview

**SPEECHER - RESTful API** is a high-performance backend service built with Python and FastAPI, designed to serve as the core engine for a multimodal Virtual AI Assistant. By integrating Google's GenAI capabilities, this API is built to handle complex, human-like interactions.

## 🚀 Key Features

- **Scalable AI Brain**: A modular foundation built to easily integrate future capabilities (e.g., Vision, NLP, Contextual Memory).
- **RESTful Architecture**: Fully compliant REST API with proper HTTP methods, status codes, and strict JSON payloads.
- **Native AI Audio Generation (Module v1)**: Direct integration with Google Gemini's multimodal capabilities for high-fidelity audio streams.
- **In-Memory Processing**: Streams and packages `.wav` files directly into HTTP responses for zero-latency interactions.

## 🛠️ Technology Stack

| Component         | Technology         |
| ----------------- | ------------------ |
| **Framework**     | FastAPI            |
| **Language**      | Python 3.10+       |
| **AI SDK**        | `google-genai`     |
| **Documentation** | Swagger UI / ReDoc |

## 🏗️ Project Architecture

SPEECHER is built using a **Modular Feature-Based Architecture** (Domain-Driven Design). This ensures that as the Virtual Assistant gains new "senses" or skills, the codebase remains clean and maintainable.

```bash
SPEECHER/
├── app/
│   ├── main.py              # Root module & application entry point
│   ├── core/                # Global configurations & shared utilities
│   │   ├── __init__.py
│   │   └── providers.py     # Dependency Injection (e.g., GenAI Client)
│   └── api/                 # Assistant's Skills (Feature modules)
│       ├── __init__.py
│       └── speech/          # Speech generation module (Skill 1)
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

### Environment Configuration

Create a `.env` file in the root directory:

```bash
# AI Provider Configuration
GEMINI_API_KEY="your_google_api_key_here"
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
</ol>
