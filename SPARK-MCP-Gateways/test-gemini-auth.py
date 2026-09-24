import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

async def handle_all(request: Request):
    print(f"--- INCOMING {request.method} {request.url.path} ---")
    print(request.headers)
    body = await request.body()
    print(body)
    return JSONResponse({"access_token": "no-oauth-required", "token_type": "bearer", "expires_in": 3600})

app = Starlette(routes=[
    Route("/{path:path}", endpoint=handle_all, methods=["GET", "POST", "HEAD", "OPTIONS"])
])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)
