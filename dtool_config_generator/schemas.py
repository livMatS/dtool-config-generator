from marshmallow import Schema
from marshmallow.fields import (
    String,
    UUID,
    Dict,
    List,
    Boolean,
    Integer,
    Nested,
    Float
)


class TestResponseSchema(Schema):
    test_response = String()