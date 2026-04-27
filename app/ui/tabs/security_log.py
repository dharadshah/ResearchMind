import gradio as gr


def build_tab() -> None:
    with gr.Tab("Security Log"):
        gr.Markdown("### Security Log")
        gr.Markdown("Audit log of flagged inputs and detected injection attempts.")
        gr.Textbox(label="Status", value="Coming in Phase 5", interactive=False)