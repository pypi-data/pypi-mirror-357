from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    def __hash__(self) -> int:
        return hash(self.model_dump_json())
