import gradio as gr
import requests
from app.constants.app_constants import LLMProvider

API_BASE = "http://localhost:8000"


def fetch_templates() -> dict[str, int]:
    try:
        response = requests.get(f"{API_BASE}/prompt-studio/templates")
        templates = response.json()
        return {t["name"]: t["id"] for t in templates}
    except Exception:
        return {}


def fetch_template_detail(template_id: int) -> dict:
    try:
        response = requests.get(f"{API_BASE}/prompt-studio/templates/{template_id}")
        return response.json()
    except Exception:
        return {}


def on_template_select(template_name: str, template_map: dict) -> tuple:
    if not template_name or template_name not in template_map:
        return "", "", ""
    template_id = template_map[template_name]
    detail = fetch_template_detail(template_id)
    variables = detail.get("variables") or ""
    description = detail.get("description") or ""
    return description, variables, ""


def run_prompt(
    template_name: str,
    template_map: dict,
    variable_input: str,
    provider: str,
) -> tuple:
    if not template_name or template_name not in template_map:
        return "No template selected.", ""

    template_id = template_map[template_name]
    detail = fetch_template_detail(template_id)
    variables = detail.get("variables") or ""

    variable_values = {}
    if variables:
        keys = [v.strip() for v in variables.split(",")]
        pairs = [line.strip() for line in variable_input.strip().splitlines() if "=" in line]
        for pair in pairs:
            k, _, v = pair.partition("=")
            if k.strip() in keys:
                variable_values[k.strip()] = v.strip()

    payload = {
        "template_id": template_id,
        "provider": provider,
        "variable_values": variable_values,
    }

    try:
        response = requests.post(f"{API_BASE}/prompt-studio/run", json=payload)
        data = response.json()
        result = data.get("response", "No response received.")
        latency = data.get("latency_ms", 0)
        return result, f"{latency} ms"
    except Exception as e:
        return f"Error: {str(e)}", ""


def build_tab() -> None:
    template_map_state = gr.State({})

    with gr.Tab("Experiment Studio"):
        gr.Markdown("### Experiment Studio")
        gr.Markdown("Select a prompt template, fill in variables, and run it against an LLM provider.")

        with gr.Row():
            refresh_btn = gr.Button("Refresh Templates", scale=1)
            template_dropdown = gr.Dropdown(
                label="Prompt Template",
                choices=[],
                scale=3,
            )

        description_box = gr.Textbox(
            label="Description",
            interactive=False,
            lines=1,
        )

        variables_box = gr.Textbox(
            label="Variables",
            interactive=False,
            lines=1,
            info="Comma-separated list of variables in this template.",
        )

        variable_input = gr.Textbox(
            label="Variable Values",
            lines=4,
            placeholder="topic=vector databases\naudience=10 year old",
            info="Enter one variable per line in key=value format.",
        )

        provider_dropdown = gr.Dropdown(
            label="LLM Provider",
            choices=LLMProvider.ALL,
            value=LLMProvider.GROQ,
        )

        run_btn = gr.Button("Run Prompt", variant="primary")

        with gr.Row():
            response_box = gr.Textbox(
                label="Response",
                lines=10,
                interactive=False,
                scale=4,
            )
            latency_box = gr.Textbox(
                label="Latency",
                interactive=False,
                scale=1,
            )

        def refresh_templates():
            template_map = fetch_templates()
            choices = list(template_map.keys())
            return gr.update(choices=choices, value=None), template_map

        refresh_btn.click(
            fn=refresh_templates,
            outputs=[template_dropdown, template_map_state],
        )

        template_dropdown.change(
            fn=on_template_select,
            inputs=[template_dropdown, template_map_state],
            outputs=[description_box, variables_box, response_box],
        )

        run_btn.click(
            fn=run_prompt,
            inputs=[template_dropdown, template_map_state, variable_input, provider_dropdown],
            outputs=[response_box, latency_box],
        )