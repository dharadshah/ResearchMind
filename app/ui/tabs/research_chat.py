import gradio as gr
import requests

API_BASE = "http://localhost:8000"


def send_message(
    message: str,
    history: list,
    conversation_id: int | None,
    use_hitl: bool,
) -> tuple:
    if not message.strip():
        return history, conversation_id, "", ""

    if use_hitl:
        try:
            payload = {"question": message}
            if conversation_id:
                payload["conversation_id"] = conversation_id

            response = requests.post(
                f"{API_BASE}/research/hitl/start",
                json=payload,
            )
            data = response.json()
            thread_id = data.get("thread_id", "")
            intent = data.get("intent", "")
            conv_id = data.get("conversation_id", conversation_id)

            pending_msg = (
                f"Agent paused after intent classification.\n"
                f"Detected intent: {intent}\n"
                f"Thread ID: {thread_id}\n\n"
                f"Use the HITL Resume panel below to approve or override."
            )
            history = history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": pending_msg},
            ]
            return history, conv_id, thread_id, intent
        except Exception as e:
            history = history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": f"Error: {str(e)}"},
            ]
            return history, conversation_id, "", ""
    else:
        try:
            payload = {"question": message}
            if conversation_id:
                payload["conversation_id"] = conversation_id

            response = requests.post(
                f"{API_BASE}/research/query",
                json=payload,
            )
            data = response.json()
            conv_id = data.get("conversation_id", conversation_id)
            agent_used = data.get("agent_used", "")
            intent = data.get("intent", "")
            tools_used = ", ".join(data.get("tools_used", []))
            answer = data.get("response", "No response received.")

            meta = f"\n\n[Agent: {agent_used} | Intent: {intent} | Tools: {tools_used}]"
            history = history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": answer + meta},
            ]
            return history, conv_id, "", intent
        except Exception as e:
            history = history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": f"Error: {str(e)}"},
            ]
            return history, conversation_id, "", ""


def resume_hitl(
    thread_id: str,
    conversation_id: int | None,
    approved: bool,
    override_intent: str,
    history: list,
) -> tuple:
    if not thread_id:
        return history, "No active HITL session to resume."
    try:
        payload = {
            "thread_id": thread_id,
            "approved": approved,
            "conversation_id": conversation_id or 1,
        }
        if override_intent:
            payload["override_intent"] = override_intent

        response = requests.post(
            f"{API_BASE}/research/hitl/resume",
            json=payload,
        )
        data = response.json()
        agent_used = data.get("agent_used", "")
        intent = data.get("intent", "")
        tools_used = ", ".join(data.get("tools_used", []))
        answer = data.get("response", "No response received.")

        meta = f"\n\n[Agent: {agent_used} | Intent: {intent} | Tools: {tools_used}]"
        last_question = history[-2]["content"] if len(history) >= 2 else ""
        history = history[:-2] + [
            {"role": "user", "content": last_question},
            {"role": "assistant", "content": answer + meta},
        ]
        return history, "HITL session completed."
    except Exception as e:
        return history, f"Resume failed: {str(e)}"


def build_tab() -> None:
    conversation_id_state = gr.State(None)
    thread_id_state = gr.State("")
    intent_state = gr.State("")

    with gr.Tab("Research Chat"):
        gr.Markdown("### Research Chat")
        gr.Markdown(
            "Ask questions against your ingested documents. "
            "Enable HITL to review the agent intent before it runs."
        )

        chatbot = gr.Chatbot(
            label="Conversation",
            height=400,
        )

        with gr.Row():
            message_input = gr.Textbox(
                label="Your Question",
                placeholder="What is retrieval augmented generation?",
                scale=4,
            )
            use_hitl = gr.Checkbox(label="Enable HITL", value=False, scale=1)

        with gr.Row():
            send_btn = gr.Button("Send", variant="primary", scale=3)
            new_chat_btn = gr.Button("New Conversation", scale=1)

        conversation_info = gr.Textbox(
            label="Conversation ID",
            interactive=False,
        )

        gr.Markdown("---")
        gr.Markdown("### HITL Resume Panel")
        gr.Markdown("Only needed when HITL mode is enabled and the agent is paused.")

        with gr.Row():
            thread_id_display = gr.Textbox(
                label="Thread ID",
                interactive=False,
                scale=3,
            )
            intent_display = gr.Textbox(
                label="Detected Intent",
                interactive=False,
                scale=1,
            )

        override_intent = gr.Dropdown(
            label="Override Intent (optional)",
            choices=["", "research", "summarise", "fact_check"],
            value="",
        )

        with gr.Row():
            approve_btn = gr.Button("Approve and Continue", variant="primary")
            reject_btn = gr.Button("Reject", variant="stop")

        hitl_status = gr.Textbox(label="HITL Status", interactive=False)

        def on_send(message, history, conv_id, hitl_enabled):
            new_history, new_conv_id, thread_id, intent = send_message(
                message, history, conv_id, hitl_enabled
            )
            conv_display = str(new_conv_id) if new_conv_id else ""
            return (
                new_history,
                new_conv_id,
                thread_id,
                intent,
                "",
                conv_display,
                thread_id,
                intent,
            )

        def on_new_chat():
            return [], None, "", "", "", ""

        def on_approve(thread_id, conv_id, override, history):
            new_history, status = resume_hitl(
                thread_id, conv_id, True, override, history
            )
            return new_history, status, "", ""

        def on_reject(thread_id, conv_id, history):
            new_history, status = resume_hitl(
                thread_id, conv_id, False, "", history
            )
            return new_history, status

        send_btn.click(
            fn=on_send,
            inputs=[message_input, chatbot, conversation_id_state, use_hitl],
            outputs=[
                chatbot,
                conversation_id_state,
                thread_id_state,
                intent_state,
                message_input,
                conversation_info,
                thread_id_display,
                intent_display,
            ],
        )

        new_chat_btn.click(
            fn=on_new_chat,
            outputs=[
                chatbot,
                conversation_id_state,
                thread_id_state,
                intent_state,
                conversation_info,
                hitl_status,
            ],
        )

        approve_btn.click(
            fn=on_approve,
            inputs=[thread_id_state, conversation_id_state, override_intent, chatbot],
            outputs=[chatbot, hitl_status, thread_id_display, intent_display],
        )

        reject_btn.click(
            fn=on_reject,
            inputs=[thread_id_state, conversation_id_state, chatbot],
            outputs=[chatbot, hitl_status],
        )