"""Plotly visualizations for NLP analytics."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PRIMARY = "#4F46E5"
ACCENT = "#0891B2"
TEXT = "#111827"
CARD_BG = "#FFFFFF"
GRID = "#DDE5F0"
CHART_SEQUENCE = ["#4F46E5", "#0891B2", "#059669", "#7C3AED", "#D97706", "#DC2626"]


def get_plotly_theme(theme: str = "Light") -> dict[str, object]:
    """Return Plotly layout colors for the light app theme."""
    return {
        "template": "plotly_white",
        "paper_bgcolor": CARD_BG,
        "plot_bgcolor": CARD_BG,
        "font_color": TEXT,
        "grid_color": GRID,
        "table_bg": CARD_BG,
        "table_header_bg": "#F8FAFC",
        "discrete_sequence": CHART_SEQUENCE,
        "continuous_scale": ["#E0F2FE", ACCENT, PRIMARY],
    }


def apply_plotly_theme(figure: go.Figure, theme: str = "Light") -> go.Figure:
    """Apply app theme colors to a Plotly figure."""
    colors = get_plotly_theme(theme)
    figure.update_layout(
        template=colors["template"],
        paper_bgcolor=colors["paper_bgcolor"],
        plot_bgcolor=colors["plot_bgcolor"],
        font={"color": colors["font_color"]},
        title={"font": {"size": 18, "color": colors["font_color"]}},
        legend={"font": {"color": colors["font_color"]}},
        margin={"l": 22, "r": 22, "t": 54, "b": 26},
    )
    figure.update_xaxes(
        gridcolor=colors["grid_color"],
        zerolinecolor=colors["grid_color"],
        linecolor=colors["grid_color"],
        tickfont={"color": colors["font_color"]},
        title_font={"color": colors["font_color"]},
    )
    figure.update_yaxes(
        gridcolor=colors["grid_color"],
        zerolinecolor=colors["grid_color"],
        linecolor=colors["grid_color"],
        tickfont={"color": colors["font_color"]},
        title_font={"color": colors["font_color"]},
    )
    return figure


def _empty_figure(message: str, theme: str = "Light") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"color": get_plotly_theme(theme)["font_color"], "size": 14},
    )
    figure.update_layout(
        height=360,
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
    )
    return apply_plotly_theme(figure, theme)


def plot_top_entities(top_entities: pd.DataFrame, theme: str = "Light") -> go.Figure:
    """Render a horizontal bar chart for top entities."""
    if top_entities is None or top_entities.empty:
        return _empty_figure("No entities available yet.", theme)

    chart_df = top_entities.copy().sort_values("count", ascending=True)
    chart_df["entity_label"] = chart_df["entity_text"] + " (" + chart_df["label"] + ")"
    colors = get_plotly_theme(theme)

    figure = px.bar(
        chart_df,
        x="count",
        y="entity_label",
        orientation="h",
        color="label",
        color_discrete_sequence=colors["discrete_sequence"],
        labels={"count": "Mentions", "entity_label": "Entity"},
        title="Top Entities",
    )
    figure.update_layout(height=460, title_x=0.02)
    return apply_plotly_theme(figure, theme)


def plot_label_distribution(label_counts: pd.DataFrame, theme: str = "Light") -> go.Figure:
    """Render a bar chart for entity label distribution."""
    if label_counts is None or label_counts.empty:
        return _empty_figure("No labels available yet.", theme)

    colors = get_plotly_theme(theme)
    figure = px.bar(
        label_counts,
        x="label",
        y="count",
        color="label",
        color_discrete_sequence=colors["discrete_sequence"],
        labels={"label": "Entity Type", "count": "Mentions"},
        title="Entity Labels",
    )
    figure.update_layout(height=420, showlegend=False, title_x=0.02)
    return apply_plotly_theme(figure, theme)


def plot_keywords(keyword_df: pd.DataFrame, theme: str = "Light") -> go.Figure:
    """Render a horizontal bar chart for top TF-IDF keywords."""
    if keyword_df is None or keyword_df.empty:
        return _empty_figure("No keywords available yet.", theme)

    chart_df = keyword_df.copy().sort_values("score", ascending=True)
    colors = get_plotly_theme(theme)
    figure = px.bar(
        chart_df,
        x="score",
        y="keyword",
        orientation="h",
        color="document_count",
        color_continuous_scale=colors["continuous_scale"],
        labels={"score": "TF-IDF Score", "keyword": "Keyword", "document_count": "Documents"},
        title="Top Keywords",
    )
    figure.update_layout(height=460, title_x=0.02)
    return apply_plotly_theme(figure, theme)


def plot_cross_category(cross_category_df: pd.DataFrame, theme: str = "Light") -> go.Figure:
    """Render a heatmap of entity label mentions by category."""
    if cross_category_df is None or cross_category_df.empty:
        return _empty_figure("No cross-category patterns available yet.", theme)

    pivot = cross_category_df.pivot_table(
        index="category",
        columns="label",
        values="entity_mentions",
        aggfunc="sum",
        fill_value=0,
    )
    colors = get_plotly_theme(theme)
    figure = px.imshow(
        pivot,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=colors["continuous_scale"],
        labels={"x": "Entity Type", "y": "Category", "color": "Mentions"},
        title="Entity Patterns by Category",
    )
    figure.update_layout(height=440, title_x=0.02)
    return apply_plotly_theme(figure, theme)


def show_co_occurrence_table(co_occurrence_df: pd.DataFrame, theme: str = "Light"):
    """Return a styled co-occurrence table for Streamlit display."""
    if co_occurrence_df is None or co_occurrence_df.empty:
        return pd.DataFrame(columns=["entity_1", "entity_2", "cooccurrence_count"])

    colors = get_plotly_theme(theme)
    return (
        co_occurrence_df.style.background_gradient(
            subset=["cooccurrence_count"],
            cmap="PuBu",
        )
        .set_properties(
            **{
                "background-color": colors["table_bg"],
                "color": colors["font_color"],
                "border-color": colors["grid_color"],
            }
        )
        .set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("background-color", colors["table_header_bg"]),
                        ("color", colors["font_color"]),
                    ],
                },
                {"selector": "td", "props": [("border-color", colors["grid_color"])]},
            ]
        )
    )
