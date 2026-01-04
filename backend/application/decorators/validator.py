from pydantic import validate_call, ConfigDict


pydantic_config = ConfigDict(arbitrary_types_allowed=True)

def validate_types(f):
    return validate_call(config=pydantic_config)(f)