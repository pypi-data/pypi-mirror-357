from rule_engine import Context, Rule

from conflictlib.functions.builtins import Unique, GetDuplicates, UniqueForSet


class DeconflictionContext(Context):
    def resolve(self, thing, name, scope=None):
        if name == "__root__":
            return thing
        # Remove this hardcode once a method for dynamic function discovery is implemented
        custom_functions = [Unique(), GetDuplicates(), UniqueForSet()]
        for function in custom_functions:
            if name == function.name:
                return function

        return super().resolve(thing, name, scope)


class DeconflictionRule(Rule):
    def __init__(self, text, *args, **kwargs):
        context = DeconflictionContext(*args, **kwargs)
        super().__init__(text, context)
