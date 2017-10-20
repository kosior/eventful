from events.apps import EventsConfig


def test_app_name():
    assert EventsConfig.name == 'events'
