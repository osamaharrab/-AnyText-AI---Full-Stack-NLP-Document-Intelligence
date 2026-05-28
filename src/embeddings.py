"""Optional embedding utilities.

This module is intentionally disabled by default. It only imports transformers and
torch inside functions so the core Streamlit Cloud app remains lightweight.
"""

from __future__ import annotations


def embeddings_available() -> tuple[bool, str]:
    """Return whether optional transformer embeddings can be used."""
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401
    except Exception:
        return (
            False,
            "Transformer embeddings are optional and are not installed in this deployment.",
        )

    return True, "Transformer embeddings are available."


def compute_optional_embeddings(texts, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    """Compute optional embeddings when torch and transformers are installed."""
    available, message = embeddings_available()
    if not available:
        return None, message

    try:
        from transformers import AutoModel, AutoTokenizer
        import torch
    except Exception:
        return None, message

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()

    encoded = tokenizer(list(texts), padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        output = model(**encoded)
        embeddings = output.last_hidden_state.mean(dim=1).cpu().numpy()

    return embeddings, "Embeddings computed successfully."
