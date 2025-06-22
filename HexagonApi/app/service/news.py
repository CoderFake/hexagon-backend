from typing import List, Optional
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload, joinedload

import app.model.db as m
import app.model.composite as c
from .commons import service, Maybe, Errors, r


@service
async def get_news_categories(
    category_type: Optional[str] = None,
    course_id: Optional[str] = None,
    active_only: bool = True
) -> Maybe[List[c.NewsCategory]]:
    """Get news categories"""
    query = select(m.NewsCategory).options(
        joinedload(m.NewsCategory.course),
        selectinload(m.NewsCategory.news)
    )
    
    if active_only:
        query = query.where(m.NewsCategory.is_active == True)
    
    if category_type:
        query = query.where(m.NewsCategory.category_type == category_type)
    
    if course_id:
        query = query.where(m.NewsCategory.course_id == course_id)
    
    query = query.order_by(m.NewsCategory.order, m.NewsCategory.name)
    
    result = await r.tx.execute(query)
    categories = result.scalars().all()
    return [c.NewsCategory.of(cat) for cat in categories]


@service
async def get_news_category_by_slug(slug: str) -> Maybe[c.NewsCategory]:
    """Get news category by slug"""
    query = select(m.NewsCategory).options(
        joinedload(m.NewsCategory.course),
        selectinload(m.NewsCategory.news)
    ).where(
        and_(
            m.NewsCategory.slug == slug,
            m.NewsCategory.is_active == True
        )
    )
    
    result = await r.tx.execute(query)
    category = result.scalar_one_or_none()
    
    if not category:
        return Errors.DATA_NOT_FOUND
    
    return c.NewsCategory.of(category)


@service
async def get_news_list(
    category_id: Optional[str] = None,
    category_type: Optional[str] = None,
    published_only: bool = True,
    page: int = 1,
    per_page: int = 20
) -> Maybe[tuple[List[c.News], int]]:
    """Get news list with pagination"""
    query = select(m.News).options(
        joinedload(m.News.category).joinedload(m.NewsCategory.course),
        selectinload(m.News.content_blocks)
    )
    
    if published_only:
        query = query.where(
            and_(
                m.News.is_published == True,
                m.News.is_active == True
            )
        )
    elif not published_only:
        query = query.where(m.News.is_active == True)
    
    if category_id:
        query = query.where(m.News.category_id == category_id)
    
    if category_type:
        query = query.join(m.NewsCategory).where(
            m.NewsCategory.category_type == category_type
        )
    
    # Count total
    count_query = select(func.count(m.News.id))
    if published_only:
        count_query = count_query.where(
            and_(
                m.News.is_published == True,
                m.News.is_active == True
            )
        )
    elif not published_only:
        count_query = count_query.where(m.News.is_active == True)
    
    if category_id:
        count_query = count_query.where(m.News.category_id == category_id)
    
    if category_type:
        count_query = count_query.join(m.NewsCategory).where(
            m.NewsCategory.category_type == category_type
        )
    
    total_result = await r.tx.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination and ordering
    query = query.order_by(desc(m.News.published_at), desc(m.News.created_at))
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await r.tx.execute(query)
    news_list = result.scalars().all()
    
    return ([c.News.of(news) for news in news_list], total)


@service
async def get_news_by_slug(slug: str) -> Maybe[c.News]:
    """Get news by slug with all content"""
    query = select(m.News).options(
        joinedload(m.News.category).joinedload(m.NewsCategory.course),
        selectinload(m.News.content_blocks)
    ).where(
        and_(
            m.News.slug == slug,
            m.News.is_published == True,
            m.News.is_active == True
        )
    )
    
    result = await r.tx.execute(query)
    news = result.scalar_one_or_none()
    
    if not news:
        return Errors.DATA_NOT_FOUND
    
    return c.News.of(news)


@service
async def get_news_by_id(news_id: str) -> Maybe[c.News]:
    """Get news by ID"""
    query = select(m.News).options(
        joinedload(m.News.category).joinedload(m.NewsCategory.course),
        selectinload(m.News.content_blocks)
    ).where(
        and_(
            m.News.id == news_id,
            m.News.is_published == True,
            m.News.is_active == True
        )
    )
    
    result = await r.tx.execute(query)
    news = result.scalar_one_or_none()
    
    if not news:
        return Errors.DATA_NOT_FOUND
    
    return c.News.of(news)


@service
async def get_recent_news(limit: int = 5) -> Maybe[List[c.News]]:
    """Get recent published news"""
    query = select(m.News).options(
        joinedload(m.News.category),
        selectinload(m.News.content_blocks)
    ).where(
        and_(
            m.News.is_published == True,
            m.News.is_active == True
        )
    ).order_by(desc(m.News.published_at)).limit(limit)
    
    result = await r.tx.execute(query)
    news_list = result.scalars().all()
    
    return [c.News.of(news) for news in news_list]


@service
async def get_featured_news(category_type: str, limit: int = 3) -> Maybe[List[c.News]]:
    """Get featured news by category type"""
    query = select(m.News).options(
        joinedload(m.News.category),
        selectinload(m.News.content_blocks)
    ).join(m.NewsCategory).where(
        and_(
            m.News.is_published == True,
            m.News.is_active == True,
            m.NewsCategory.category_type == category_type,
            m.NewsCategory.is_active == True
        )
    ).order_by(desc(m.News.published_at)).limit(limit)
    
    result = await r.tx.execute(query)
    news_list = result.scalars().all()
    
    return [c.News.of(news) for news in news_list]


@service
async def increment_view_count(news_id: str) -> Maybe[None]:
    """Increment view count for news"""
    query = select(m.News).where(m.News.id == news_id)
    result = await r.tx.execute(query)
    news = result.scalar_one_or_none()
    
    if news:
        news.view_count += 1
        await r.tx.commit()
    
    return None 