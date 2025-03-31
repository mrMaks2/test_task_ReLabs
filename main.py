from fastapi import FastAPI, WebSocket, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
import json

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    global messages, message_counter
    message_counter = 0
    messages = []
    return templates.TemplateResponse("index.html", {"request": request, "messages": messages})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global message_counter
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                message_text = payload.get("message", "")
            except json.JSONDecodeError:
                message_text = "Invalid JSON received"
            message_counter += 1
            formatted_message = f"{message_counter}. {message_text}"
            messages.append(formatted_message)
            await websocket.send_text(json.dumps({"type": "new_message", "message": formatted_message}))
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print("Websocket disconnected")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)