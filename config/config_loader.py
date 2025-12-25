from pathlib import Path
import yaml
from pydantic import BaseModel, Field, ValidationError
from typing import Literal


# -----------------------------
# Pydantic schemas
# -----------------------------

class TemperatureConfig(BaseModel):
    extraction: float = Field(ge=0.0, le=1.0)
    reasoning: float = Field(ge=0.0, le=1.0)


class LLMConfig(BaseModel):
    extraction_model: Literal[
        "claude-haiku-4-5",
        "claude-sonnet-4-5",
        "claude-opus-4-5",
    ]
    reasoning_model: Literal[
        "claude-haiku-4-5",
        "claude-sonnet-4-5",
        "claude-opus-4-5",
    ]
    temperature: TemperatureConfig
    max_tokens: int = Field(gt=0, le=8000)


class PathsConfig(BaseModel):
    contracts_dir: Path
    invoices_dir: Path
    output_dir: Path


class GovernanceConfig(BaseModel):
    enable_pii_masking: bool
    enable_audit_logs: bool


class AppConfig(BaseModel):
    llm: LLMConfig
    paths: PathsConfig
    governance: GovernanceConfig


# -----------------------------
# Loader
# -----------------------------

def load_config(config_path: str = "config/config.yaml") -> AppConfig:
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file, "r") as f:
        raw_config = yaml.safe_load(f)

    try:
        return AppConfig(**raw_config)
    except ValidationError as e:
        raise RuntimeError(
            "Invalid configuration. Fix config/config.yaml before running."
        ) from e
