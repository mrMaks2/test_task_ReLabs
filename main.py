from fastapi import FastAPI, WebSocket, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Dict
import json

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


connection_states: Dict[WebSocket, Dict] = {}


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connection_states[websocket] = {"message_counter": 0, "messages": []}
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                message_text = payload.get("message", "")
            except json.JSONDecodeError:
                message_text = "Получен неверный JSON"
            connection_states[websocket]["message_counter"] += 1
            message_counter = connection_states[websocket]["message_counter"]
            formatted_message = f"{message_counter}. {message_text}"
            connection_states[websocket]["messages"].append(formatted_message)
            await websocket.send_text(json.dumps({"type": "new_message", "message": formatted_message}))
    except Exception as e:
        print(f"Ошибка WebSocket: {e}")
    finally:
        print("Websocket отключен")
        del connection_states[websocket]

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)