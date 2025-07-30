from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.body_delete_access_token_v0_accesstoken_delete_post import BodyDeleteAccessTokenV0AccesstokenDeletePost
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: BodyDeleteAccessTokenV0AccesstokenDeletePost,
    authorization: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v0/accesstoken.delete",
    }

    _kwargs["data"] = body.to_dict()

    headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = response.json()
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
) -> Response[Union[Any, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BodyDeleteAccessTokenV0AccesstokenDeletePost,
    authorization: Union[Unset, str] = UNSET,
) -> Response[Union[Any, HTTPValidationError]]:
    """Delete Access Token

     Delete an accesstoken.

    **Example**:
    ```
    POST <api_prefix>/accesstoken.delete HTTP/1.1
    Host: <zebrastream_host>
    Content-Type: application/x-www-form-urlencoded
    Authorization: Bearer <management_api_key>

    token_id=123456789012
    ```

    Args:
        authorization (Union[Unset, str]): Bearer style authorization header
        body (BodyDeleteAccessTokenV0AccesstokenDeletePost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BodyDeleteAccessTokenV0AccesstokenDeletePost,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Delete Access Token

     Delete an accesstoken.

    **Example**:
    ```
    POST <api_prefix>/accesstoken.delete HTTP/1.1
    Host: <zebrastream_host>
    Content-Type: application/x-www-form-urlencoded
    Authorization: Bearer <management_api_key>

    token_id=123456789012
    ```

    Args:
        authorization (Union[Unset, str]): Bearer style authorization header
        body (BodyDeleteAccessTokenV0AccesstokenDeletePost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BodyDeleteAccessTokenV0AccesstokenDeletePost,
    authorization: Union[Unset, str] = UNSET,
) -> Response[Union[Any, HTTPValidationError]]:
    """Delete Access Token

     Delete an accesstoken.

    **Example**:
    ```
    POST <api_prefix>/accesstoken.delete HTTP/1.1
    Host: <zebrastream_host>
    Content-Type: application/x-www-form-urlencoded
    Authorization: Bearer <management_api_key>

    token_id=123456789012
    ```

    Args:
        authorization (Union[Unset, str]): Bearer style authorization header
        body (BodyDeleteAccessTokenV0AccesstokenDeletePost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BodyDeleteAccessTokenV0AccesstokenDeletePost,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Delete Access Token

     Delete an accesstoken.

    **Example**:
    ```
    POST <api_prefix>/accesstoken.delete HTTP/1.1
    Host: <zebrastream_host>
    Content-Type: application/x-www-form-urlencoded
    Authorization: Bearer <management_api_key>

    token_id=123456789012
    ```

    Args:
        authorization (Union[Unset, str]): Bearer style authorization header
        body (BodyDeleteAccessTokenV0AccesstokenDeletePost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
        )
    ).parsed
