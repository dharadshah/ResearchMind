import gradio as gr


def build_tab() -> None:
    with gr.Tab("Document Ingestion"):
        gr.Markdown("### Document Ingestion")
        gr.Markdown("Upload documents and ingest them into the vector store.")
        gr.Textbox(label="Status", value="Coming in Phase 3", interactive=False)