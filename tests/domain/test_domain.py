from slowking.domain.commands import CommandChannelEnum
from slowking.domain.events import EventChannelEnum


def test_get_event_channels():
    events = EventChannelEnum.get_event_channels()
    assert events == ["benchmark_created", "project_created"]


def test_get_command_channels():
    commands = CommandChannelEnum.get_command_channels()
    assert commands == ["create_benchmark"]
