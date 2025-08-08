from supabase import create_client
from app.core.config import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

async def signup_user(email: str, password: str):
    result = await supabase.auth.sign_up({"email": email, "password": password})
    if result.user is None:
        raise Exception("Signup failed")
    return result.user
