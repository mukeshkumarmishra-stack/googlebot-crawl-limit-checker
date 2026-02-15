from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import httpx

app = FastAPI(title="HTML Size Checker")


class URLRequest(BaseModel):
    url: HttpUrl


class HTMLSizeResponse(BaseModel):
    url: HttpUrl
    size_bytes: int


@app.post("/html-size", response_model=HTMLSizeResponse)
async def get_html_size(payload: URLRequest) -> HTMLSizeResponse:
    """Fetch a page asynchronously and return HTML payload size in bytes."""
    timeout = httpx.Timeout(10.0, connect=5.0)

    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(str(payload.url))
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Timed out while fetching the URL") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Upstream server returned HTTP {exc.response.status_code}",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch URL: {exc}") from exc

    return HTMLSizeResponse(url=payload.url, size_bytes=len(response.content))
