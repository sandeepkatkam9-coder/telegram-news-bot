def should_notify(event):
    """
    Return True only for important events.
    """

    if event is None:
        return False

    return event["importance"] >= 90