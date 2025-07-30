from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.add_documents_request import AddDocumentsRequest
from ...models.add_documents_response import AddDocumentsResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    collection_name: str,
    *,
    body: AddDocumentsRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/collections/{collection_name}/documents",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AddDocumentsResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = AddDocumentsResponse.from_dict(response.json())

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
) -> Response[Union[AddDocumentsResponse, HTTPValidationError]]:
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
    body: AddDocumentsRequest,
) -> Response[Union[AddDocumentsResponse, HTTPValidationError]]:
    """Add Documents Endpoint

     Add documents to a specified collection.

    - **collection_name**: Optional collection name
    - **documents**: List of documents to add

    Args:
        collection_name (str):
        body (AddDocumentsRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AddDocumentsResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        collection_name=collection_name,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collection_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AddDocumentsRequest,
) -> Optional[Union[AddDocumentsResponse, HTTPValidationError]]:
    """Add Documents Endpoint

     Add documents to a specified collection.

    - **collection_name**: Optional collection name
    - **documents**: List of documents to add

    Args:
        collection_name (str):
        body (AddDocumentsRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AddDocumentsResponse, HTTPValidationError]
    """

    return sync_detailed(
        collection_name=collection_name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    collection_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AddDocumentsRequest,
) -> Response[Union[AddDocumentsResponse, HTTPValidationError]]:
    """Add Documents Endpoint

     Add documents to a specified collection.

    - **collection_name**: Optional collection name
    - **documents**: List of documents to add

    Args:
        collection_name (str):
        body (AddDocumentsRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AddDocumentsResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        collection_name=collection_name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AddDocumentsRequest,
) -> Optional[Union[AddDocumentsResponse, HTTPValidationError]]:
    """Add Documents Endpoint

     Add documents to a specified collection.

    - **collection_name**: Optional collection name
    - **documents**: List of documents to add

    Args:
        collection_name (str):
        body (AddDocumentsRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AddDocumentsResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            collection_name=collection_name,
            client=client,
            body=body,
        )
    ).parsed
