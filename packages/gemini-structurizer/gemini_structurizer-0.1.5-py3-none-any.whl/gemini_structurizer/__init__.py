# gemini_structurizer/__init__.py

# 只导出对库使用者有用的公共API
from .processor import structure_file_with_gemini

__all__ = [
    "structure_file_with_gemini",
    "create_config_template"
]