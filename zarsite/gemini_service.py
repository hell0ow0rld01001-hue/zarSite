from pathlib import Path
from django.conf import settings
from google import genai
from google.genai import types, errors

client = genai.Client(api_key=settings.GEMINI_API_KEY)

KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge_base"

FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash"
]


class GeminiChatError(Exception):
    """Custom exception carrying a safe Persian message for the UI and an HTTP status code."""
    def __init__(self, user_message: str, status_code: int = 500):
        self.user_message = user_message
        self.status_code = status_code
        super().__init__(user_message)


def load_zar_knowledge() -> str:
    if not KNOWLEDGE_DIR.exists():
        return "اطلاعاتی یافت نشد"

    texts = []
    for file_path in sorted(KNOWLEDGE_DIR.glob("*.txt")):
        content = file_path.read_text(encoding="utf-8").strip()
        if content:
            texts.append(f"--- منبع: {file_path.name} ---\n{content}")

    return "\n\n".join(texts) if texts else "اطلاعاتی یافت نشد"


def get_system_instruction() -> str:
    knowledge = load_zar_knowledge()
    return f"""تو دستیار هوشمند پشتیبانی وب‌سایت «گروه صنعتی زر» هستی
قوانین بسیار مهم:
1. فقط و فقط به زبان فارسی پاسخ بده (حتی اگر کاربر انگلیسی تایپ کرد)
2. لحن تو باید محترمانه، کوتاه، مفید و رسمی باشد
3. فقط بر اساس «اطلاعات مرجع» زیر پاسخ بده. اگر جواب سوالی در متن زیر نبود، از خودت چیزی نساز و بگو: متاسفانه اطلاعات دقیقی در این مورد ندارم، لطفاً با پشتیبانی تماس بگیرید

اطلاعات مرجع گروه زر:
{knowledge}
"""


def ask_zar_bot(user_message: str, history: list[dict] = None) -> str:
    contents = []

    if history:
        for turn in history[-10:]:
            contents.append(
                types.Content(
                    role=turn["role"],
                    parts=[types.Part.from_text(text=turn["text"])],
                )
            )

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        )
    )

    config = types.GenerateContentConfig(
        system_instruction=get_system_instruction(),
        temperature=0.2,
    )

    last_exception = None

    for model_name in FALLBACK_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
            if response and response.text:
                return response.text

            raise GeminiChatError("پاسخ معتبری از هوش مصنوعی دریافت نشد", status_code=502)

        except errors.ServerError as e:
            print(f"[Gemini Fallback] ServerError ({e.code}) on {model_name}. Trying next...")
            last_exception = e
            continue

        except errors.ClientError as e:
            if e.code in (429, 404):
                print(f"[Gemini Fallback] ClientError ({e.code}) on {model_name}. Trying next...")
                last_exception = e
                continue

            if e.code == 403:
                print(f"[Gemini Critical 403]: Access denied (Check VPN/Sanctions or API Key): {e}")
                raise GeminiChatError(
                    "دسترسی سرور به سرویس هوش مصنوعی محدود شده است (خطای ۴۰۳)",
                    status_code=403,
                )

            if e.code == 400:
                print(f"[Gemini Critical 400]: Bad Request / Invalid Key: {e}")
                raise GeminiChatError(
                    "کلید ارتباطی یا درخواست ارسالی به هوش مصنوعی نامعتبر است (خطای ۴۰۰)",
                    status_code=400,
                )

            print(f"[Gemini ClientError {e.code}]: {e}")
            raise GeminiChatError("خطا در پردازش درخواست شما رخ داد", status_code=e.code or 400)

        except GeminiChatError:
            raise

        except Exception as e:
            print(f"[Gemini Network/Connection Error]: {type(e).__name__}: {e}")
            raise GeminiChatError(
                "عدم امکان برقراری ارتباط شبکه با سرویس هوش مصنوعی. لطفاً اتصال سرور را بررسی کنید",
                status_code=503,
            )

    print(f"[Gemini Exhausted All Fallbacks]: Last error was {last_exception}")
    if isinstance(last_exception, errors.ClientError) and last_exception.code == 429:
        raise GeminiChatError(
            "تعداد درخواست‌ها بیش از حد مجاز است. لطفاً یک دقیقه دیگر دوباره تلاش کنید",
            status_code=429,
        )

    raise GeminiChatError(
        "سرورهای هوش مصنوعی در حال حاضر پاسخگو نیستند. لطفاً کمی بعد تلاش کنید",
        status_code=503,
    )