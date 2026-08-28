import os

from omegaconf import DictConfig, OmegaConf


def build_from_configs(obj, cfg: DictConfig, **kwargs):
    if cfg is None:
        return None
    cfg = cfg.copy()
    if isinstance(cfg, DictConfig):
        OmegaConf.set_struct(cfg, False)
    type = cfg.pop("type")
    return getattr(obj, type)(**cfg, **kwargs)


def format_number(n, decimal_places=2):
    return f"{n:+.{decimal_places}f}" if abs(round(n, decimal_places)) > 1e-2 else "0.0"


def _to_scalar(value):
    return value.item() if hasattr(value, "item") else value


def format_history_context(history_trajectory):
    history_len = len(history_trajectory)
    prompt_format = os.environ.get("SGDRIVE_HISTORY_PROMPT_FORMAT", "legacy").lower()
    if prompt_format not in {"current", "legacy"}:
        raise ValueError(
            "SGDRIVE_HISTORY_PROMPT_FORMAT must be 'current' or 'legacy', "
            f"got {prompt_format!r}"
        )
    prefix = "-t-" if prompt_format == "current" else "   - t-"
    return " ".join(
        [
            (
                f"{prefix}{history_len - 1 - i}: "
                f"({format_number(_to_scalar(history_trajectory[i][0]))}, "
                f"{format_number(_to_scalar(history_trajectory[i][1]))}, "
                f"{format_number(_to_scalar(history_trajectory[i][2]))})"
            )
            for i in range(history_len)
        ]
    )


def get_navigation_command(high_command_one_hot):
    navigation_commands = ["turn left", "go straight", "turn right"]
    for i, value in enumerate(high_command_one_hot):
        if int(_to_scalar(value)) == 1:
            return navigation_commands[i] if i < len(navigation_commands) else "unknown"
    return "unknown"
