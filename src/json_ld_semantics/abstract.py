"""
Some needed abstraction.
"""
PROTECTED_ATTRS = ["fieldName", "data", "foundType", "parent", "children", "path"]


class Protected(type):
    """Protection for changing source data in semantics."""

    def __setattr__(cls, key, value):
        if key in PROTECTED_ATTRS:
            raise AttributeError(f"Cannot modify `{key}`.")
        else:
            return type.__setattr__(cls, key, value)

    def __delattr__(cls, key):
        if key in PROTECTED_ATTRS:
            raise AttributeError(f"Cannot delete `{key}`.")
        else:
            return type.__delattr__(cls, key)
