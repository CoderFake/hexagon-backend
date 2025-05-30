from typing import Optional, List
import app.service.news as ns
from app.api.commons import (
    APIRouter,
    Authorized,
    Depends,
    Query,
    Path,
    Response,
    vr,
    maybe_user,
)

router = APIRouter()


@router.get(
    "/categories",
    responses={
        200: {"description": "List of news categories."},
    },
)
async def get_news_categories(
    category_type: Optional[str] = Query(None, description="Filter by category type"),
    course_id: Optional[str] = Query(None, description="Filter by course ID")
) -> List[vr.NewsCategory]:
    """Get all active news categories"""
    categories = (await ns.get_news_categories(
        category_type=category_type,
        course_id=course_id
    )).get()
    return [vr.NewsCategory.of(cat) for cat in categories]


@router.get(
    "/categories/{slug}",
    responses={
        200: {"description": "News category details."},
        404: {"description": "Category not found."},
    },
)
async def get_news_category(
    slug: str = Path(..., description="Category slug")
) -> vr.NewsCategory:
    """Get news category by slug"""
    category = (await ns.get_news_category_by_slug(slug)).get()
    return vr.NewsCategory.of(category)


@router.get(
    "",
    responses={
        200: {"description": "List of news with pagination."},
    },
)
async def get_news_list(
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    category_type: Optional[str] = Query(None, description="Filter by category type"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page")
) -> vr.NewsListResponse:
    """Get news list with pagination"""
    news_list, total = (await ns.get_news_list(
        category_id=category_id,
        category_type=category_type,
        page=page,
        per_page=per_page
    )).get()
    
    total_pages = (total + per_page - 1) // per_page
    
    return vr.NewsListResponse(
        items=[vr.NewsSummary.of(news) for news in news_list],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )


@router.get(
    "/recent",
    responses={
        200: {"description": "Recent news."},
    },
)
async def get_recent_news(
    limit: int = Query(5, ge=1, le=20, description="Number of recent news")
) -> List[vr.NewsSummary]:
    """Get recent published news"""
    news_list = (await ns.get_recent_news(limit=limit)).get()
    return [vr.NewsSummary.of(news) for news in news_list]


@router.get(
    "/featured/{category_type}",
    responses={
        200: {"description": "Featured news by category type."},
    },
)
async def get_featured_news(
    category_type: str = Path(..., description="Category type"),
    limit: int = Query(3, ge=1, le=10, description="Number of featured news")
) -> List[vr.NewsSummary]:
    """Get featured news by category type"""
    news_list = (await ns.get_featured_news(
        category_type=category_type,
        limit=limit
    )).get()
    return [vr.NewsSummary.of(news) for news in news_list]


@router.get(
    "/{slug}",
    responses={
        200: {"description": "News details."},
        404: {"description": "News not found."},
    },
)
async def get_news(
    slug: str = Path(..., description="News slug")
) -> vr.News:
    """Get news details by slug"""
    news = (await ns.get_news_by_slug(slug)).get()

    await ns.increment_view_count(news.id)
    
    return vr.News.of(news) 