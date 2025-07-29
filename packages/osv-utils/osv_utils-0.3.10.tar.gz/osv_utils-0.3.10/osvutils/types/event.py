from pydantic import BaseModel


# Event model
class Event(BaseModel):
    version: str


class Introduced(Event):
    # TODO: Implement additional properties/functionality as needed
    pass


class Fixed(Event):
    # TODO: Implement additional properties/functionality as needed
    pass


class LastAffected(Event):
    # TODO: Implement additional properties/functionality as needed
    pass


class Limit(Event):
    # TODO: Implement additional properties/functionality as needed
    pass


event_mapping = {
    'introduced': Introduced,
    'fixed': Fixed,
    'last_affected': LastAffected,
    'limit': Limit
}
