from dataclasses import dataclass
from typing import Optional


@dataclass
class ScanConfig:
    target_url: str
    timeout: int = 10
    concurrency: int = 10
    max_depth: int = 1
    max_pages: int = 10
    output_path: Optional[str] = None