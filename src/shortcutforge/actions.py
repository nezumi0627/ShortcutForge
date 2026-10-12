"""Explicitly supported action catalog; unknown identifiers fail closed."""
CATALOG = {
    "text": {"identifier": "is.workflow.actions.gettext", "parameters": {"text": "WFTextActionText"}, "output": True},
    "current_date": {"identifier": "is.workflow.actions.currentdate", "parameters": {}, "output": True},
    "notify": {"identifier": "is.workflow.actions.notification", "parameters": {"text": "WFNotificationActionBody"}, "output": False},
    "speak": {"identifier": "is.workflow.actions.speaktext", "parameters": {"text": "WFSpeakTextText"}, "output": False},
    "open_url": {"identifier": "is.workflow.actions.openurl", "parameters": {"url": "WFURLActionURL"}, "output": False},
}
