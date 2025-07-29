from __future__ import annotations

from typing import Annotated, Optional

from fastapi import Depends, FastAPI

from fastapi_mvp.metrics import MetricsSettings, instrument_app
from fastapi_mvp.storage.mongo_storage import (
    MongoSettings,
    MongoStorage,
    get_mongo_storage,
)
from fastapi_mvp.storage.s3_storage import (
    S3Settings,
    S3Storage,
    get_s3_storage,
)


class Mvp:
    __instance__: Optional[Mvp] = None

    def __init__(
        self,
        fastapi_app: FastAPI,
        mongo_storage: Optional[MongoStorage] = None,
        s3_storage: Optional[S3Storage] = None,
    ) -> None:
        self.__fastapi_app = fastapi_app  # pylint: disable=unused-private-member
        self.__mongo_storage = mongo_storage
        self.__s3_storage = s3_storage

    def mongo(self) -> MongoStorage:
        if self.__mongo_storage is None:
            err = "Provide mongo settings to Mvp.setup() to use MongoDB."
            raise RuntimeError(err)

        return self.__mongo_storage

    def s3(self) -> S3Storage:
        if self.__s3_storage is None:
            err = "Provide s3 settings to Mvp.setup() to use S3 Object Storage."
            raise RuntimeError(err)

        return self.__s3_storage

    @classmethod
    def setup(
        cls,
        app: FastAPI,
        mongo: Optional[MongoSettings] = None,
        s3: Optional[S3Settings] = None,
        metrics: Optional[MetricsSettings] = None,
    ) -> None:
        mongo_storage = get_mongo_storage(mongo) if mongo else None
        s3_storage = get_s3_storage(s3) if s3 else None

        if metrics:
            instrument_app(app, metrics)

        cls.__instance__ = cls(
            fastapi_app=app,
            mongo_storage=mongo_storage,
            s3_storage=s3_storage,
        )


def get_mvp() -> Mvp:
    if Mvp.__instance__ is None:
        err = "MVP is not set up, call Mvp.setup() after FastAPI app is initialized."
        raise RuntimeError(err)
    return Mvp.__instance__


MvpDep = Annotated[Mvp, Depends(get_mvp)]
