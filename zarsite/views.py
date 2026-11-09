import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .gemini_service import ask_zar_bot, GeminiChatError


def index_view(request):
    return render(request, "index.html")


@require_POST
def chat_api(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "فرمت درخواست نامعتبر است"}, status=400)

    user_message = data.get("message", "").strip()
    if not user_message:
        return JsonResponse({"error": "پیام نمی‌تواند خالی باشد"}, status=400)

    history = request.session.get("chat_history", [])

    try:
        bot_reply = ask_zar_bot(user_message, history=history)

        history.append({"role": "user", "text": user_message})
        history.append({"role": "model", "text": bot_reply})
        request.session["chat_history"] = history[-10:]

        return JsonResponse({"reply": bot_reply})

    except GeminiChatError as e:
        return JsonResponse({"error": e.user_message}, status=e.status_code)

    except Exception as e:
        print(f"[Unexpected View Error]: {type(e).__name__}: {e}")
        return JsonResponse({"error": "خطای داخلی سرور رخ داد. لطفاً دوباره تلاش کنید"}, status=500)