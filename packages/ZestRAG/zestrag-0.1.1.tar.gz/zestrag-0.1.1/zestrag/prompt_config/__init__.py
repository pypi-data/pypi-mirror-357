from .base_prompt import BasePromptSettings
from .chinese_prompt import PromptSettings as ChinesePromptSettings



cn_prompt_settings = ChinesePromptSettings()



__all__ = [
    "cn_prompt_settings",
    "BasePromptSettings"
]
