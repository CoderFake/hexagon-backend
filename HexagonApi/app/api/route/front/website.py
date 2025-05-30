from typing import Optional, List
import app.service.website as ws
from app.api.commons import (
    APIRouter,
    Depends,
    Query,
    Path,
    Response,
    vr,
)

router = APIRouter()


@router.get(
    "/config",
    responses={
        200: {"description": "Complete website configuration."},
    },
)
async def get_website_config() -> vr.WebsiteConfig:
    """Get complete website configuration including settings, contact info, and banners"""
    settings, contact, banners = (await ws.get_website_config()).get()
    return vr.WebsiteConfig.of(settings, contact, banners)


@router.get(
    "/settings",
    responses={
        200: {"description": "List of site settings."},
    },
)
async def get_site_settings() -> List[vr.SiteSettings]:
    """Get all active site settings"""
    settings = (await ws.get_site_settings()).get()
    return [vr.SiteSettings.of(setting) for setting in settings]


@router.get(
    "/settings/{key}",
    responses={
        200: {"description": "Site setting by key."},
        404: {"description": "Setting not found."},
    },
)
async def get_site_setting(
    key: str = Path(..., description="Setting key")
) -> vr.SiteSettings:
    """Get site setting by key"""
    setting = (await ws.get_site_setting_by_key(key)).get()
    return vr.SiteSettings.of(setting)


@router.get(
    "/contact",
    responses={
        200: {"description": "Contact information."},
        404: {"description": "Contact info not found."},
    },
)
async def get_contact_info() -> vr.ContactInfo:
    """Get contact information"""
    contact = (await ws.get_contact_info()).get()
    return vr.ContactInfo.of(contact)


@router.get(
    "/faqs",
    responses={
        200: {"description": "List of FAQs."},
    },
)
async def get_faqs(
    category_id: Optional[str] = Query(None, description="Filter by course category ID")
) -> List[vr.FAQ]:
    """Get FAQs, optionally filtered by category"""
    faqs = (await ws.get_faqs(category_id=category_id)).get()
    return [vr.FAQ.of(faq) for faq in faqs]


@router.get(
    "/banners",
    responses={
        200: {"description": "List of active banners."},
    },
)
async def get_banners(
    position: Optional[str] = Query(None, description="Filter by banner position (hero, sidebar, footer, popup)")
) -> List[vr.Banner]:
    """Get active banners, optionally filtered by position"""
    banners = (await ws.get_banners(position=position)).get()
    return [vr.Banner.of(banner) for banner in banners] 