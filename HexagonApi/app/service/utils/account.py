import httpx
from app.resources import context as r


async def download_and_save_profile_picture(picture_url: str, user_id: str) -> str:
    """Download and save profile picture from URL"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(picture_url)
            response.raise_for_status()

            file_ext = picture_url.split('.')[-1] if '.' in picture_url else 'jpg'
            if file_ext not in ['jpg', 'jpeg', 'png', 'gif']:
                file_ext = 'jpg'

            storage_path = f"profile_pictures/{user_id}.{file_ext}"

            if hasattr(r.storage, 'write'):
                if 'public' in r.storage.write.__code__.co_varnames:
                    r.storage.write(storage_path, response.content, public=True)
                else:
                    r.storage.write(storage_path, response.content)
            else:
                r.storage.write(storage_path, response.content)

            return r.storage.urlize(storage_path)
            
    except Exception as e:
        r.logger.warning(f"Failed to download profile picture from {picture_url}", exc_info=e)
        return picture_url
