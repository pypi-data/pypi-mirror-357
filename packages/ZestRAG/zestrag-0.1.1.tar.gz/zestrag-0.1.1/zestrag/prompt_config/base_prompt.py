from pydantic_settings import BaseSettings


class BasePromptSettings(BaseSettings):
    default_language: str
    default_tuple_delimiter: str
    default_record_delimiter: str
    default_completion_delimiter: str
    default_entity_types: list[str]
    default_user_prompt: str
    entity_extraction: str
    entity_extraction_examples: list[str]
    summarize_entity_descriptions: str
    entity_continue_extraction: str
    entity_if_loop_extraction: str
    fail_response: str
    rag_response: str
    keywords_extraction: str
    keywords_extraction_examples: list[str]
    naive_rag_response: str
    similarity_check: str
