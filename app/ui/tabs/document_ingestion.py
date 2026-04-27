import gradio as gr
import requests

API_BASE = "http://localhost:8000"


def ingest_text(name: str, text: str) -> str:
    if not name or not text:
        return "Please provide both a name and text content."
    try:
        response = requests.post(
            f"{API_BASE}/documents/ingest/text",
            json={"name": name, "text": text},
        )
        data = response.json()
        return (
            f"Document '{data['name']}' ingested successfully.\n"
            f"Status: {data['status']}\n"
            f"Chunks: {data['chunk_count']}"
        )
    except Exception as e:
        return f"Ingestion failed: {str(e)}"


def ingest_url(name: str, url: str) -> str:
    if not name or not url:
        return "Please provide both a name and a URL."
    try:
        response = requests.post(
            f"{API_BASE}/documents/ingest/url",
            json={"name": name, "url": url},
        )
        data = response.json()
        return (
            f"Document '{data['name']}' ingested successfully.\n"
            f"Status: {data['status']}\n"
            f"Chunks: {data['chunk_count']}"
        )
    except Exception as e:
        return f"Ingestion failed: {str(e)}"


def ingest_pdf(name: str, file) -> str:
    if not name or file is None:
        return "Please provide both a name and a PDF file."
    try:
        with open(file.name, "rb") as f:
            response = requests.post(
                f"{API_BASE}/documents/ingest/pdf",
                files={"file": (file.name, f, "application/pdf")},
            )
        data = response.json()
        return (
            f"Document '{data['name']}' ingested successfully.\n"
            f"Status: {data['status']}\n"
            f"Chunks: {data['chunk_count']}"
        )
    except Exception as e:
        return f"Ingestion failed: {str(e)}"


def list_documents() -> str:
    try:
        response = requests.get(f"{API_BASE}/documents/")
        documents = response.json()
        if not documents:
            return "No documents ingested yet."
        lines = []
        for doc in documents:
            lines.append(
                f"[{doc['id']}] {doc['name']} | {doc['document_type']} | "
                f"{doc['chunk_count']} chunks | {doc['status']}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Failed to fetch documents: {str(e)}"


def build_tab() -> None:
    with gr.Tab("Document Ingestion"):
        gr.Markdown("### Document Ingestion")
        gr.Markdown("Ingest documents into the vector store for research.")

        with gr.Tabs():
            with gr.Tab("Text"):
                text_name = gr.Textbox(label="Document Name", placeholder="my_document")
                text_input = gr.Textbox(
                    label="Text Content",
                    lines=8,
                    placeholder="Paste your text content here...",
                )
                text_btn = gr.Button("Ingest Text", variant="primary")
                text_result = gr.Textbox(label="Result", interactive=False)
                text_btn.click(
                    fn=ingest_text,
                    inputs=[text_name, text_input],
                    outputs=text_result,
                )

            with gr.Tab("URL"):
                url_name = gr.Textbox(label="Document Name", placeholder="my_webpage")
                url_input = gr.Textbox(label="URL", placeholder="https://example.com")
                url_btn = gr.Button("Ingest URL", variant="primary")
                url_result = gr.Textbox(label="Result", interactive=False)
                url_btn.click(
                    fn=ingest_url,
                    inputs=[url_name, url_input],
                    outputs=url_result,
                )

            with gr.Tab("PDF"):
                pdf_name = gr.Textbox(label="Document Name", placeholder="my_pdf")
                pdf_file = gr.File(label="Upload PDF", file_types=[".pdf"])
                pdf_btn = gr.Button("Ingest PDF", variant="primary")
                pdf_result = gr.Textbox(label="Result", interactive=False)
                pdf_btn.click(
                    fn=ingest_pdf,
                    inputs=[pdf_name, pdf_file],
                    outputs=pdf_result,
                )

        gr.Markdown("---")
        gr.Markdown("### Ingested Documents")
        refresh_btn = gr.Button("Refresh Document List")
        doc_list = gr.Textbox(label="Documents", interactive=False, lines=8)
        refresh_btn.click(fn=list_documents, outputs=doc_list)