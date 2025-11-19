"""Price value object - alias for Money"""
from app.domain.value_objects.money import Money


class Price(Money):
    """Price value object - extends Money for semantic clarity"""
    pass

