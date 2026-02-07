"""
Ring Buffer Logging System.

Prevents log files from growing forever by:
- Limiting the maximum number of lines per log file.
- Limiting the total number of log files kept on disk.
- Rotating automatically: oldest file is deleted when the cap is hit.

Think of it like a circular notebook — when you fill the last page,
you tear out the oldest page to make room.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


class RingBufferHandler(logging.Handler):
    """Logging handler that rotates files based on line count."""

    def __init__(
        self,
        log_dir: Path,
        max_lines: int = 1000,
        max_files: int = 5,
        filename_pattern: str = "app_{timestamp}.log",
    ) -> None:
        super().__init__()
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.max_lines = max_lines
        self.max_files = max_files
        self.filename_pattern = filename_pattern
        self.current_line_count = 0
        self.file_handle: Optional[object] = None
        self._rotate_file()

    # -- internal helpers ---------------------------------------------------

    def _new_filename(self) -> str:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.filename_pattern.replace("{timestamp}", stamp)

    def _rotate_file(self) -> None:
        """Close current log, open a fresh one, prune old files."""
        if self.file_handle:
            self.file_handle.close()
        path = self.log_dir / self._new_filename()
        self.file_handle = open(path, "w", encoding="utf-8")
        self.current_line_count = 0
        self._cleanup()

    def _cleanup(self) -> None:
        """Delete oldest log files when we exceed *max_files*."""
        logs = sorted(self.log_dir.glob("*.log"), key=lambda f: f.stat().st_mtime)
        while len(logs) > self.max_files:
            logs.pop(0).unlink()

    # -- public API ---------------------------------------------------------

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record) + "\n"
            self.file_handle.write(msg)
            self.file_handle.flush()
            self.current_line_count += 1
            if self.current_line_count >= self.max_lines:
                self._rotate_file()
        except Exception:
            self.handleError(record)

    def get_status(self) -> dict:
        """Return dict with file_count, total_lines, total_size_kb."""
        logs = list(self.log_dir.glob("*.log"))
        total_lines = 0
        total_size = 0
        for f in logs:
            total_size += f.stat().st_size
            total_lines += sum(1 for _ in open(f, encoding="utf-8"))
        return {
            "file_count": len(logs),
            "total_lines": total_lines,
            "total_size_kb": round(total_size / 1024, 2),
            "max_lines_per_file": self.max_lines,
            "max_files": self.max_files,
        }

    def close(self) -> None:
        if self.file_handle:
            self.file_handle.close()
        super().close()


def setup_logger(
    name: str = "app", config_path: Optional[Path] = None
) -> logging.Logger:
    """
    Create a logger backed by a RingBufferHandler.

    Args:
        name: Logger name (e.g. ``"task1"``).
        config_path: Path to ``log_config.json``. Falls back to defaults.
    """
    if config_path and config_path.exists():
        cfg = json.loads(config_path.read_text())["ring_buffer"]
    else:
        cfg = {
            "max_lines_per_file": 1000,
            "max_log_files": 5,
            "log_directory": "logs",
            "log_level": "INFO",
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        }

    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, cfg["log_level"]))
        handler = RingBufferHandler(
            log_dir=Path(cfg["log_directory"]),
            max_lines=cfg["max_lines_per_file"],
            max_files=cfg["max_log_files"],
        )
        handler.setFormatter(logging.Formatter(cfg["format"]))
        logger.addHandler(handler)
    return logger


def print_log_status(logger: logging.Logger) -> None:
    """Print a short summary of current log usage."""
    for h in logger.handlers:
        if isinstance(h, RingBufferHandler):
            s = h.get_status()
            print(f"\nLog status: {s['file_count']}/{s['max_files']} files, "
                  f"{s['total_lines']} lines, {s['total_size_kb']} KB")
            break
