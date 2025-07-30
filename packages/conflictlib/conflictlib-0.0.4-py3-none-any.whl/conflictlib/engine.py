from typing import List, Optional, Dict, Any


class ConflictReport:
    def __init__(
        self,
        conflict: bool,
        rule: Optional[str] = None,
        conflicting_ids: Optional[List[str]] = None,
        dimensions: Optional[List[str]] = None,
        message: str = ""
    ):
        self.conflict = conflict
        self.rule = rule
        self.conflicting_ids = conflicting_ids or []
        self.dimensions = dimensions or []
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict": self.conflict,
            "rule": self.rule,
            "conflicting_allocation_ids": self.conflicting_ids,
            "dimensions": self.dimensions,
            "message": self.message,
        }


class ConflictEngine:
    def __init__(self, rules):
        self.rules = rules

    def check_conflict(self, new, existing) -> ConflictReport:
        rule = self.rules[0]
        rule_type = rule["type"]
        dims = rule.get("dimensions", [])

        if rule_type == "exact_match":
            conflicting = []
            for alloc in existing:
                if all(new["dimensions"].get(dim) == alloc["dimensions"].get(dim) for dim in dims):
                    conflicting.append(alloc["resource_id"])

            if conflicting:
                return ConflictReport(
                    conflict=True,
                    rule=rule_type,
                    conflicting_ids=conflicting,
                    dimensions=dims,
                    message=f"Conflict on dimensions {dims} with resources: {conflicting}"
                )

        return ConflictReport(conflict=False, rule=rule_type)
