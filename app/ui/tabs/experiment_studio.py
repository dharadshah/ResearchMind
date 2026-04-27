import gradio as gr


def build_tab() -> None:
    with gr.Tab("Experiment Studio"):
        gr.Markdown("### Experiment Studio")
        gr.Markdown("Test and compare prompt templates side by side.")
        gr.Textbox(label="Status", value="Coming in Phase 2", interactive=False)