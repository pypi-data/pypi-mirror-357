from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BodyCreateAccessTokenV0AccesstokenCreatePost")


@_attrs_define
class BodyCreateAccessTokenV0AccesstokenCreatePost:
    """
    Attributes:
        path (str): Path within the user space
        access_mode (str): Any of 'read' or 'write'
        recursive (bool): Whether the access token is recursive
        expires (int): Expiration time in seconds since epoch (UNIX time)
        idem_key (Union[Unset, str]): Idempotency key used to avoid creating multiple keys by accident
    """

    path: str
    access_mode: str
    recursive: bool
    expires: int
    idem_key: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        access_mode = self.access_mode

        recursive = self.recursive

        expires = self.expires

        idem_key = self.idem_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "access_mode": access_mode,
                "recursive": recursive,
                "expires": expires,
            }
        )
        if idem_key is not UNSET:
            field_dict["idem_key"] = idem_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        path = d.pop("path")

        access_mode = d.pop("access_mode")

        recursive = d.pop("recursive")

        expires = d.pop("expires")

        idem_key = d.pop("idem_key", UNSET)

        body_create_access_token_v0_accesstoken_create_post = cls(
            path=path,
            access_mode=access_mode,
            recursive=recursive,
            expires=expires,
            idem_key=idem_key,
        )

        body_create_access_token_v0_accesstoken_create_post.additional_properties = d
        return body_create_access_token_v0_accesstoken_create_post

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
