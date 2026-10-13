"""``GET /robots.txt``: crawl rules that follow the ``INDEXING_ENABLED`` setting."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.adapters.web.dependencies import ContainerDep

router = APIRouter()

DISALLOW_ALL = "User-agent: *\nDisallow: /\n"
ALLOW_ALL = "User-agent: *\nAllow: /\n"


@router.get("/robots.txt", include_in_schema=False)
def robots(container: ContainerDep) -> PlainTextResponse:
    body = ALLOW_ALL if container.settings.indexing_enabled else DISALLOW_ALL
    return PlainTextResponse(body, media_type="text/plain; charset=utf-8")
