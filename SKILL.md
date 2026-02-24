 The project follows a modular Layered Architecture pattern (Routing -> Service -> Core Providers) built on FastAPI.

Below is the technical documentation organized by "Skills" to facilitate maintenance, scaling, and AI understanding of the system.

---

### Skill 1: Project Architecture & Coding Standards
**Overview:** Defines the structural rules and development patterns enforced in the codebase.

*   **Modular Design:** Each feature resides in `app/api/{module_name}`. Every module must contain a `router.py` (entry points), `service.py` (business logic), and `schemas.py` (Pydantic models).
*   **Dependency Injection:** The Google GenAI client is managed in `app/core/providers.py` and injected into routers using FastAPI's `Depends(get_gemini_client)`.
*   **Environment Configuration:** The system strictly uses `.env` for configuration. Keys include:
    *   `GEMINI_API_KEY`: For AI operations.
    *   `GEMINI_VOICE_MODE_AI` / `GEMINI_TEXT_MODE_AI`: Model identifiers.
    *   `META_ACCESS_TOKEN` / `META_PHONE_NUMBER_ID` / `META_WEBHOOK_VERIFY_TOKEN`: WhatsApp integration.
*   **Error Handling:** Services should raise specific exceptions or return `None`, while routers are responsible for returning `HTTPException` to the client.

---

### Skill 2: Extending the API (Creating New Endpoints)
**Process:** How to add a new functionality following the established pattern.

1.  **Define Schema:** Create a Pydantic model in `schemas.py` for request validation.
2.  **Implement Service:** Create a method in `service.py`. If the service requires AI, inject the `genai.Client` via the constructor.
3.  **Define Router:**
    *   Create an `APIRouter` with appropriate tags and prefixes.
    *   Inject the client: `client = Depends(get_gemini_client)`.
    *   Instantiate the service inside the endpoint: `service = NewService(client)`.
4.  **Register Router:** Include the new router in `app/main.py` using `app.include_router()`.

---

### Skill 3: AI Assistant Logic (Gemini Flow)
**Overview:** This skill manages how the AI thinks and decides response formats.

*   **Intent Classification (`wants_audio`):** Before responding, the system uses a low-temperature (0.0) prompt to classify if the user needs an audio response. It expects a strict "yes" or "no" output.
*   **Contextual Generation:**
    *   The assistant acts as a technical support agent.
    *   **Text Mode:** Concise and analytical.
    *   **Audio Mode:** The system automatically modifies the prompt to exclude Markdown (asterisks, bullet points, emojis) to ensure the TTS (Text-to-Speech) produces natural speech.
*   **Speech Generation:** Uses the `GenerateContentConfig` with `AUDIO` modality and the "Puck" voice configuration.


---

### Skill 4: WhatsApp & Meta Integration
**Overview:** Management of external Webhooks and Meta Graph API interactions.

*   **Webhook Verification:** Handled via `GET /webhook`. It compares the `hub.verify_token` against the local environment variable.
*   **Asynchronous Processing:** To prevent Meta timeout (5-second limit), the logic for processing messages and generating AI responses is executed via `BackgroundTasks`.
*   **Messaging Pipeline:**
    1.  Receive Webhook (JSON).
    2.  Send "Typing/Read" indicator to Meta.
    3.  Generate AI response (Text or Audio).
    4.  Upload Media (if audio) to obtain a `media_id`.
    5.  Dispatch the final payload to `https://graph.facebook.com/v22.0/{ID}/messages`.

---

### Skill 5: Media Processing (Audio Engineering)
**Overview:** Handling raw PCM data and converting it for WhatsApp compatibility.

*   **WAV Generation:** The `SpeechService` manually constructs a RIFF/WAV header using the `struct` library to wrap the raw PCM data provided by Gemini (24kHz sample rate).
*   **Opus Conversion:**
    *   WhatsApp requires OGG Opus for native voice note playback.
    *   The system utilizes `subprocess` to call `ffmpeg`.
    *   **Command:** `ffmpeg -i pipe:0 -c:a libopus -f ogg pipe:1`.
    *   *Requirement:* FFmpeg must be installed and available in the system's PATH.
*   **Media Upload:** Audio is uploaded as `audio/wav` (as a filename) but encoded as OGG/Opus to Meta's media endpoints.

---

### Project Rule Checklist (For AI Developers)
1.  **No Logic in Routers:** Routers only handle HTTP-related tasks. Business logic stays in `service.py`.
2.  **Static Headers:** Meta API headers must always include `Authorization: Bearer {token}`.
3.  **Prompt Safety:** When `is_audio_requested` is True, always strip special characters that break TTS flow.
4.  **Async/Sync Balance:** Use `httpx.AsyncClient` for external API calls, but standard `def` for internal CPU-bound logic (like header packing) unless necessary.