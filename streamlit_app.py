import os
from typing import Any, Dict, List

import pandas as pd
import requests
import streamlit as st

DEFAULT_API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


def init_state() -> None:
    if "api_base_url" not in st.session_state:
        st.session_state.api_base_url = DEFAULT_API_BASE_URL
    if "analysis_data" not in st.session_state:
        st.session_state.analysis_data = None
    if "full_text" not in st.session_state:
        st.session_state.full_text = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []


def get_ingest_endpoint(file_name: str, base_url: str) -> str:
    lower_name = file_name.lower()
    if lower_name.endswith(".pdf"):
        return f"{base_url}/ingest/pdf"
    if lower_name.endswith(".csv"):
        return f"{base_url}/ingest/csv"
    raise ValueError("Unsupported file type. Please upload a PDF or CSV file.")


def ingest_file(uploaded_file, base_url: str) -> Dict[str, Any]:
    endpoint = get_ingest_endpoint(uploaded_file.name, base_url)
    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "application/octet-stream")
    }
    response = requests.post(endpoint, files=files, timeout=120)
    response.raise_for_status()
    return response.json()


def analyze_text(text: str, base_url: str) -> Dict[str, Any]:
    response = requests.post(f"{base_url}/analyze", json={"text": text}, timeout=180)
    response.raise_for_status()
    return response.json()


def ask_question(question: str, base_url: str) -> str:
    response = requests.post(f"{base_url}/qa", json={"question": question}, timeout=120)
    response.raise_for_status()
    data = response.json()
    return data.get("answer", "No answer received.")


def render_analytics(analytics: Any) -> None:
    st.subheader("Financial Insights")

    if isinstance(analytics, str):
        st.markdown(analytics)
        return

    if not isinstance(analytics, dict):
        st.info("No analytics data available.")
        return

    charts = analytics.get("charts", [])
    if isinstance(charts, list) and charts:
        for idx, chart in enumerate(charts, start=1):
            title = chart.get("title", f"Chart {idx}")
            chart_type = chart.get("type", "bar")
            data = chart.get("data", [])
            insights = chart.get("insights")

            st.markdown(f"### {title}")
            if not isinstance(data, list) or not data:
                st.warning("Chart has no data.")
                continue

            df = pd.DataFrame(data)
            if "name" in df.columns and "value" in df.columns:
                df = df[["name", "value"]]
                df["value"] = pd.to_numeric(df["value"], errors="coerce")
                df = df.dropna(subset=["value"])

                if df.empty:
                    st.warning("Chart data is invalid after parsing.")
                    continue

                chart_df = df.set_index("name")
                
                if chart_type == "line":
                    st.line_chart(chart_df, use_container_width=True)
                elif chart_type == "area":
                    st.area_chart(chart_df, use_container_width=True)
                elif chart_type == "pie":
                    # Streamlit pie-chart via Vega-Lite spec.
                    st.vega_lite_chart(
                        df,
                        {
                            "mark": {"type": "arc", "innerRadius": 20},
                            "encoding": {
                                "theta": {"field": "value", "type": "quantitative"},
                                "color": {"field": "name", "type": "nominal"},
                                "tooltip": [
                                    {"field": "name", "type": "nominal"},
                                    {"field": "value", "type": "quantitative"},
                                ],
                            },
                        },
                        use_container_width=True,
                    )
                else:
                    # Default: bar chart
                    st.bar_chart(chart_df, use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)

            if insights:
                st.caption(f"📊 {insights}")
    else:
        st.info("No chart data available.")

    text_analysis = analytics.get("text_analysis") or analytics.get("insights")
    if text_analysis:
        st.markdown(text_analysis)


def render_results(analysis_data: Dict[str, Any]) -> None:
    tab_summary, tab_mcq, tab_analytics = st.tabs(["Summary", "Q&A / MCQs", "Analytics"])

    with tab_summary:
        st.subheader("Document Summary")
        st.markdown(analysis_data.get("summary") or "No summary available.")

    with tab_mcq:
        st.subheader("Generated Questions")
        mcqs: List[Dict[str, Any]] = analysis_data.get("mcqs") or []
        if isinstance(mcqs, list) and mcqs:
            for idx, question in enumerate(mcqs, start=1):
                q = question.get("question", "No question text provided.")
                options = question.get("options", [])
                correct_answer = question.get("correct_answer", "")

                st.markdown(f"**{idx}. {q}**")
                if isinstance(options, list) and options:
                    for option in options:
                        st.write(f"- {option}")
                else:
                    raw_output = question.get("raw")
                    if raw_output:
                        st.code(raw_output)
                    else:
                        st.caption("No options available.")

                if correct_answer:
                    st.success(f"Answer: {correct_answer}")
                st.divider()
        else:
            st.info("No questions generated or response format issue.")
            st.json(mcqs)

    with tab_analytics:
        render_analytics(analysis_data.get("analytics"))


def render_chat(base_url: str) -> None:
    st.subheader("Financial Advisor Chat")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask a question about your uploaded documents...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = ask_question(question, base_url)
                except requests.RequestException as exc:
                    answer = f"Could not fetch answer: {exc}"
                st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})


def render_chat(base_url: str) -> None:
    st.subheader("Financial Advisor Chat")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask a question about your uploaded documents...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = ask_question(question, base_url)
                except requests.RequestException as exc:
                    answer = f"Could not fetch answer: {exc}"
                st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})


def main() -> None:
    st.set_page_config(page_title="Financial Insights AI", layout="wide")
    init_state()

    st.title("Financial Insights AI")
    st.caption("Upload financial PDF/CSV files, generate summary/MCQs/analytics, and ask questions.")

    with st.sidebar:
        st.header("Backend Settings")
        st.session_state.api_base_url = st.text_input(
            "FastAPI Base URL",
            value=st.session_state.api_base_url,
            help="Example: http://localhost:8000/api/v1",
        )
        if st.button("Clear Session"):
            st.session_state.analysis_data = None
            st.session_state.full_text = ""
            st.session_state.messages = []
            st.rerun()

    st.subheader("Upload Financial Document")
    uploaded_file = st.file_uploader("Choose a PDF or CSV", type=["pdf", "csv"])

    if uploaded_file is not None and st.button("Upload and Analyze", type="primary"):
        with st.spinner("Uploading and processing document..."):
            try:
                ingest_data = ingest_file(uploaded_file, st.session_state.api_base_url)
                st.session_state.full_text = ingest_data.get("full_content", "")
                if not st.session_state.full_text:
                    st.warning("No text extracted from file.")
                else:
                    # Reset chat so questions stay scoped to the newly uploaded document.
                    st.session_state.messages = []
                    st.info("Document uploaded. Running multi-agent analysis...")
                    st.session_state.analysis_data = analyze_text(
                        st.session_state.full_text,
                        st.session_state.api_base_url,
                    )
                    st.success("Analysis complete.")
            except ValueError as exc:
                st.error(str(exc))
            except requests.RequestException as exc:
                st.error(f"Backend request failed: {exc}")
                response = getattr(exc, "response", None)
                if response is not None:
                    with st.expander("Backend error details"):
                        st.code(response.text)

    st.divider()
    render_chat(st.session_state.api_base_url)

    st.divider()
    if st.session_state.analysis_data:
        render_results(st.session_state.analysis_data)
    else:
        st.info("Upload a file to see analysis results here.")


if __name__ == "__main__":
    main()
