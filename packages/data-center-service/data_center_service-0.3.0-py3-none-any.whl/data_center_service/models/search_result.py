from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.search_result_metadata import SearchResultMetadata


T = TypeVar("T", bound="SearchResult")


@_attrs_define
class SearchResult:
    text: str
    metadata: "SearchResultMetadata"
    id: Union[None, str]
    score: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        text = self.text

        metadata = self.metadata.to_dict()

        id: Union[None, str]
        id = self.id

        score = self.score

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "text": text,
                "metadata": metadata,
                "id": id,
                "score": score,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_result_metadata import SearchResultMetadata

        d = dict(src_dict)
        text = d.pop("text")

        metadata = SearchResultMetadata.from_dict(d.pop("metadata"))

        def _parse_id(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        id = _parse_id(d.pop("id"))

        score = d.pop("score")

        search_result = cls(
            text=text,
            metadata=metadata,
            id=id,
            score=score,
        )

        search_result.additional_properties = d
        return search_result

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
