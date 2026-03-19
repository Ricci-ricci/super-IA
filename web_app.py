from __future__ import annotations

import io
from contextlib import redirect_stdout
from typing import Optional

import gradio as gr

from knowledge_base import SERVICES_ACTIONS
from parser import parse_nmap

# LLM optional import (same spirit as main.py)
try:
    from llm import OllamaClient

    HAS_LLM = True
except Exception:
    HAS_LLM = False

    class OllamaClient:  # fallback stub
        def __init__(self, base_url="http://localhost:11434", model="llama3.2:1b"):
            self.base_url = base_url
            self.model = model
            self.timeout = 20

        def is_available(self):
            return False

        def chat(self, model, message, system_prompt="", temperature=0.0):
            return None


def get_llm_scan_analysis(parsed_services: list, llm_client) -> Optional[str]:
    if not llm_client.is_available():
        return None

    services_text = [service for _, service, _ in parsed_services]
    prompt = f"Security analysis for: {', '.join(services_text)}. Priority?"

    try:
        llm_client.timeout = 20
        return llm_client.chat(
            model=llm_client.model,
            message=prompt,
            system_prompt="",
            temperature=0.0,
        )
    except Exception:
        return None


def analyze_scan(nmap_text: str, use_ai: bool):
    nmap_text = (nmap_text or "").strip()
    if not nmap_text:
        return "Please paste Nmap output first.", []

    parsed = parse_nmap(nmap_text)
    if not parsed:
        return (
            "No open services found. Make sure your input contains Nmap normal output with "
            "`PORT  STATE  SERVICE  VERSION`.",
            [],
        )

    llm_client = OllamaClient()
    ai_block = ""

    if use_ai and HAS_LLM and len(parsed) <= 2:
        ai = get_llm_scan_analysis(parsed, llm_client)
        if ai:
            ai_block = f"## AI Analysis\n{ai}\n\n"
        else:
            ai_block = "## AI Analysis\nAI unavailable or timeout; showing rule-based analysis.\n\n"

    lines = [ai_block + "## Service Recommendations"]
    table_rows = []

    for port, service, version in parsed:
        actions = SERVICES_ACTIONS.get(
            service,
            "No specific actions found. Use general pentesting methodology.",
        )
        lines.append(f"- **{port} / {service}** ({version})\n  - {actions}")
        table_rows.append([port, service, version, actions])

    markdown = "\n".join(lines)
    return markdown, table_rows


def analyze_uploaded_file(file_obj, use_ai: bool):
    if file_obj is None:
        return "Please upload a file.", []

    # Gradio file gives a path-like object depending on version
    try:
        with open(file_obj.name, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return "Could not read uploaded file.", []

    return analyze_scan(content, use_ai)


with gr.Blocks(title="superAI - Local Web demo") as demo:
    gr.Markdown("# superAI (Local)")
    gr.Markdown(
        "Authorized use only. This UI runs locally and helps analyze pasted Nmap results."
    )

    with gr.Tab("Paste Scan"):
        nmap_input = gr.Textbox(
            label="Nmap Output",
            lines=18,
            placeholder="Paste Nmap normal output here...",
        )
        use_ai_checkbox = gr.Checkbox(
            label="Use local AI analysis (Ollama)", value=True
        )
        analyze_btn = gr.Button("Analyze")
        md_output = gr.Markdown()
        table_output = gr.Dataframe(
            headers=["Port", "Service", "Version", "Recommended Actions"],
            datatype=["str", "str", "str", "str"],
            interactive=False,
            wrap=True,
        )
        analyze_btn.click(
            fn=analyze_scan,
            inputs=[nmap_input, use_ai_checkbox],
            outputs=[md_output, table_output],
        )

    with gr.Tab("Upload File"):
        file_input = gr.File(label="Upload Nmap output file (.txt, .nmap)")
        use_ai_checkbox2 = gr.Checkbox(
            label="Use local AI analysis (Ollama)", value=True
        )
        analyze_file_btn = gr.Button("Analyze File")
        md_output2 = gr.Markdown()
        table_output2 = gr.Dataframe(
            headers=["Port", "Service", "Version", "Recommended Actions"],
            datatype=["str", "str", "str", "str"],
            interactive=False,
            wrap=True,
        )
        analyze_file_btn.click(
            fn=analyze_uploaded_file,
            inputs=[file_input, use_ai_checkbox2],
            outputs=[md_output2, table_output2],
        )

if __name__ == "__main__":
    # local only for safety
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
