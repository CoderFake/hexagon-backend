from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload

import app.model.db as m
import app.model.composite as c
from .commons import service, Maybe, Errors, r


@service
async def get_site_settings(active_only: bool = True) -> Maybe[List[c.SiteSettings]]:
    """Get all site settings"""
    query = select(m.SiteSettings)
    
    if active_only:
        query = query.where(m.SiteSettings.is_active == True)
    
    query = query.order_by(m.SiteSettings.key)
    
    result = await r.tx.execute(query)
    settings = result.scalars().all()
    
    return [c.SiteSettings.of(setting) for setting in settings]


@service
async def get_site_setting_by_key(key: str) -> Maybe[c.SiteSettings]:
    """Get site setting by key"""
    query = select(m.SiteSettings).where(
        and_(
            m.SiteSettings.key == key,
            m.SiteSettings.is_active == True
        )
    )
    
    result = await r.tx.execute(query)
    setting = result.scalar_one_or_none()
    
    if not setting:
        return Errors.DATA_NOT_FOUND
    
    return c.SiteSettings.of(setting)


@service
async def get_contact_info() -> Maybe[c.ContactInfo]:
    """Get active contact information"""
    query = select(m.ContactInfo).where(
        m.ContactInfo.is_active == True
    ).order_by(m.ContactInfo.created_at.desc())
    
    result = await r.tx.execute(query)
    contact = result.scalar_one_or_none()
    
    if not contact:
        return Errors.DATA_NOT_FOUND
    
    return c.ContactInfo.of(contact)


@service
async def get_faqs(
    category_id: Optional[str] = None,
    active_only: bool = True
) -> Maybe[List[c.FAQ]]:
    """Get FAQs"""
    query = select(m.FAQ).options(
        joinedload(m.FAQ.category)
    )
    
    if active_only:
        query = query.where(m.FAQ.is_active == True)
    
    if category_id:
        query = query.where(m.FAQ.category_id == category_id)
    
    query = query.order_by(m.FAQ.order, m.FAQ.question)
    
    result = await r.tx.execute(query)
    faqs = result.scalars().all()
    
    return [c.FAQ.of(faq) for faq in faqs]


@service
async def get_banners(
    position: Optional[str] = None,
    active_only: bool = True
) -> Maybe[List[c.Banner]]:
    """Get banners"""
    query = select(m.Banner)
    
    if active_only:
        query = query.where(m.Banner.is_active == True)
        now = datetime.now()
        query = query.where(
            and_(
                (m.Banner.start_date.is_(None)) | (m.Banner.start_date <= now),
                (m.Banner.end_date.is_(None)) | (m.Banner.end_date >= now)
            )
        )
    
    if position:
        query = query.where(m.Banner.position == position)
    
    query = query.order_by(m.Banner.position, m.Banner.order)
    
    result = await r.tx.execute(query)
    banners = result.scalars().all()
    
    return [c.Banner.of(banner) for banner in banners]


@service
async def get_website_config() -> Maybe[tuple[List[c.SiteSettings], Optional[c.ContactInfo], List[c.Banner]]]:
    """Get complete website configuration"""
    settings_result = await get_site_settings()
    contact_result = await get_contact_info()
    banners_result = await get_banners()
    
    settings = settings_result.get() if settings_result.get() else []
    contact = contact_result.get() if contact_result.get() else None
    banners = banners_result.get() if banners_result.get() else []
    
    return (settings, contact, banners) 