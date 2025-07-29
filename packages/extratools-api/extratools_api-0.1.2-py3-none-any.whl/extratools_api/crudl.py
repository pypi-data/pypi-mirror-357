import json
from collections.abc import Awaitable, Callable, Iterable, Mapping, MutableMapping
from http import HTTPStatus
from typing import Annotated, Any, cast

from extratools_core.crudl import CRUDLWrapper, RLWrapper
from extratools_core.json import JsonDict
from extratools_core.str import wildcard_match
from extratools_core.typing import SearchableMapping
from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, ValidationError


def add_crudl_endpoints[KT: str, VT: JsonDict | BaseModel](
    app: FastAPI,
    path_prefix: str,
    *,
    create_func: Callable[[KT, JsonDict], Awaitable[VT | None]] | None = None,
    read_func: Callable[[KT], Awaitable[VT]] | None = None,
    update_func: Callable[[KT, JsonDict], Awaitable[VT | None]] | None = None,
    delete_func: Callable[[KT], Awaitable[VT | None]] | None = None,
    list_func: Callable[[JsonDict | None], Awaitable[Iterable[tuple[KT, Any]]]] | None = None,
) -> None:
    path_prefix = path_prefix.rstrip("/")

    if create_func:
        @app.put(path_prefix + "/{identifier}")
        async def create_endpoint(
            identifier: KT,
            put_body: Annotated[JsonDict, Body()],
        ) -> VT | None:
            return await create_func(
                identifier,
                put_body,
            )

    if read_func:
        @app.get(path_prefix + "/{identifier}")
        async def read_endpoint(identifier: KT) -> VT:
            return await read_func(
                identifier,
            )

    if update_func:
        @app.patch(path_prefix + "/{identifier}")
        async def update_endpoint(
            identifier: KT,
            patch_body: Annotated[JsonDict, Body()],
        ) -> VT | None:
            return await update_func(
                identifier,
                patch_body,
            )

    if delete_func:
        @app.delete(path_prefix + "/{identifier}")
        async def delete_endpoint(identifier: KT) -> VT | None:
            return await delete_func(identifier)

    if list_func:
        @app.get(path_prefix + "/")
        async def list_endpoint(filter_body: str | None = None) -> dict[KT, Any]:
            try:
                return dict(await list_func(
                    json.loads(filter_body) if filter_body
                    else None,
                ))
            except json.JSONDecodeError as e:
                raise HTTPException(HTTPStatus.BAD_REQUEST) from e


class FilterBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: Any = None

    includes: list[str] | None = None
    excludes: list[str] | None = None

    def match(self, key: str) -> bool:
        return wildcard_match(key, includes=self.includes, excludes=self.excludes)


def add_crudl_endpoints_for_mapping[KT: str, VT: JsonDict](
    app: FastAPI,
    path_prefix: str,
    mapping: Mapping[KT, VT],
    *,
    values_in_list: bool = False,
    readonly: bool | None = None,
) -> None:
    mutable: bool = isinstance(mapping, MutableMapping)
    if readonly is None:
        readonly = not mutable

    async def read_func(key: KT) -> VT:
        try:
            return crudl_store.read(key)
        except KeyError as e:
            raise HTTPException(HTTPStatus.NOT_FOUND) from e

    async def list_func(filter_body: JsonDict | None) -> Iterable[tuple[KT, VT | None]]:
        try:
            filter_body_model: FilterBody | None = (
                FilterBody.model_validate(filter_body, strict=True) if filter_body
                else None
            )
        except ValidationError as e:
            raise HTTPException(HTTPStatus.BAD_REQUEST) from e

        if (
            filter_body_model
            and filter_body_model.query is not None
            and not isinstance(mapping, SearchableMapping)
        ):
            raise HTTPException(HTTPStatus.BAD_REQUEST)

        return crudl_store.list(
            None if filter_body_model is None
            else (
                filter_body_model.query if isinstance(mapping, SearchableMapping) else None,
                filter_body_model.match,
            ),
        )

    if mutable and not readonly:
        crudl_store = CRUDLWrapper[KT, VT](
            mapping,
            values_in_list=values_in_list,
        )

        async def create_func(key: KT, value: JsonDict) -> None:
            try:
                crudl_store.create(key, cast("VT", value))
            except KeyError as e:
                raise HTTPException(HTTPStatus.CONFLICT) from e

        async def update_func(key: KT, value: JsonDict) -> None:
            try:
                crudl_store.update(key, cast("VT", value))
            except KeyError as e:
                raise HTTPException(HTTPStatus.NOT_FOUND) from e

        async def delete_func(key: KT) -> None:
            try:
                crudl_store.delete(key)
            except KeyError as e:
                raise HTTPException(HTTPStatus.NOT_FOUND) from e

        add_crudl_endpoints(
            app,
            path_prefix,
            read_func=read_func,
            list_func=list_func,
            create_func=create_func,
            update_func=update_func,
            delete_func=delete_func,
        )
    else:
        crudl_store = RLWrapper[KT, VT](
            mapping,
            values_in_list=values_in_list,
        )

        add_crudl_endpoints(
            app,
            path_prefix,
            read_func=read_func,
            list_func=list_func,
        )
