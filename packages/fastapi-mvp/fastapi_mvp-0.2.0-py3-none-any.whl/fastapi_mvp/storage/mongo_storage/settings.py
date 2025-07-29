from fastapi_mvp.settings import Settings


class MongoSettings(Settings):
    name: str
    user: str
    password: str
    host: str
    port: int

    def url(self) -> str:
        return f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}"
