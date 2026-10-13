"""Crawlers ask for /robots.txt first: the answer follows INDEXING_ENABLED."""

from fastapi.testclient import TestClient

from app.main import create_app
from tests.conftest import SettingsFactory
from tests.fakes import FakeDatabaseProbe

BASE = "https://new.example.com"


def test_robots_disallows_everything_while_indexing_is_off(
    make_settings: SettingsFactory,
) -> None:
    app = create_app(make_settings(), db_probe=FakeDatabaseProbe())

    with TestClient(app) as client:
        response = client.get("/robots.txt")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert response.text == "User-agent: *\nDisallow: /\n"


def test_robots_allows_everything_when_indexing_is_on(
    make_settings: SettingsFactory,
) -> None:
    app = create_app(make_settings(INDEXING_ENABLED="true"), db_probe=FakeDatabaseProbe())

    with TestClient(app) as client:
        response = client.get("/robots.txt")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert response.text == "User-agent: *\nAllow: /\n"


def test_robots_is_redirected_in_redirect_mode(make_settings: SettingsFactory) -> None:
    app = create_app(make_settings(REDIRECT_BASE_URL=BASE), db_probe=FakeDatabaseProbe())

    with TestClient(app, follow_redirects=False) as client:
        response = client.get("/robots.txt")

    assert response.status_code == 307
    assert response.headers["location"] == f"{BASE}/robots.txt"
