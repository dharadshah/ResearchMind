import gradio as gr
import app.ui.tabs.document_ingestion as document_ingestion
import app.ui.tabs.research_chat as research_chat
import app.ui.tabs.experiment_studio as experiment_studio
import app.ui.tabs.evaluation as evaluation
import app.ui.tabs.security_log as security_log
import app.ui.tabs.settings as settings


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="ResearchMind") as ui:
        gr.Markdown("# ResearchMind")
        gr.Markdown("AI-powered research assistant")

        document_ingestion.build_tab()
        research_chat.build_tab()
        experiment_studio.build_tab()
        evaluation.build_tab()
        security_log.build_tab()
        settings.build_tab()

    return ui