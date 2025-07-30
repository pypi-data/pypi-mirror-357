from typing import Optional, Any

from conflictlib.functions.base import RuleFunction


class IteratorFunction(RuleFunction):
    def _get_value(self, item: Any, attr: Optional[str] = None) -> Any:
        if attr is not None:
            try:
                value = getattr(item, attr)
            except AttributeError:
                value = item[attr]
        else:
            value = item
        return value

    def _iterate(self, data: iter, attr: Optional[str] = None):
        for item in data:
            yield item, self._get_value(item, attr)


class Unique(IteratorFunction):
    def run(self, data: iter, attr: Optional[str] = None) -> bool:
        values = set()
        for _, value in self._iterate(data, attr):
            if value in values:
                return False
            values.add(value)
        return True


class GetDuplicates(IteratorFunction):
    def run(
        self, data: iter, attr: Optional[str] = None
    ) -> list[tuple[Any, list[Any]]]:
        values_dict = {}
        for item, value in self._iterate(data, attr):
            str_value = str(value)
            if str_value not in values_dict:
                values_dict[str_value] = {"original_value": value, "items": []}
            values_dict[str_value]["items"].append(item)
        return [
            (item["original_value"], item["items"])
            for item in values_dict.values()
            if len(item["items"]) > 1
        ]


class UniqueForSet(IteratorFunction):
    def run(self, dataset: iter, new_item: Any, attr: Optional[str] = None) -> bool:
        new_obj_value = self._get_value(new_item, attr)
        for _, value in self._iterate(dataset, attr):
            if value == new_obj_value:
                return False
        return True
