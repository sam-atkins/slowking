from src.domain.events import EventChannelEnum


def test_get_event_channels():
    events = EventChannelEnum.get_event_channels()
    assert events == ["benchmark_created", "project_created"]
