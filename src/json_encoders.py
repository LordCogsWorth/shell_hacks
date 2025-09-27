"""JSON encoders for handling custom types."""

from decimal import Decimal
from json import JSONEncoder


class DecimalJSONEncoder(JSONEncoder):
    """Custom JSON encoder that can handle Decimal types."""

    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)  # Convert Decimal to string
        return super().default(o)