from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import aggregate_entity_stats
from src.drilldown import get_entity_contexts
from src.input_loader import (
    load_csv_file,
    load_docx_file,
    load_manual_text,
    load_pdf_file,
    load_txt_file,
)
from src.keywords import extract_corpus_keywords, extract_document_keywords
from src.ner import get_entity_label_descriptions, load_spacy_model, run_spacy_ner
from src.preprocessing import prepare_documents
from src.report import generate_report
from src.search import build_tfidf_index, search_documents
from src.utils import (
    dataframe_to_csv_bytes,
    dict_to_json_bytes,
    display_unknown,
    markdown_to_bytes,
    metric_value,
    shorten_filename,
    shorten_identifier,
)
from src.visualization import (
    apply_plotly_theme,
    plot_cross_category,
    plot_keywords,
    plot_label_distribution,
    plot_top_entities,
    show_co_occurrence_table,
)


st.set_page_config(
    page_title="AnyText AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


APP_DIR = Path(__file__).parent
SAMPLE_DATA_PATH = APP_DIR / "data" / "sample_text_corpus.csv"
UI_THEME = "Light"
STATE_KEYS = [
    "document_df",
    "entity_df",
    "stats",
    "vectorizer",
    "tfidf_matrix",
    "keyword_df",
    "document_keyword_df",
]


def init_session_state() -> None:
    """Initialize all Streamlit session-state slots used by the app."""
    for key in STATE_KEYS:
        if key not in st.session_state:
            st.session_state[key] = None

    if "stats_top_n" not in st.session_state:
        st.session_state["stats_top_n"] = None
    if "keyword_top_n" not in st.session_state:
        st.session_state["keyword_top_n"] = None


def inject_css() -> None:
    """Inject a small light-mode stylesheet for a clean SaaS dashboard shell."""
    st.markdown(
        """
<style>
:root {
    --app-bg: #F7F8FB;
    --card-bg: #FFFFFF;
    --card-subtle: #F8FAFC;
    --text-main: #111827;
    --text-muted: #64748B;
    --border: #E5E7EB;
    --border-strong: #CBD5E1;
    --primary: #4F46E5;
    --primary-hover: #4338CA;
    --primary-soft: #EEF2FF;
    --accent: #0891B2;
    --shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
}

#MainMenu,
footer,
header {
    visibility: hidden;
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stToolbar"] {
    background: var(--app-bg);
    color: var(--text-main);
}

.main .block-container {
    max-width: 1360px;
    padding: 1.25rem 2rem 3rem;
}

h1,
h2,
h3,
h4,
h5,
h6,
[data-testid="stMarkdownContainer"],
[data-testid="stText"] {
    color: var(--text-main);
}

h1 {
    font-size: clamp(1.8rem, 2.4vw, 2.45rem) !important;
    line-height: 1.12 !important;
    font-weight: 760 !important;
    margin-bottom: 0.2rem !important;
}

h2 {
    font-size: 1.25rem !important;
    line-height: 1.3 !important;
    margin-bottom: 0.25rem !important;
}

h3 {
    font-size: 1.03rem !important;
    line-height: 1.35 !important;
}

[data-testid="stCaptionContainer"] {
    color: var(--text-muted) !important;
    overflow-wrap: anywhere;
}

hr {
    border-color: var(--border) !important;
    margin: 1.1rem 0;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    box-shadow: var(--shadow);
    padding: 0.15rem;
}

[data-testid="stDataFrame"],
[data-testid="stTable"],
[data-testid="stPlotlyChart"] {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

[data-testid="stPlotlyChart"] {
    padding: 0.45rem;
}

.stButton > button,
.stDownloadButton > button {
    min-height: 2.55rem;
    border-radius: 10px !important;
    border: 1px solid var(--border-strong) !important;
    background: var(--card-bg) !important;
    color: var(--text-main) !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: var(--primary) !important;
    background: var(--primary-soft) !important;
    color: var(--primary) !important;
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: var(--primary) !important;
    border-color: var(--primary) !important;
    color: #FFFFFF !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    background: var(--primary-hover) !important;
    border-color: var(--primary-hover) !important;
    color: #FFFFFF !important;
}

.stButton > button:disabled,
.stDownloadButton > button:disabled {
    background: #E2E8F0 !important;
    border-color: var(--border) !important;
    color: #64748B !important;
    box-shadow: none !important;
}

.stTextInput input,
.stTextArea textarea,
[data-baseweb="select"] > div,
[data-baseweb="input"] input {
    background: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-main) !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
[data-baseweb="select"] > div:focus-within,
[data-baseweb="input"] input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px var(--primary-soft) !important;
}

[data-baseweb="popover"] [role="listbox"],
[data-baseweb="menu"] {
    background: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

[data-baseweb="menu"] li,
[role="option"] {
    color: var(--text-main) !important;
}

.stMultiSelect [data-baseweb="tag"] {
    background: var(--primary) !important;
    color: #FFFFFF !important;
    border-radius: 999px !important;
}

[data-testid="stFileUploaderDropzone"] {
    background: var(--card-subtle) !important;
    border: 1px dashed var(--border-strong) !important;
    border-radius: 12px !important;
    min-height: 8rem;
}

[data-testid="stAlert"] {
    border-radius: 12px;
}

[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] p {
    color: var(--text-main) !important;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: var(--text-muted) !important;
}

[role="radiogroup"] {
    gap: 0.4rem;
}

[role="radiogroup"] label {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 0.35rem 0.75rem;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
}

@media (max-width: 900px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )


def document_count() -> int:
    document_df = st.session_state.get("document_df")
    return 0 if document_df is None or document_df.empty else int(len(document_df))


def get_ui_state() -> dict[str, object]:
    """Summarize the current app state for the header and sidebar."""
    document_df = st.session_state.get("document_df")
    entity_df = st.session_state.get("entity_df")
    keyword_df = st.session_state.get("keyword_df")
    vectorizer = st.session_state.get("vectorizer")
    tfidf_matrix = st.session_state.get("tfidf_matrix")

    docs = 0 if document_df is None or document_df.empty else int(len(document_df))
    entities = 0 if entity_df is None or entity_df.empty else int(len(entity_df))
    keywords = 0 if keyword_df is None or keyword_df.empty else int(len(keyword_df))
    search_ready = docs > 0 and vectorizer is not None and tfidf_matrix is not None

    if docs == 0:
        analysis_state = "No corpus"
        next_step = "Paste text, upload files, or load the sample corpus."
    elif entity_df is None:
        analysis_state = "Ready to analyze"
        next_step = "Run NLP Analysis to extract entities, keywords, search vectors, and reports."
    else:
        analysis_state = "Analysis complete"
        next_step = "Explore the top navigation to answer what this document collection can tell you."

    return {
        "document_count": docs,
        "entity_count": entities,
        "keyword_count": keywords,
        "search_status": "Ready" if search_ready else "Pending",
        "analysis_state": analysis_state,
        "next_step": next_step,
    }


def is_empty(df: pd.DataFrame | None) -> bool:
    return df is None or df.empty


def render_section_header(title: str, description: str | None = None, overline: str | None = None) -> None:
    if overline:
        st.caption(overline.upper())
    st.subheader(title)
    if description:
        st.caption(description)


def render_empty_state(icon: str, title: str, message: str) -> None:
    st.info(f"{icon} **{title}**\n\n{message}")


def render_stat_card(label: str, value, note: str | None = None) -> None:
    with st.container(border=True):
        st.caption(label)
        st.subheader(metric_value(value))
        if note:
            st.caption(note)


def render_dataframe_section(title: str, description: str, df: pd.DataFrame, *, hide_index: bool = True) -> None:
    with st.container(border=True):
        render_section_header(title, description)
        st.dataframe(df, use_container_width=True, hide_index=hide_index)


def display_category(value) -> str:
    text = display_unknown(value)
    if text == "Unknown":
        return text
    return text.replace("_", " ").title()


def document_option_label(document: pd.Series) -> str:
    source = shorten_filename(display_unknown(document.get("source_name", "")), max_chars=32)
    category = display_category(document.get("category", ""))
    doc_id = shorten_identifier(document.get("id", ""), prefix_chars=3, max_chars=12)
    return f"{source} · {category} · {doc_id}"


def dataframe_records(df: pd.DataFrame | None) -> list[dict]:
    if is_empty(df):
        return []
    return df.to_dict(orient="records")


def build_analysis_summary(
    document_df: pd.DataFrame | None,
    entity_df: pd.DataFrame | None,
    stats: dict,
    keyword_df: pd.DataFrame | None,
) -> dict:
    document_df = document_df if document_df is not None else pd.DataFrame()
    entity_df = entity_df if entity_df is not None else pd.DataFrame()
    stats = stats or {}

    return {
        "corpus": {
            "document_count": int(len(document_df)),
            "total_characters": int(document_df.get("text_length", pd.Series(dtype=int)).sum()),
            "languages": document_df.get("language", pd.Series(dtype=str)).value_counts().to_dict(),
            "categories": document_df.get("category", pd.Series(dtype=str)).value_counts().to_dict(),
        },
        "entities": {
            "total_mentions": int(stats.get("total_entities", 0)),
            "unique_entities": int(stats.get("unique_entities", 0)),
            "documents_with_entities": int(stats.get("documents_with_entities", 0)),
            "label_counts": dataframe_records(stats.get("label_counts")),
            "top_entities": dataframe_records(stats.get("top_entities")),
            "co_occurrence": dataframe_records(stats.get("co_occurrence")),
            "cross_category": dataframe_records(stats.get("cross_category")),
        },
        "keywords": dataframe_records(keyword_df),
        "report_metadata": {
            "format": "markdown",
            "generated_in_memory": True,
            "ner_model": "en_core_web_sm",
            "search_method": "TF-IDF cosine similarity",
        },
    }


def build_full_analysis_export(
    document_df: pd.DataFrame | None,
    entity_df: pd.DataFrame | None,
    stats: dict,
    keyword_df: pd.DataFrame | None,
    document_keyword_df: pd.DataFrame | None,
) -> dict:
    summary = build_analysis_summary(document_df, entity_df, stats, keyword_df)
    summary["documents"] = dataframe_records(document_df)
    summary["entity_mentions"] = dataframe_records(entity_df)
    summary["document_keywords"] = dataframe_records(document_keyword_df)
    return summary


def clear_session() -> None:
    for key in STATE_KEYS:
        st.session_state[key] = None
    st.session_state["stats_top_n"] = None
    st.session_state["keyword_top_n"] = None


def add_documents(frame: pd.DataFrame) -> None:
    if is_empty(frame):
        return

    current = st.session_state["document_df"]
    combined = frame if is_empty(current) else pd.concat([current, frame], ignore_index=True)
    st.session_state["document_df"] = prepare_documents(combined)
    st.session_state["entity_df"] = None
    st.session_state["stats"] = None
    st.session_state["stats_top_n"] = None
    st.session_state["keyword_df"] = None
    st.session_state["document_keyword_df"] = None
    st.session_state["keyword_top_n"] = None
    st.session_state["vectorizer"], st.session_state["tfidf_matrix"] = build_tfidf_index(
        st.session_state["document_df"]
    )


def process_uploaded_files(
    uploaded_files,
    fallback_category: str,
    split_pdf_pages: bool,
    csv_text_col: str | None,
    csv_id_col: str | None,
    csv_language_col: str | None,
    csv_category_col: str | None,
) -> tuple[pd.DataFrame, list[str]]:
    frames = []
    warnings = []

    for uploaded_file in uploaded_files or []:
        source_name = getattr(uploaded_file, "name", "uploaded_file")
        extension = Path(source_name).suffix.lower()

        try:
            if extension == ".txt":
                frame = load_txt_file(uploaded_file, category=fallback_category)
            elif extension == ".csv":
                frame = load_csv_file(
                    uploaded_file,
                    text_col=csv_text_col,
                    id_col=csv_id_col,
                    language_col=csv_language_col,
                    category_col=csv_category_col,
                    default_category=fallback_category,
                )
            elif extension == ".pdf":
                frame, warning = load_pdf_file(
                    uploaded_file,
                    category=fallback_category,
                    split_pages=split_pdf_pages,
                )
                if warning:
                    warnings.append(warning)
            elif extension == ".docx":
                frame = load_docx_file(uploaded_file, category=fallback_category)
            else:
                warnings.append(f"Unsupported file type for {source_name}.")
                continue

            if frame.empty:
                warnings.append(f"No usable text found in {source_name}.")
            else:
                frames.append(frame)
        except Exception as exc:
            warnings.append(f"Could not process {source_name}: {exc}")

    if not frames:
        return pd.DataFrame(), warnings

    return pd.concat(frames, ignore_index=True), warnings


def run_analysis(top_n: int) -> None:
    document_df = st.session_state["document_df"]
    if is_empty(document_df):
        st.warning("Add documents before running analysis.")
        return

    document_df = prepare_documents(document_df)
    st.session_state["document_df"] = document_df

    if "normalized_text" not in document_df.columns or not document_df["normalized_text"].str.strip().any():
        st.error("No non-empty text is available for NER.")
        return

    with st.spinner("Loading spaCy and extracting entities..."):
        nlp = load_spacy_model()
        entity_df = run_spacy_ner(document_df, nlp, text_column="normalized_text")

    keyword_df, document_keyword_df = get_keyword_data(top_n)
    st.session_state["entity_df"] = entity_df
    st.session_state["stats"] = aggregate_entity_stats(entity_df, top_n=top_n)
    st.session_state["stats"]["keywords"] = keyword_df
    st.session_state["stats_top_n"] = top_n
    st.session_state["keyword_df"] = keyword_df
    st.session_state["document_keyword_df"] = document_keyword_df
    st.session_state["vectorizer"], st.session_state["tfidf_matrix"] = build_tfidf_index(document_df)

    if entity_df.empty:
        st.warning("No named entities were detected. Check that the documents contain extractable English text.")
    else:
        st.success(f"Extracted {len(entity_df):,} entity mentions.")


def get_stats(top_n: int) -> dict:
    if st.session_state["stats"] is None or st.session_state["stats_top_n"] != top_n:
        st.session_state["stats"] = aggregate_entity_stats(st.session_state["entity_df"], top_n=top_n)
        st.session_state["stats_top_n"] = top_n
    keyword_df, _ = get_keyword_data(top_n)
    st.session_state["stats"]["keywords"] = keyword_df
    return st.session_state["stats"]


def get_keyword_data(corpus_top_n: int, document_top_n: int = 10) -> tuple[pd.DataFrame, pd.DataFrame]:
    document_df = st.session_state["document_df"]
    if is_empty(document_df):
        return pd.DataFrame(), pd.DataFrame()

    if st.session_state["keyword_df"] is None or st.session_state["keyword_top_n"] != corpus_top_n:
        st.session_state["keyword_df"] = extract_corpus_keywords(document_df, top_n=corpus_top_n)
        st.session_state["document_keyword_df"] = extract_document_keywords(
            document_df,
            top_n=document_top_n,
        )
        st.session_state["keyword_top_n"] = corpus_top_n

    return st.session_state["keyword_df"], st.session_state["document_keyword_df"]


def get_report(top_n: int) -> str:
    return generate_report(get_stats(top_n), st.session_state["document_df"])


def render_sidebar() -> tuple[int, int, bool]:
    with st.sidebar:
        st.markdown("### Settings")
        st.caption("Optional analysis controls.")
        top_n = st.slider("Top entities", 5, 50, 20)
        top_k = st.slider("Search results", 3, 10, 5)
        split_pages = st.checkbox("Split PDF by page")

    return top_n, top_k, split_pages


def render_header() -> None:
    header_col, meta_col = st.columns([1.7, 1], gap="large")
    with header_col:
        st.title("AnyText AI")
        st.caption("Document Intelligence Dashboard")
        st.write(
            "Turn a collection of text, PDFs, DOCX files, and CSV rows into searchable NLP intelligence."
        )

    with meta_col:
        with st.container(border=True):
            st.caption("Product focus")
            st.subheader("What can this collection tell me?")
            st.caption("Entities, keywords, relationships, search results, and reports.")


def render_status_strip() -> None:
    state = get_ui_state()
    metric_cols = st.columns(4, gap="medium")
    metrics = [
        ("Documents", state["document_count"]),
        ("Entities", state["entity_count"]),
        ("Keywords", state["keyword_count"]),
        ("Search", state["search_status"]),
    ]
    for col, (label, value) in zip(metric_cols, metrics, strict=False):
        with col:
            render_stat_card(label, value)


def render_top_navigation() -> str:
    sections = [
        "Input",
        "Overview",
        "Entities",
        "Keywords",
        "Explorer",
        "Relationships",
        "Search",
        "Report",
        "Downloads",
    ]
    return st.radio(
        "Section",
        sections,
        horizontal=True,
        label_visibility="collapsed",
        key="top_navigation",
    )


def render_input_section(top_n: int, split_pdf_pages: bool) -> None:
    render_section_header(
        "Build your document corpus",
        "Paste text, upload files, or load the sample corpus. Every input is standardized before analysis.",
        overline="Input",
    )

    paste_col, upload_col = st.columns(2, gap="large")

    with paste_col:
        with st.container(border=True):
            render_section_header("Paste text", "Add a quick article, memo, transcript, or report excerpt.")
            manual_text = st.text_area(
                "Text",
                height=260,
                placeholder="Paste an article, memo, transcript, or report excerpt...",
            )
            manual_category = st.text_input("Manual text category", value="manual")
            if st.button("Add pasted text", use_container_width=True):
                frame = load_manual_text(manual_text, category=manual_category)
                if frame.empty:
                    st.warning("Paste some text before adding it to the corpus.")
                else:
                    add_documents(frame)
                    st.success("Manual text added.")

    with upload_col:
        with st.container(border=True):
            render_section_header("Upload files", "Process one or more TXT, CSV, PDF, or DOCX files.")
            uploaded_files = st.file_uploader(
                "TXT, CSV, PDF, or DOCX",
                type=["txt", "csv", "pdf", "docx"],
                accept_multiple_files=True,
            )
            upload_category = st.text_input("Fallback category for uploaded files", value="unknown")
            st.caption(
                "PDFs will be split by page."
                if split_pdf_pages
                else "PDF page splitting is available in the optional settings panel."
            )

            with st.expander("CSV column mapping"):
                csv_text_col = st.text_input("Text column", value="", placeholder="Auto-detect if blank")
                csv_id_col = st.text_input("ID column", value="", placeholder="Optional")
                csv_language_col = st.text_input("Language column", value="", placeholder="Optional")
                csv_category_col = st.text_input("Category column", value="", placeholder="Optional")

            if st.button("Process uploaded files", use_container_width=True):
                frame, warnings = process_uploaded_files(
                    uploaded_files,
                    fallback_category=upload_category,
                    split_pdf_pages=split_pdf_pages,
                    csv_text_col=csv_text_col.strip() or None,
                    csv_id_col=csv_id_col.strip() or None,
                    csv_language_col=csv_language_col.strip() or None,
                    csv_category_col=csv_category_col.strip() or None,
                )
                for warning in warnings:
                    st.warning(warning)
                if frame.empty:
                    st.warning("No documents were added from the selected files.")
                else:
                    add_documents(frame)
                    st.success(f"Added {len(frame):,} document rows.")

    with st.container(border=True):
        render_section_header("Analyze the corpus", "Load sample data for screenshots or run the NLP pipeline on your prepared corpus.")
        action_cols = st.columns([1, 1.35, 1], gap="medium")
        with action_cols[0]:
            if st.button("Load sample corpus", use_container_width=True):
                sample_df = pd.read_csv(SAMPLE_DATA_PATH)
                add_documents(sample_df)
                st.success("Sample corpus loaded.")
        with action_cols[1]:
            if st.button("Run NLP Analysis", type="primary", use_container_width=True):
                run_analysis(top_n)
        with action_cols[2]:
            if st.button("Clear session", use_container_width=True):
                clear_session()
                st.success("Session cleared.")

    document_df = st.session_state["document_df"]
    if is_empty(document_df):
        render_empty_state("📄", "No documents yet", "Paste text, upload a file, or load the sample corpus to begin.")
    else:
        render_dataframe_section(
            "Current corpus",
            "Prepared document rows currently available for analysis.",
            document_df[["id", "source_name", "category", "language", "text_length", "text"]],
        )


def render_overview_section(top_n: int) -> None:
    document_df = st.session_state["document_df"]
    if is_empty(document_df):
        render_empty_state("📊", "No corpus yet", "Load documents to see corpus-level metrics and charts.")
        return

    render_section_header(
        "Corpus overview",
        "A high-level read on corpus size, language mix, categories, text length, and analysis readiness.",
        overline="Overview",
    )
    stats = get_stats(top_n)
    total_docs = len(document_df)
    total_chars = int(document_df["text_length"].sum())
    avg_length = round(float(document_df["text_length"].mean()))
    num_categories = document_df["category"].nunique()
    num_languages = document_df["language"].nunique()

    metric_cols = st.columns(6)
    metrics = [
        ("Documents", total_docs),
        ("Characters", total_chars),
        ("Avg Length", avg_length),
        ("Categories", num_categories),
        ("Languages", num_languages),
        ("Entities", stats["total_entities"]),
    ]
    for col, (label, value) in zip(metric_cols, metrics, strict=False):
        with col:
            render_stat_card(label, value)

    chart_col, language_col = st.columns(2, gap="large")
    with chart_col:
        with st.container(border=True):
            render_section_header("Documents by category", "How uploaded or labeled documents are distributed.")
            category_counts = document_df["category"].value_counts().reset_index()
            category_counts.columns = ["category", "documents"]
            category_counts["category"] = category_counts["category"].apply(display_category)
            figure = px.bar(
                category_counts,
                x="category",
                y="documents",
                color="category",
                title="Documents by Category",
                color_discrete_sequence=["#4F46E5", "#0891B2", "#059669", "#7C3AED", "#D97706"],
            )
            figure.update_layout(showlegend=False, title_x=0.02)
            st.plotly_chart(apply_plotly_theme(figure, UI_THEME), use_container_width=True)

    with language_col:
        with st.container(border=True):
            render_section_header("Language mix", "Detected language distribution across the prepared corpus.")
            language_counts = document_df["language"].value_counts().reset_index()
            language_counts.columns = ["language", "documents"]
            language_counts["language"] = language_counts["language"].astype(str).str.upper()
            figure = px.pie(
                language_counts,
                names="language",
                values="documents",
                title="Language Mix",
                color_discrete_sequence=["#4F46E5", "#0891B2", "#059669", "#7C3AED", "#D97706"],
            )
            figure.update_layout(title_x=0.02)
            st.plotly_chart(apply_plotly_theme(figure, UI_THEME), use_container_width=True)

    render_dataframe_section(
        "Prepared documents",
        "The standardized table used by downstream NLP, keyword extraction, search, and exports.",
        document_df,
    )


def render_entities_section(top_n: int) -> None:
    entity_df = st.session_state["entity_df"]
    if entity_df is None:
        render_empty_state("🏷️", "No analysis yet", "Run NLP Analysis from the Input tab to extract named entities.")
        return
    if entity_df.empty:
        render_empty_state("🏷️", "No entities found", "The current corpus did not produce named entities.")
        return

    stats = get_stats(top_n)
    render_section_header(
        "Entity analysis",
        "Identify people, organizations, places, dates, quantities, and other named concepts.",
        overline="Entities",
    )

    metric_cols = st.columns(3)
    for col, (label, value) in zip(
        metric_cols,
        [
            ("Entity Mentions", stats["total_entities"]),
            ("Unique Entities", stats["unique_entities"]),
            ("Docs With Entities", stats["documents_with_entities"]),
        ],
        strict=False,
    ):
        with col:
            render_stat_card(label, value)

    chart_col, label_col = st.columns([1.3, 1], gap="large")
    with chart_col:
        with st.container(border=True):
            render_section_header("Top entities", "Most frequent entity mentions and labels.")
            st.plotly_chart(plot_top_entities(stats["top_entities"], UI_THEME), use_container_width=True)
    with label_col:
        with st.container(border=True):
            render_section_header("Entity type mix", "Mention counts by spaCy entity label.")
            st.plotly_chart(plot_label_distribution(stats["label_counts"], UI_THEME), use_container_width=True)

    with st.expander("Entity label descriptions", expanded=False):
        descriptions = pd.DataFrame(
            [
                {"label": label, "description": description}
                for label, description in get_entity_label_descriptions().items()
            ]
        )
        st.dataframe(descriptions, use_container_width=True, hide_index=True)

    with st.container(border=True):
        render_section_header("Entity explorer", "Filter the entity table by label, source, category, or language.")
        filter_cols = st.columns(4)
        with filter_cols[0]:
            selected_labels = st.multiselect(
                "Entity labels",
                sorted(entity_df["label"].dropna().astype(str).unique()),
                key="entity_filter_labels",
            )
        with filter_cols[1]:
            selected_sources = st.multiselect(
                "Sources",
                sorted(entity_df["source_name"].dropna().astype(str).unique()),
                format_func=lambda value: shorten_filename(display_unknown(value), max_chars=30),
                key="entity_filter_sources",
            )
        with filter_cols[2]:
            selected_categories = st.multiselect(
                "Categories",
                sorted(entity_df["category"].dropna().astype(str).unique()),
                format_func=display_category,
                key="entity_filter_categories",
            )
        with filter_cols[3]:
            selected_languages = st.multiselect(
                "Languages",
                sorted(entity_df["language"].dropna().astype(str).unique()),
                format_func=lambda value: display_unknown(value).upper(),
                key="entity_filter_languages",
            )

        filtered_entities = entity_df.copy()
        if selected_labels:
            filtered_entities = filtered_entities[filtered_entities["label"].isin(selected_labels)]
        if selected_sources:
            filtered_entities = filtered_entities[filtered_entities["source_name"].isin(selected_sources)]
        if selected_categories:
            filtered_entities = filtered_entities[filtered_entities["category"].isin(selected_categories)]
        if selected_languages:
            filtered_entities = filtered_entities[filtered_entities["language"].isin(selected_languages)]

        summary_cols = st.columns(2)
        with summary_cols[0]:
            render_stat_card("Filtered Mentions", len(filtered_entities))
        with summary_cols[1]:
            render_stat_card("Filtered Unique Entities", filtered_entities["entity_text"].nunique())

        if filtered_entities.empty:
            render_empty_state("🔎", "No matching entities", "Adjust filters to bring entity mentions back into view.")
        else:
            st.dataframe(filtered_entities, use_container_width=True, hide_index=True)

    with st.container(border=True):
        render_section_header("Entity drilldown", "Select one entity to see where it appears and the surrounding document context.")
        if filtered_entities.empty:
            render_empty_state("🧭", "No entity selected", "Adjust filters to select an entity for drilldown.")
            return

        entity_options = sorted(filtered_entities["entity_text"].dropna().astype(str).unique())
        if not entity_options:
            render_empty_state("🧭", "No entity selected", "Filtered rows do not include entity text values.")
            return

        selected_entity = st.selectbox(
            "Select an entity",
            entity_options,
            key="entity_drilldown_select",
        )
        contexts = get_entity_contexts(
            st.session_state["document_df"],
            entity_df,
            selected_entity,
            window=140,
        )
        if contexts.empty:
            render_empty_state("🧭", "No contexts found", "No matching document contexts were found.")
            return

        drill_cols = st.columns(3)
        with drill_cols[0]:
            render_stat_card("Mentions", int(contexts["mention_count"].sum()))
        with drill_cols[1]:
            render_stat_card("Documents", contexts["document_id"].nunique())
        with drill_cols[2]:
            labels = sorted(label for label in set(", ".join(contexts["labels"]).split(", ")) if label)
            render_stat_card("Labels", ", ".join(labels))
        st.dataframe(contexts, use_container_width=True, hide_index=True)


def render_keywords_section(top_n: int) -> None:
    document_df = st.session_state["document_df"]
    if is_empty(document_df):
        render_empty_state("🔑", "No keywords yet", "Load documents to extract TF-IDF keywords and keyphrases.")
        return

    render_section_header(
        "Keyword insights",
        "Keywords use TF-IDF statistical weighting over normalized search text, with English stop-word removal.",
        overline="Keywords",
    )
    keyword_df, document_keyword_df = get_keyword_data(top_n)

    if keyword_df.empty:
        render_empty_state("🔑", "No keywords found", "The current corpus did not produce TF-IDF keyword features.")
    else:
        with st.container(border=True):
            render_section_header("Top corpus keywords", "The most distinctive terms and phrases across the full corpus.")
            st.plotly_chart(plot_keywords(keyword_df, UI_THEME), use_container_width=True)
            st.dataframe(keyword_df, use_container_width=True, hide_index=True)
            st.download_button(
                label="Download keywords CSV",
                data=dataframe_to_csv_bytes(keyword_df),
                file_name="keywords.csv",
                mime="text/csv",
                key="download_keywords_csv_tab",
                use_container_width=True,
            )

    with st.container(border=True):
        render_section_header("Per-document keywords", "Inspect top TF-IDF terms for individual documents.")
        if document_keyword_df.empty:
            render_empty_state("📄", "No document keywords", "No per-document keywords are available yet.")
        else:
            st.dataframe(document_keyword_df, use_container_width=True, hide_index=True)


def render_document_explorer_section(top_n: int) -> None:
    document_df = st.session_state["document_df"]
    if is_empty(document_df):
        render_empty_state("📄", "No documents loaded", "Paste text, upload files, or load the sample corpus first.")
        return

    render_section_header(
        "Document explorer",
        "Inspect one document as a detail page: metadata, raw text, detected entities, and document-level keywords.",
        overline="Explorer",
    )
    document_options = document_df["id"].dropna().astype(str).tolist()
    document_lookup = {
        str(row["id"]): row
        for _, row in document_df.iterrows()
        if pd.notna(row.get("id"))
    }
    if not document_options:
        render_empty_state("📄", "No selectable documents", "The loaded corpus has no document identifiers.")
        return

    with st.container(border=True):
        render_section_header("Select a document", "Labels are shortened for readability; full identifiers remain available in metadata.")
        selected_document_id = st.selectbox(
            "Select document",
            document_options,
            format_func=lambda doc_id: document_option_label(document_lookup.get(str(doc_id), pd.Series())),
            key="document_explorer_select",
        )

    selected_document = document_lookup[str(selected_document_id)]
    clean_category = display_category(selected_document.get("category", ""))
    clean_language = display_unknown(selected_document.get("language", ""))
    source_name = display_unknown(selected_document.get("source_name", ""))
    full_document_id = str(selected_document.get("id", ""))
    full_text = str(selected_document.get("text", ""))
    word_count = len(full_text.split())

    with st.container(border=True):
        render_section_header("Document metadata", "Compact cards keep long IDs readable without changing internal identifiers.")
        first_row = st.columns(3)
        with first_row[0]:
            render_stat_card("Doc ID", shorten_identifier(full_document_id, prefix_chars=3, max_chars=12), full_document_id)
        with first_row[1]:
            render_stat_card("Source", shorten_filename(source_name, max_chars=28), source_name)
        with first_row[2]:
            render_stat_card("Category", clean_category)

        second_row = st.columns(3)
        with second_row[0]:
            render_stat_card("Language", clean_language.upper(), clean_language)
        with second_row[1]:
            render_stat_card("Characters", selected_document["text_length"])
        with second_row[2]:
            render_stat_card("Words", word_count)

        st.caption(
            f"Selected document: {shorten_filename(source_name, max_chars=48)} | "
            f"ID: {shorten_identifier(full_document_id, prefix_chars=3, max_chars=14)}"
        )

        with st.expander("Full document metadata", expanded=False):
            metadata = pd.DataFrame(
                [
                    {"field": "document_id", "value": full_document_id},
                    {"field": "source_name", "value": source_name},
                    {"field": "category", "value": clean_category},
                    {"field": "language", "value": clean_language},
                    {"field": "text_length", "value": str(int(selected_document.get("text_length", 0)))},
                    {"field": "word_count", "value": str(word_count)},
                ]
            )
            st.dataframe(metadata, use_container_width=True, hide_index=True)

    with st.container(border=True):
        render_section_header("Raw text preview", "A read-only preview of the original document text.")
        st.text_area(
            "Document text",
            value=full_text,
            height=280,
            disabled=True,
            label_visibility="collapsed",
        )

    with st.container(border=True):
        render_section_header("Entities in this document", "Detected named entities for the selected document.")
        entity_df = st.session_state["entity_df"]
        if is_empty(entity_df):
            render_empty_state("🏷️", "No entities yet", "Run NLP Analysis to see document-level entities.")
        else:
            doc_entities = entity_df[entity_df["document_id"] == selected_document_id]
            if doc_entities.empty:
                render_empty_state("🏷️", "No entities found", "This document has no detected named entities.")
            else:
                st.dataframe(doc_entities, use_container_width=True, hide_index=True)

    with st.container(border=True):
        render_section_header("Top keywords in this document", "Per-document TF-IDF terms and phrases.")
        _, document_keyword_df = get_keyword_data(top_n)
        if document_keyword_df is None or document_keyword_df.empty or "document_id" not in document_keyword_df.columns:
            doc_keywords = pd.DataFrame()
        else:
            doc_keywords = document_keyword_df[document_keyword_df["document_id"] == selected_document_id]

        if doc_keywords.empty:
            render_empty_state("🔑", "No keywords found", "No keywords were extracted for this document.")
        else:
            st.dataframe(doc_keywords, use_container_width=True, hide_index=True)


def render_relationships_section(top_n: int) -> None:
    render_section_header(
        "Relationships",
        "Explore entity co-occurrence and cross-category patterns from the analyzed corpus.",
        overline="Relationships",
    )
    entity_df = st.session_state["entity_df"]
    if entity_df is None:
        render_empty_state("🔗", "No analysis yet", "Run NLP Analysis before exploring relationships.")
        return

    stats = get_stats(top_n)
    co_occurrence = stats["co_occurrence"]
    cross_category = stats["cross_category"]

    with st.container(border=True):
        render_section_header("Entity co-occurrence", "Pairs are counted once per document, even if an entity appears multiple times.")
        if co_occurrence.empty:
            render_empty_state("🔗", "No pairs found", "At least two unique entities must appear in a document.")
        else:
            st.dataframe(show_co_occurrence_table(co_occurrence, UI_THEME), use_container_width=True)

    with st.container(border=True):
        render_section_header("Cross-category patterns", "Compare entity label distribution across document categories.")
        if cross_category.empty:
            render_empty_state("🧭", "No patterns found", "Add categorized documents with detected entities.")
        else:
            st.plotly_chart(plot_cross_category(cross_category, UI_THEME), use_container_width=True)
            st.dataframe(cross_category, use_container_width=True, hide_index=True)


def render_search_result_card(row: pd.Series) -> None:
    score_pct = f"{float(row['similarity_score']) * 100:.0f}%"
    source_name = display_unknown(row.get("source_name", ""))
    source_label = shorten_filename(source_name, max_chars=54)
    category = display_category(row.get("category", ""))
    language = display_unknown(row.get("language", "")).upper()

    with st.container(border=True):
        score_col, detail_col = st.columns([1, 5], gap="large")
        with score_col:
            render_stat_card("Match", score_pct)
        with detail_col:
            st.markdown(f"**{source_label}**")
            st.caption(f"{category} · {language}")
            st.write(str(row["text_preview"]))


def render_search_section(search_top_k: int) -> None:
    document_df = st.session_state["document_df"]
    if is_empty(document_df):
        render_empty_state("🔎", "Nothing to search", "Load documents first, then search.")
        return

    render_section_header(
        "Search documents",
        "TF-IDF search ranks documents by keyword importance and cosine similarity.",
        overline="Search",
    )
    if st.session_state["vectorizer"] is None or st.session_state["tfidf_matrix"] is None:
        st.session_state["vectorizer"], st.session_state["tfidf_matrix"] = build_tfidf_index(document_df)

    with st.container(border=True):
        render_section_header("Ask the corpus", "Search for organizations, places, themes, or policy topics.")
        st.caption("Try: Apple · public health · Amman · climate policy · artificial intelligence")
        query = st.text_input("Search query", placeholder="Try: Apple, public health, Amman, climate policy")

        if not query:
            render_empty_state("🔎", "Enter a query", "Search results will appear here as ranked cards.")
            return

        results = search_documents(
            query,
            document_df,
            st.session_state["vectorizer"],
            st.session_state["tfidf_matrix"],
            top_k=search_top_k,
        )
        if results.empty:
            render_empty_state("🔎", "No matches", "Try a broader query or load more documents.")
            return

        for _, row in results.iterrows():
            render_search_result_card(row)


def render_report_section(top_n: int) -> None:
    document_df = st.session_state["document_df"]
    if is_empty(document_df):
        render_empty_state("📝", "No report yet", "Add documents and run analysis to generate a report.")
        return

    render_section_header(
        "Analysis report",
        "A Markdown-ready summary of corpus structure, entity findings, keywords, co-occurrence, category patterns, and limitations.",
        overline="Report",
    )
    report = get_report(top_n)

    with st.container(border=True):
        render_section_header("Report preview", "This preview is the same content used by the Markdown download.")
        st.markdown(report)
        st.download_button(
            label="Download markdown report",
            data=markdown_to_bytes(report),
            file_name="nlp_analysis_report.md",
            mime="text/markdown",
            key="download_report_md_report_tab",
            use_container_width=True,
        )


def render_downloads_section(top_n: int) -> None:
    document_df = st.session_state["document_df"]
    entity_df = st.session_state["entity_df"]
    if is_empty(document_df):
        render_empty_state("⬇️", "No files to download", "Load documents and run analysis to enable exports.")
        return

    stats = get_stats(top_n)
    keyword_df, document_keyword_df = get_keyword_data(top_n)
    report = get_report(top_n)
    analysis_summary = build_analysis_summary(document_df, entity_df, stats, keyword_df)
    full_analysis_export = build_full_analysis_export(
        document_df,
        entity_df,
        stats,
        keyword_df,
        document_keyword_df,
    )

    render_section_header(
        "Downloads",
        "All exports are generated in memory for Streamlit Cloud compatibility.",
        overline="Export",
    )

    left, right = st.columns(2, gap="large")
    with left:
        with st.container(border=True):
            render_section_header("Corpus", "Standardized document rows used by the app.")
            st.download_button(
                label="Download prepared corpus CSV",
                data=dataframe_to_csv_bytes(document_df),
                file_name="prepared_documents.csv",
                mime="text/csv",
                key="download_prepared_documents_csv",
                use_container_width=True,
            )

        with st.container(border=True):
            render_section_header("Entities", "Raw mentions plus aggregated entity outputs.")
            entities_unavailable = entity_df is None or entity_df.empty
            if entities_unavailable:
                st.caption("Run NLP Analysis to enable entity exports.")
            st.download_button(
                label="Download extracted entities CSV",
                data=dataframe_to_csv_bytes(entity_df),
                file_name="extracted_entities.csv",
                mime="text/csv",
                disabled=entities_unavailable,
                key="download_extracted_entities_csv",
                use_container_width=True,
            )
            st.download_button(
                label="Download top entities CSV",
                data=dataframe_to_csv_bytes(stats.get("top_entities")),
                file_name="top_entities.csv",
                mime="text/csv",
                disabled=stats.get("top_entities") is None or stats.get("top_entities").empty,
                key="download_top_entities_csv",
                use_container_width=True,
            )
            st.download_button(
                label="Download entity label counts CSV",
                data=dataframe_to_csv_bytes(stats.get("label_counts")),
                file_name="entity_label_counts.csv",
                mime="text/csv",
                disabled=stats.get("label_counts") is None or stats.get("label_counts").empty,
                key="download_entity_label_counts_csv",
                use_container_width=True,
            )

        with st.container(border=True):
            render_section_header("Keywords", "Corpus-level TF-IDF keywords and keyphrases.")
            st.download_button(
                label="Download keywords CSV",
                data=dataframe_to_csv_bytes(keyword_df),
                file_name="keywords.csv",
                mime="text/csv",
                disabled=keyword_df is None or keyword_df.empty,
                key="download_keywords_csv",
                use_container_width=True,
            )

    with right:
        with st.container(border=True):
            render_section_header("Relationships", "Entity co-occurrence and cross-category pattern tables.")
            st.download_button(
                label="Download co-occurrence CSV",
                data=dataframe_to_csv_bytes(stats.get("co_occurrence")),
                file_name="entity_co_occurrence.csv",
                mime="text/csv",
                disabled=stats.get("co_occurrence") is None or stats.get("co_occurrence").empty,
                key="download_co_occurrence_csv",
                use_container_width=True,
            )
            st.download_button(
                label="Download cross-category CSV",
                data=dataframe_to_csv_bytes(stats.get("cross_category")),
                file_name="cross_category_patterns.csv",
                mime="text/csv",
                disabled=stats.get("cross_category") is None or stats.get("cross_category").empty,
                key="download_cross_category_patterns_csv",
                use_container_width=True,
            )

        with st.container(border=True):
            render_section_header("Report", "Markdown report suitable for sharing or further editing.")
            st.download_button(
                label="Download markdown report",
                data=markdown_to_bytes(report),
                file_name="nlp_analysis_report.md",
                mime="text/markdown",
                key="download_report_md",
                use_container_width=True,
            )

        with st.container(border=True):
            render_section_header("JSON exports", "Machine-readable summaries for downstream analysis.")
            st.download_button(
                label="Download analysis summary JSON",
                data=dict_to_json_bytes(analysis_summary),
                file_name="analysis_summary.json",
                mime="application/json",
                key="download_analysis_summary_json",
                use_container_width=True,
            )
            st.download_button(
                label="Download full analysis JSON",
                data=dict_to_json_bytes(full_analysis_export),
                file_name="full_analysis_export.json",
                mime="application/json",
                key="download_full_analysis_export_json",
                use_container_width=True,
            )


def render_footer() -> None:
    st.divider()
    st.caption(
        "Built by **Osama Harrab** | "
        "[GitHub](https://github.com/osamaharrab) | "
        "[LinkedIn](https://www.linkedin.com/in/osama-harrab-694a2a381/)  \n"
        "Powered by spaCy · scikit-learn · Plotly · Streamlit"
    )


def main() -> None:
    init_session_state()
    inject_css()
    top_n, search_top_k, split_pdf_pages = render_sidebar()
    render_header()
    render_status_strip()
    section = render_top_navigation()

    if section == "Input":
        render_input_section(top_n, split_pdf_pages)
    elif section == "Overview":
        render_overview_section(top_n)
    elif section == "Entities":
        render_entities_section(top_n)
    elif section == "Keywords":
        render_keywords_section(top_n)
    elif section == "Explorer":
        render_document_explorer_section(top_n)
    elif section == "Relationships":
        render_relationships_section(top_n)
    elif section == "Search":
        render_search_section(search_top_k)
    elif section == "Report":
        render_report_section(top_n)
    elif section == "Downloads":
        render_downloads_section(top_n)

    render_footer()


main()
