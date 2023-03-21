import json
import os

from aiohttp import web


WS_FILE = "websocket.html"
POST_FILE = "post.html"
POST_JS_FILE = "post.js"

routes = web.RouteTableDef()


@routes.get('')
async def wshandler(request: web.Request):
    resp = web.WebSocketResponse()
    available = resp.can_prepare(request)
    print(request.path)
    if not available:
        with open(WS_FILE, "rb") as fp:
            return web.Response(body=fp.read(), content_type="text/html")

    await resp.prepare(request)

    await resp.send_str("Welcome!!!")

    try:
        print("Someone joined.")
        # for ws in request.app["sockets"]:
        #     await ws.send_str("Someone joined")
        request.app["sockets"].append(resp)

        async for msg in resp:
            if msg.type == web.WSMsgType.TEXT:
                for ws in request.app["sockets"]:
                    if ws is not resp:
                        await ws.send_str(msg.data)
            else:
                return resp
        return resp

    finally:
        request.app["sockets"].remove(resp)
        print("Someone disconnected.")
        for ws in request.app["sockets"]:
            await ws.send_str("Someone disconnected.")


@routes.post('/news')
async def handle_news_post(request):
    data = await request.json()
    msg = {'news': data['data']}
    for ws in request.app["sockets"]:
        await ws.send_str(data['data'])
    return web.json_response(msg)


@routes.get('/news')
async def handle_news_get(request):
    with open(POST_FILE, "rb") as fp:
        return web.Response(body=fp.read(), content_type="text/html")


@routes.get('/news/post.js')
async def handle_news_js_get(request):
    # with open(POST_FILE, "rb") as fp:
    return web.FileResponse(POST_JS_FILE)


async def on_shutdown(app: web.Application):
    for ws in app["sockets"]:
        await ws.close()


def init():
    app = web.Application()
    app["sockets"] = []
    app.router.add_routes(routes)
    app.on_shutdown.append(on_shutdown)
    return app


web.run_app(init(), host="127.0.0.1")
