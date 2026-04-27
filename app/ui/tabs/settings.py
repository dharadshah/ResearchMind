import gradio as gr


def build_tab() -> None:
    with gr.Tab("Settings"):
        gr.Markdown("### Settings")
        gr.Markdown("Configure LLM provider, model, and embedding options.")
        gr.Textbox(label="Status", value="Coming in Phase 2", interactive=False)