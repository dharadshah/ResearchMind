import gradio as gr


def build_tab() -> None:
    with gr.Tab("Research Chat"):
        gr.Markdown("### Research Chat")
        gr.Markdown("Ask questions against your ingested documents.")
        gr.Textbox(label="Status", value="Coming in Phase 3", interactive=False)