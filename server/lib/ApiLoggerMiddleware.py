from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from loguru import logger
import json
import re


def skip_thumb(input: str) -> str:
    # Skip the "thumb" field in the input string
    pattern = r'"thumb":\s*"(.*?)"'
    return re.sub(pattern, '"thumb": "<base64 thumb>"', input)

class ApiLoggerMiddleware(BaseHTTPMiddleware):
    """
    A middleware to log API request and response details.
    Used for debugging.
    """
    async def dispatch(self, request: Request, call_next):
        # 1. filter non-API requests
        if not request.url.path.startswith(("/api")):
            return await call_next(request)

        # 2. log request information
        headers = {name: value for name, value in request.headers.items()}
        body = await request.body()
        body_content = None
        if body:
            body = skip_thumb(body.decode(errors="ignore"))
            try:
                body_content = json.loads(body)
                headers["Content-Type"] = "application/json"
            except json.JSONDecodeError:
                body_content = body[:500]
        logger.debug(
            "\n"
            f"REQUEST: {request.method} {request.url} \n"
            f"Headers: {json.dumps(headers, indent=2)} \n"
            f"Body: {json.dumps(body_content, indent=2) if isinstance(body_content, dict) else body_content}\n\n"
        )

        # 3. create a new request with the original body for downstream handlers
        original_receive = request.receive
        has_been_read = False

        async def receive():
            nonlocal has_been_read
            if not has_been_read:
                has_been_read = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await original_receive()

        request._receive = receive

        # 4. handle the request and get the response
        response = await call_next(request)

        # 4. log response information
        headers = {name: value for name, value in response.headers.items()}
        response_body = b""
        response_body_content = None
        if hasattr(response, "body_iterator"):
            async for chunk in response.body_iterator:  # type: ignore
                response_body += chunk

            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type and response_body:
                response_body = skip_thumb(response_body.decode(errors="ignore")).encode()
                try:
                    response_body_content = json.loads(response_body)
                except json.JSONDecodeError:
                    response_body_content = response_body[:500]
        logger.debug(
            "\n"
            f"RESPONSE: {response.status_code} for {request.method} {request.url}\n"
            f"Headers: {json.dumps(headers, indent=2)} \n"
            f"Body: {json.dumps(response_body_content, indent=2) if isinstance(response_body_content, dict) else response_body_content}\n\n"
        )

        # 5. return a new response with the original body
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
