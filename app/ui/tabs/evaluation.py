import gradio as gr


def build_tab() -> None:
    with gr.Tab("Evaluation"):
        gr.Markdown("### Evaluation")
        gr.Markdown("View TruLens scores for each response.")
        gr.Textbox(label="Status", value="Coming in Phase 5", interactive=False)