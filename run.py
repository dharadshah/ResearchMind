import threading
import uvicorn
import gradio as gr
from app.ui.app import build_ui


def run_api() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)


def run_ui() -> None:
    ui = build_ui()
    ui.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    run_ui()