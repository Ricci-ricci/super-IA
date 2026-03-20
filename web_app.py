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
    prompt = f"Security analysis for: {', '.join(services_text)}. Priority targets and attack vectors?"

    try:
        llm_client.timeout = 20
        return llm_client.chat(
            model=llm_client.model,
            message=prompt,
            system_prompt="You are a cybersecurity expert. Provide concise, actionable penetration testing recommendations.",
            temperature=0.0,
        )
    except Exception:
        return None


def analyze_scan(nmap_text: str, use_ai: bool):
    nmap_text = (nmap_text or "").strip()
    if not nmap_text:
        return (
            "⚠️ **No input detected**\n\nPlease paste your Nmap scan results above.",
            [],
            "🔴 Ready",
        )

    parsed = parse_nmap(nmap_text)
    if not parsed:
        return (
            "❌ **Parse Failed**\n\nNo open services detected. Ensure your input contains standard Nmap output with:\n```\nPORT     STATE SERVICE  VERSION\n```",
            [],
            "🔴 Parse Error",
        )

    llm_client = OllamaClient()
    ai_block = ""
    status = "🟢 Analysis Complete"

    if use_ai and HAS_LLM and len(parsed) <= 3:
        status = "🟡 AI Processing..."
        ai = get_llm_scan_analysis(parsed, llm_client)
        if ai:
            ai_block = f"## 🤖 AI Security Analysis\n\n{ai}\n\n---\n\n"
            status = "🟢 AI Analysis Complete"
        else:
            ai_block = "## ⚠️ AI Analysis\n\n*Local AI unavailable or timeout. Showing rule-based analysis below.*\n\n---\n\n"
            status = "🟡 AI Timeout - Fallback Analysis"

    # Enhanced markdown with better formatting
    lines = [ai_block + "## 🎯 Target Assessment"]
    table_rows = []

    for i, (port, service, version) in enumerate(parsed, 1):
        actions = SERVICES_ACTIONS.get(
            service,
            "⚡ General enumeration recommended - check for default credentials, version-specific exploits, and misconfigurations.",
        )

        # Risk level based on common services
        risk_emoji = (
            "🔥"
            if service in ["ssh", "ftp", "telnet", "rdp"]
            else "⚡"
            if service in ["http", "https", "smb"]
            else "📡"
        )

        lines.append(f"### {risk_emoji} Target {i}: {port}/{service}")
        lines.append(f"**Version:** `{version}`")
        lines.append(f"**Attack Vectors:** {actions}")
        lines.append("---")

        table_rows.append(
            [
                f"🔹 {port}",
                service,
                version,
                actions[:100] + "..." if len(actions) > 100 else actions,
            ]
        )

    markdown = "\n".join(lines)
    return markdown, table_rows, status


def analyze_uploaded_file(file_obj, use_ai: bool):
    if file_obj is None:
        return (
            "📁 **No file selected**\n\nPlease upload a file containing Nmap scan results.",
            [],
            "🔴 No File",
        )

    try:
        with open(file_obj.name, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return analyze_scan(content, use_ai)
    except Exception as e:
        return f"❌ **File Read Error**\n\n```\n{str(e)}\n```", [], "🔴 File Error"


def get_ai_status():
    """Get current AI system status"""
    if not HAS_LLM:
        return "🔴 AI Module: Not Available"

    llm_client = OllamaClient()
    if llm_client.is_available():
        return f"🟢 AI Ready: {llm_client.model}"
    else:
        return "🟡 AI: Ollama Disconnected"


# Custom CSS for cyber dark theme
custom_css = """
/* Global dark cyber theme */
.gradio-container {
    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%) !important;
    color: #00ff9f !important;
    font-family: 'Fira Code', 'Consolas', monospace !important;
}

/* Header styling */
.markdown h1 {
    color: #00ff9f !important;
    text-shadow: 0 0 10px #00ff9f !important;
    font-weight: 700 !important;
    text-align: center !important;
    margin-bottom: 0.5rem !important;
}

.markdown h2 {
    color: #00d4ff !important;
    border-bottom: 2px solid #00d4ff !important;
    padding-bottom: 5px !important;
    margin-top: 1.5rem !important;
}

.markdown h3 {
    color: #ff6b35 !important;
    margin-top: 1rem !important;
}

/* Tab styling */
.tab-nav {
    background-color: #1e1e2e !important;
    border-radius: 10px 10px 0 0 !important;
}

.tab-nav button {
    background: linear-gradient(135deg, #2d2d44 0%, #3d3d5c 100%) !important;
    color: #00ff9f !important;
    border: 1px solid #00ff9f !important;
    margin: 5px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.tab-nav button[aria-selected="true"] {
    background: linear-gradient(135deg, #00ff9f 0%, #00d4ff 100%) !important;
    color: #000 !important;
    box-shadow: 0 0 20px #00ff9f !important;
}

/* Input styling */
.gr-textbox, .gr-file {
    background-color: #1a1a2e !important;
    border: 2px solid #00d4ff !important;
    border-radius: 8px !important;
    color: #00ff9f !important;
}

.gr-textbox:focus, .gr-file:focus {
    border-color: #00ff9f !important;
    box-shadow: 0 0 15px rgba(0, 255, 159, 0.3) !important;
}

/* Button styling */
.gr-button {
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #000 !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
    box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4) !important;
    transition: all 0.3s ease !important;
}

.gr-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(255, 107, 53, 0.6) !important;
}

/* Checkbox styling */
.gr-checkbox {
    accent-color: #00ff9f !important;
}

/* Status indicator */
.status-indicator {
    background: linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%) !important;
    border: 1px solid #00d4ff !important;
    border-radius: 8px !important;
    padding: 10px !important;
    text-align: center !important;
    font-weight: 600 !important;
    margin: 10px 0 !important;
}

/* Data table styling */
.gr-dataframe {
    background-color: #1a1a2e !important;
    border: 2px solid #00d4ff !important;
    border-radius: 8px !important;
}

.gr-dataframe th {
    background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important;
    color: #000 !important;
    font-weight: 700 !important;
}

.gr-dataframe td {
    color: #00ff9f !important;
    border-color: #2d2d44 !important;
}

/* Markdown content styling */
.markdown {
    background-color: #1a1a2e !important;
    border: 1px solid #00d4ff !important;
    border-radius: 8px !important;
    padding: 15px !important;
    margin: 10px 0 !important;
}

.markdown code {
    background-color: #0a0a0a !important;
    color: #ff6b35 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    border: 1px solid #ff6b35 !important;
}

.markdown pre {
    background-color: #0a0a0a !important;
    border: 1px solid #00d4ff !important;
    border-radius: 6px !important;
    padding: 10px !important;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 12px !important;
}

::-webkit-scrollbar-track {
    background: #1a1a2e !important;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #00ff9f 0%, #00d4ff 100%) !important;
    border-radius: 6px !important;
}

/* Animation for loading */
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.loading {
    animation: pulse 1.5s infinite !important;
}
"""

# Create the modern dashboard
with gr.Blocks(
    title="🔒 superPENTESTING | Local Cyber Dashboard",
) as demo:
    gr.HTML("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1>🔒 superPENTESTING</h1>
        <p style="color: #00d4ff; font-size: 18px; margin: 0;">
            <strong>Local Cybersecurity Analysis Dashboard</strong>
        </p>
        <p style="color: #ff6b35; font-size: 14px; margin: 5px 0 0 0;">
            ⚠️ AUTHORIZED USE ONLY - Local Processing - No Data Leaves This Machine
        </p>
    </div>
    """)

    # System status indicator
    status_display = gr.Markdown(
        value=f"### 🖥️ System Status\n{get_ai_status()}\n🌐 **Interface:** Local (127.0.0.1:7860)\n🔐 **Security:** Offline Processing",
        elem_classes=["status-indicator"],
    )

    with gr.Tab("📊 Paste Analysis", elem_id="paste-tab"):
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### 📝 Input: Nmap Scan Results")
                nmap_input = gr.Textbox(
                    label="🔍 Nmap Output",
                    lines=16,
                    placeholder="""Paste your Nmap scan results here...\n\nExample:\nPORT     STATE SERVICE  VERSION\n22/tcp   open  ssh      OpenSSH 8.0\n80/tcp   open  http     nginx 1.18.0\n443/tcp  open  https    nginx 1.18.0""",
                )

                with gr.Row():
                    use_ai_checkbox = gr.Checkbox(
                        label="🤖 Enable AI Analysis",
                        value=True,
                    )
                    analyze_btn = gr.Button(
                        "🎯 Analyze Targets", variant="primary", size="lg"
                    )

                scan_status = gr.Markdown(
                    value="🔴 Ready for Input", elem_classes=["status-indicator"]
                )

            with gr.Column(scale=3):
                gr.Markdown("### 📊 Analysis Results")
                md_output = gr.Markdown(
                    value="🕐 **Waiting for scan data...**\n\nPaste Nmap results and click 'Analyze Targets' to begin assessment.",
                    elem_classes=["markdown"],
                )

        gr.Markdown("### 📋 Detailed Service Breakdown")
        table_output = gr.Dataframe(
            headers=["🔹 Port", "🔧 Service", "📦 Version", "⚡ Attack Vectors"],
            datatype=["str", "str", "str", "str"],
            interactive=False,
            wrap=True,
            row_count=(5, "dynamic"),
        )

        analyze_btn.click(
            fn=analyze_scan,
            inputs=[nmap_input, use_ai_checkbox],
            outputs=[md_output, table_output, scan_status],
        )

    with gr.Tab("📁 File Upload", elem_id="upload-tab"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📤 Upload Scan File")
                file_input = gr.File(
                    label="📄 Upload Nmap Results",
                    file_types=[".txt", ".nmap", ".xml"],
                )

                with gr.Row():
                    use_ai_checkbox2 = gr.Checkbox(
                        label="🤖 Enable AI Analysis", value=True
                    )
                    analyze_file_btn = gr.Button(
                        "🔍 Process File", variant="primary", size="lg"
                    )

                file_status = gr.Markdown(
                    value="🔴 No File Selected", elem_classes=["status-indicator"]
                )

            with gr.Column(scale=2):
                gr.Markdown("### 📊 File Analysis Results")
                md_output2 = gr.Markdown(
                    value="📁 **No file uploaded**\n\nSelect a file containing Nmap scan results and click 'Process File'.",
                    elem_classes=["markdown"],
                )

        gr.Markdown("### 📋 Service Analysis Table")
        table_output2 = gr.Dataframe(
            headers=["🔹 Port", "🔧 Service", "📦 Version", "⚡ Attack Vectors"],
            datatype=["str", "str", "str", "str"],
            interactive=False,
            wrap=True,
            row_count=(5, "dynamic"),
        )

        analyze_file_btn.click(
            fn=analyze_uploaded_file,
            inputs=[file_input, use_ai_checkbox2],
            outputs=[md_output2, table_output2, file_status],
        )

    with gr.Tab("ℹ️ About", elem_id="about-tab"):
        gr.Markdown("""
        ### 🔐 superPENTESTING Dashboard

        **Version:** 2.0 (Modern Cyber Theme)
        **Purpose:** Local penetration testing analysis tool

        #### 🎯 Features
        - **🔍 Nmap Parser:** Intelligent parsing of scan results
        - **🤖 AI Analysis:** Local LLM-powered threat assessment via Ollama
        - **📊 Visual Dashboard:** Modern cyber-themed interface
        - **🔒 Privacy-First:** All processing happens locally
        - **📁 File Support:** Upload and analyze scan files

        #### ⚠️ Important Notes
        - **Authorized Use Only:** Only test systems you own or have explicit permission to test
        - **Local Processing:** No data leaves your machine
        - **AI Optional:** Works with or without Ollama
        - **Educational Purpose:** Designed for learning and authorized security testing

        #### 🛠️ Technical Stack
        - **Backend:** Python + Gradio
        - **AI Engine:** Ollama (optional)
        - **Model:** llama3.2:1b (default)
        - **Interface:** Modern dark cyber theme

        #### 📞 Support
        For questions or issues, refer to the project documentation.

        ---
        *Remember: With great power comes great responsibility. Use ethically.*
        """)

if __name__ == "__main__":
    print("🚀 Starting superPENTESTING Dashboard...")
    print(f"🤖 AI Status: {get_ai_status()}")
    print("🌐 Access: http://127.0.0.1:7860")
    print("🔒 Security: Local-only processing")

    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        quiet=False,
        inbrowser=True,  # Auto-open in browser
        css=custom_css,
        theme=gr.themes.Base(
            primary_hue="cyan",
            secondary_hue="green",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Fira Code"),
        ),
    )
