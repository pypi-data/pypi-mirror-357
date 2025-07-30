# weaver/config.py

import os
from pathlib import Path

# Base LLM configurations (model identifiers, API params, and token‐costs)
LLM_CONFIG = {
    "main_orchestrator": os.getenv("WEAVER_ORCHESTRATOR", "gpt-4-turbo"),
    "available_llms": {
        "gpt-4-turbo": {
            "model": "openai/gpt-4-turbo",
            "max_tokens": 8192,
            # cost per 1k tokens in USD (prompt vs. completion)
            "cost_per_1k_tokens": {"prompt": 0.0015, "completion": 0.0020},
            # Other litellm params can go here, e.g. api_key via env
        },
        "gemini-1.5-pro": {
            "model": "gemini/gemini-1.5-pro",
            "max_tokens": 8192,
            "cost_per_1k_tokens": {"prompt": 0.0020, "completion": 0.0025},
        },
        # Users can add more models here…
    },
}

# Helper to fetch a model's config dict
def get_model_config(key: str):
    try:
        return LLM_CONFIG["available_llms"][key]
    except KeyError:
        raise KeyError(f"LLM config key '{key}' not found in available_llms.")
