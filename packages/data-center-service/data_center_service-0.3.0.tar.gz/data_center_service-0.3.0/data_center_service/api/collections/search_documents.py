from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.search_response import SearchResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    collection_name: str,
    *,
    query: str,
    k: Union[Unset, int] = 10,
    filter_: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["query"] = query

    params["k"] = k

    params["filter"] = filter_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/collections/{collection_name}/documents",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, SearchResponse]]:
    if response.status_code == 200:
        response_200 = SearchResponse.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[HTTPValidationError, SearchResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    collection_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    query: str,
    k: Union[Unset, int] = 10,
    filter_: Union[Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, SearchResponse]]:
    """Search Endpoint

     Search documents in a specified collection.

    Parameters:
    - **collection_name**: Optional collection name within the database
    - **query**: The search text
    - **k**: Number of results to return (default: 10)
    - **filter**: Optional filter criteria as a JSON string

    Args:
        collection_name (str):
        query (str):
        k (Union[Unset, int]):  Default: 10.
        filter_ (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SearchResponse]]
    """

    kwargs = _get_kwargs(
        collection_name=collection_name,
        query=query,
        k=k,
        filter_=filter_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collection_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    query: str,
    k: Union[Unset, int] = 10,
    filter_: Union[Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, SearchResponse]]:
    """Search Endpoint

     Search documents in a specified collection.

    Parameters:
    - **collection_name**: Optional collection name within the database
    - **query**: The search text
    - **k**: Number of results to return (default: 10)
    - **filter**: Optional filter criteria as a JSON string

    Args:
        collection_name (str):
        query (str):
        k (Union[Unset, int]):  Default: 10.
        filter_ (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SearchResponse]
    """

    return sync_detailed(
        collection_name=collection_name,
        client=client,
        query=query,
        k=k,
        filter_=filter_,
    ).parsed


async def asyncio_detailed(
    collection_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    query: str,
    k: Union[Unset, int] = 10,
    filter_: Union[Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, SearchResponse]]:
    """Search Endpoint

     Search documents in a specified collection.

    Parameters:
    - **collection_name**: Optional collection name within the database
    - **query**: The search text
    - **k**: Number of results to return (default: 10)
    - **filter**: Optional filter criteria as a JSON string

    Args:
        collection_name (str):
        query (str):
        k (Union[Unset, int]):  Default: 10.
        filter_ (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SearchResponse]]
    """

    kwargs = _get_kwargs(
        collection_name=collection_name,
        query=query,
        k=k,
        filter_=filter_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    query: str,
    k: Union[Unset, int] = 10,
    filter_: Union[Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, SearchResponse]]:
    """Search Endpoint

     Search documents in a specified collection.

    Parameters:
    - **collection_name**: Optional collection name within the database
    - **query**: The search text
    - **k**: Number of results to return (default: 10)
    - **filter**: Optional filter criteria as a JSON string

    Args:
        collection_name (str):
        query (str):
        k (Union[Unset, int]):  Default: 10.
        filter_ (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SearchResponse]
    """

    return (
        await asyncio_detailed(
            collection_name=collection_name,
            client=client,
            query=query,
            k=k,
            filter_=filter_,
        )
    ).parsed
