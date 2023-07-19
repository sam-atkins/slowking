from slowking.domain.events import ProjectCreated


def test_event_to_dict():
    event = ProjectCreated(benchmark_id=2)
    event_dict = event.to_dict()
    assert event_dict == {"benchmark_id": 2, "channel": "project_created"}


def test_event_to_json():
    event = ProjectCreated(benchmark_id=2)
    event_json = event.to_json()
    assert event_json == '{"benchmark_id": 2, "channel": "project_created"}'
