# products/chat_views.py
import os, json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from google import genai
from google.genai import types

# client با api key از ENV خوانده می‌شود
GEMINI_KEY = os.environ.get("AIzaSyDdawnzwgquypyTD1njU3BB-uJaVjfdBE8")
client = genai.Client(api_key=GEMINI_KEY)

# system instruction از نمونه‌ی شما (می‌توانید آن را کوتاه/تغییر دهید)
SYSTEM_INSTRUCTION_TEXT = (
    "You are a friendly assistant for our product pages. "
    "Answer concisely in casual english when asked about product specs, shipping, and returns. "
    "Remember, never ask question from users and only answer their questions. "
    "Keep responses reasonably short."
)

@csrf_exempt
def chat_proxy(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_message = body.get("message", "")
    if not user_message:
        return JsonResponse({"error": "message field required"}, status=400)

    # ساختار محتوا برای request به GenAI
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)]
        )
    ]

    generate_content_config = types.GenerateContentConfig(
        system_instruction=[types.Part.from_text(text=SYSTEM_INSTRUCTION_TEXT)],
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )

    try:
        # درخواست غیر-streaming (ساده‌تر)
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",  # یا مدل دلخواه و قابل دسترس شما
            contents=contents,
            config=generate_content_config,
        )

        # استخراج متن از response (جمع‌آوری از candidates/parts)
        reply_text = ""
        if getattr(response, "candidates", None):
            for cand in response.candidates:
                if getattr(cand, "content", None) and getattr(cand.content, "parts", None):
                    for part in cand.content.parts:
                        if getattr(part, "text", None):
                            reply_text += part.text

        # fallback
        if not reply_text:
            reply_text = "Sorry, I couldn't generate an answer."

        return JsonResponse({"reply": reply_text})

    except Exception as e:
        # لاگ کن و به کلاینت خطا بده
        # در production لاگینگ بهتر انجام شود
        return JsonResponse({"error": "AI request failed", "details": str(e)}, status=500)
