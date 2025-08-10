from supabase import create_async_client
from app.core.config import settings
        
        
async def signup_user(email: str, password: str):
    supabase_instance = await create_async_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    result = await supabase_instance.auth.sign_up({"email": email, "password": password})
    if result.user is None:
        raise Exception("Sign up failed")
    return result.user
