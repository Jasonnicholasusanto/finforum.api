from pydantic import EmailStr, SecretStr
from app.core.auth import get_supabase_anon_client


async def login_user(email: EmailStr, password: SecretStr):
    supabase_instance = await get_supabase_anon_client()
    pwd = password.get_secret_value()
    result = await supabase_instance.auth.sign_in_with_password(
        {"email": email, "password": pwd}
    )
    if result.user is None or result.session is None:
        raise Exception("Login failed")
    return result

# async def login_user_google():
#     supabase_instance = await get_supabase_anon_client()
#     result = await supabase_instance.auth.sign_in_with_oauth({
#         "provider": "google",
#         "options": {"redirect_to": settings.AUTH_CALLBACK_URL}
#     })
#     url = getattr(result, "url", None) or (result.get("url") if isinstance(result, dict) else None)
#     if not url:
#         raise RuntimeError("Could not get OAuth authorize URL from Supabase.")
#     return url


async def signup_user(email: EmailStr, password: SecretStr):
    supabase_instance = await get_supabase_anon_client()
    pwd = password.get_secret_value()
    result = await supabase_instance.auth.sign_up({"email": email, "password": pwd})
    if result.user is None:
        raise Exception("Sign up failed")
    return result.user
