from enum import Enum
from giturlparse import parse
from typing import List, Optional
from pydantic import BaseModel, model_validator

from osvutils.types.event import Event, event_mapping, Fixed, LastAffected


class RangeType(str, Enum):
    GIT = 'GIT'
    SEMVER = 'SEMVER'
    ECOSYSTEM = 'ECOSYSTEM'


# Range model with all properties and conditional validation
class Range(BaseModel):
    type: RangeType
    events: List[Event]
    database_specific: Optional[dict] = None  # TODO: to be extended for each database

    @model_validator(mode='before')
    def validate_events(cls, values):
        events = values.get('events', [])

        if not any(events):
            raise ValueError("At least one of 'introduced', 'fixed', 'last_affected', or 'limit' must be provided")

        processed_events = []

        # Ensure that the type matches the expected event types
        for event in events:
            if len(event) != 1:
                raise ValueError("Only one event type is allowed per event object")

            for event_type, version in event.items():
                if event_type not in event_mapping:
                    raise ValueError(f"Invalid event type: {event_type}")

                processed_events.append(event_mapping[event_type](version=version))

        # Replace the original 'events' data with the processed list of objects
        values['events'] = processed_events

        return values

    def get_fixed_events(self) -> List[Fixed]:
        return [e for e in self.events if isinstance(e, Fixed)]


class GitRepo(BaseModel):
    owner: str
    name: str

    def __str__(self):
        return f"{self.owner}/{self.name}"


class GitRange(Range):
    repo: GitRepo

    # Conditional logic for GIT type requiring repo
    @model_validator(mode='before')
    def validate_git_repo(cls, values):
        if values.get('type') == 'GIT':
            if not values.get('repo'):
                raise ValueError("GIT ranges require a 'repo' field.")

            # Parse the repo and check validity
            parsed_repo = parse(values['repo'])

            if not parsed_repo.valid:
                raise ValueError(f"Invalid repository url: {values['repo']}")

            # Replace the original 'repo' data with the parsed object
            values['repo'] = GitRepo(owner=parsed_repo.owner, name=parsed_repo.repo)

        return values

    # TODO: the schema indicates that 'fixed' and 'last_affected' are required and mutually exclusive but some entries
    #  do not follow this rule. Uncomment the following code to enforce this rule.
    # @model_validator(mode='after')
    # def validate_git_events(cls, values):
    #     # Check if both 'fixed' and 'last_affected' are present
    #     fixed_events = [e for e in values.events if isinstance(e, Fixed)]
    #     last_affected_events = [e for e in values.events if isinstance(e, LastAffected)]
    #
    #     # Check for mutual exclusivity
    #     if fixed_events and last_affected_events:
    #         raise ValueError("'fixed' and 'last_affected' events must have different versions.")
    #
    #     # At least one of 'fixed' or 'last_affected' must be present
    #     if not fixed_events and not last_affected_events:
    #         raise ValueError("Either 'fixed' or 'last_affected' event is required.")
    #
    #     return values
