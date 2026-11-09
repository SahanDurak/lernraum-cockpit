from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

NO_FRONTEND = Path("/does/not/exist")


@pytest.fixture
def frontend_dist(tmp_path: Path) -> Path:
    # A file next to dist/ must never be reachable via path traversal.
    (tmp_path / "secret.txt").write_text("secret")
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<html>cockpit</html>")
    (dist / "assets" / "app.js").write_text("console.log('hi')")
    return dist


def test_health() -> None:
    client = TestClient(create_app(frontend_dist=NO_FRONTEND))
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_without_frontend_build_only_api_is_served() -> None:
    client = TestClient(create_app(frontend_dist=NO_FRONTEND))
    assert client.get("/").status_code == 404


def test_serves_frontend_files(frontend_dist: Path) -> None:
    client = TestClient(create_app(frontend_dist=frontend_dist))
    assert client.get("/").text == "<html>cockpit</html>"
    assert client.get("/assets/app.js").text == "console.log('hi')"


# "/apifoo" only starts with "api" as text, it is not under /api, so it is a client route.
@pytest.mark.parametrize("path", ["/courses/42", "/apifoo"])
def test_client_routes_fall_back_to_index(frontend_dist: Path, path: str) -> None:
    client = TestClient(create_app(frontend_dist=frontend_dist))
    response = client.get(path)
    assert response.status_code == 200
    assert response.text == "<html>cockpit</html>"


def test_head_on_client_route_falls_back_to_index(frontend_dist: Path) -> None:
    client = TestClient(create_app(frontend_dist=frontend_dist))
    assert client.head("/courses/42").status_code == 200


@pytest.mark.parametrize(
    "path", ["/../secret.txt", "/%2e%2e/secret.txt", "/assets/..%2f..%2fsecret.txt"]
)
def test_path_traversal_does_not_leave_dist(frontend_dist: Path, path: str) -> None:
    client = TestClient(create_app(frontend_dist=frontend_dist))
    assert "secret" not in client.get(path).text


@pytest.mark.parametrize("path", ["/api", "/api/unknown"])
def test_unknown_api_paths_stay_404(frontend_dist: Path, path: str) -> None:
    client = TestClient(create_app(frontend_dist=frontend_dist))
    response = client.get(path)
    assert response.status_code == 404
    assert "cockpit" not in response.text


def test_missing_assets_stay_404(frontend_dist: Path) -> None:
    # A stale cached page asking for an old bundle must not get index.html as JavaScript.
    client = TestClient(create_app(frontend_dist=frontend_dist))
    response = client.get("/assets/missing.js")
    assert response.status_code == 404
    assert "cockpit" not in response.text
