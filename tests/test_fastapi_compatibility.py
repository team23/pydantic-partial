from typing import Annotated

import fastapi
import pydantic
import pytest
from httpx import ASGITransport, AsyncClient

from pydantic_partial import PartialModelMixin


class Something(PartialModelMixin, pydantic.BaseModel):
    name: str


class SomethingPartial(Something.model_as_partial()):
    pass


@pytest.fixture
def app():
    app = fastapi.FastAPI()

    @app.post("/something")
    async def something(data: Annotated[SomethingPartial, fastapi.Body()]) -> Something:
        return Something(name=data.name if data.name else "Undefined")

    return app


@pytest.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


def test_openapi_spec_can_be_generated(app):
    assert app.openapi()


@pytest.mark.anyio
async def test_endpoint_accepts_partial_data(client):
    response = await client.post(
        "/something",
        json={},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Undefined"



@pytest.mark.anyio
async def test_endpoint_still_accepts_data(client):
    response = await client.post(
        "/something",
        json={"name": "Some name"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Some name"
