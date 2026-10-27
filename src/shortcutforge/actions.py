"""Explicitly supported action schemas; unknown identifiers fail closed.

Parameter keys and defaults are based on exported workflows and the linked
action references in ``docs/named-actions.md``. These schemas do not promise
that an action is available on every iOS release.
"""

CATALOG = {
    "text": {
        "identifier": "is.workflow.actions.gettext",
        "parameters": {"text": "WFTextActionText"},
        "required": ("text",),
        "value_types": {"text": "string"},
        "output": True,
    },
    "current_date": {
        "identifier": "is.workflow.actions.date",
        "parameters": {"mode": "WFDateActionMode"},
        "defaults": {"mode": "Current Date"},
        "value_types": {"mode": "string"},
        "output": True,
    },
    "notify": {
        "identifier": "is.workflow.actions.notification",
        "parameters": {"text": "WFNotificationActionBody"},
        "required": ("text",),
        "value_types": {"text": "string"},
        "output": False,
    },
    "speak": {
        "identifier": "is.workflow.actions.speaktext",
        "parameters": {"text": "WFSpeakTextText"},
        "required": ("text",),
        "value_types": {"text": "string"},
        "output": False,
    },
    "open_url": {
        "identifier": "is.workflow.actions.openurl",
        "parameters": {"url": "WFURLActionURL"},
        "required": ("url",),
        "value_types": {"url": "string"},
        "output": False,
    },
    "ask_for_input": {
        "identifier": "is.workflow.actions.ask",
        "parameters": {
            "prompt": "WFAskActionPrompt",
            "input_type": "WFInputType",
            "default_answer": "WFAskActionDefaultAnswer",
            "default_date": "WFAskActionDefaultAnswerDate",
            "granularity": "WFAskActionDateGranularity",
        },
        "required": ("prompt",),
        "defaults": {"input_type": "Text"},
        "value_types": {
            "prompt": "string",
            "input_type": "string",
            "default_answer": "string",
            "default_date": "string",
            "granularity": "string",
        },
        "choices": {
            "input_type": ("Text", "Number", "URL", "Date"),
            "granularity": ("Date", "Time", "Date and Time"),
        },
        "conditional_forbidden": {
            "default_answer": ("input_type", ("Date",)),
            "default_date": ("input_type", ("Text", "Number", "URL")),
            "granularity": ("input_type", ("Text", "Number", "URL")),
        },
        "output": True,
    },
    "get_clipboard": {
        "identifier": "is.workflow.actions.getclipboard",
        "parameters": {},
        "output": True,
    },
    "set_clipboard": {
        "identifier": "is.workflow.actions.setclipboard",
        "parameters": {"input": "WFInput"},
        "required": ("input",),
        "references_only": ("input",),
        "reference_types": {"input": "WFTextTokenAttachment"},
        "output": False,
    },
    "get_current_location": {
        "identifier": "is.workflow.actions.getcurrentlocation",
        "parameters": {},
        "output": True,
    },
    "get_device_details": {
        "identifier": "is.workflow.actions.getdevicedetails",
        "parameters": {"detail": "WFDeviceDetail"},
        "defaults": {"detail": "Device Name"},
        "choices": {
            "detail": (
                "Device Name",
                "Device Model",
                "System Version",
                "Screen Width",
                "Screen Height",
                "Current Volume",
                "Current Brightness",
            ),
        },
        "value_types": {"detail": "string"},
        "output": True,
    },
    "get_upcoming_events": {
        "identifier": "is.workflow.actions.getupcomingevents",
        "parameters": {
            "calendar": "WFGetUpcomingItemCalendar",
            "count": "WFGetUpcomingItemCount",
            "day": "WFDateSpecifier",
            "specified_day": "WFSpecifiedDate",
        },
        "required": (),
        "defaults": {"count": 1, "day": "Any Day"},
        "conditional_required": {"specified_day": ("day", "Specified Day")},
        "choices": {
            "day": ("Any Day", "Today", "Tomorrow", "Specified Day"),
        },
        "value_types": {
            "calendar": "string",
            "count": "integer",
            "day": "string",
            "specified_day": "string",
        },
        "output": True,
    },
    "get_upcoming_reminders": {
        "identifier": "is.workflow.actions.getupcomingreminders",
        "parameters": {
            "list": "WFGetUpcomingItemCalendar",
            "count": "WFGetUpcomingItemCount",
        },
        "required": (),
        "defaults": {"count": 1},
        "value_types": {"list": "string", "count": "integer"},
        "output": True,
    },
    "get_current_ip_address": {
        "identifier": "is.workflow.actions.getipaddress",
        "parameters": {
            "address": "WFIPAddressSourceOption",
            "type": "WFIPAddressTypeOption",
        },
        "required": (),
        "defaults": {"address": "External", "type": "IPv4"},
        "choices": {
            "address": ("External", "Local"),
            "type": ("IPv4", "IPv6"),
        },
        "output": True,
    },
    "get_latest_photos": {
        "identifier": "is.workflow.actions.getlastphoto",
        "parameters": {
            "count": "WFGetLatestPhotoCount",
            "include_screenshots": "WFGetLatestPhotosActionIncludeScreenshots",
        },
        "required": (),
        "defaults": {"count": 1, "include_screenshots": True},
        "value_types": {"count": "integer", "include_screenshots": "boolean"},
        "output": True,
    },
    "get_contents_of_url": {
        "identifier": "is.workflow.actions.downloadurl",
        "parameters": {"url": "WFURL"},
        "required": ("url",),
        "value_types": {"url": "string"},
        "output": True,
    },
    "show_result": {
        "identifier": "is.workflow.actions.showresult",
        "parameters": {"text": "Text"},
        "required": ("text",),
        "value_types": {"text": "string"},
        "output": False,
    },
    "save_to_photos": {
        "identifier": "is.workflow.actions.savetocameraroll",
        "parameters": {"input": "WFInput"},
        "required": ("input",),
        "references_only": ("input",),
        "reference_types": {"input": "WFTextTokenAttachment"},
        "output": True,
    },
    "get_battery_level": {
        "identifier": "is.workflow.actions.getbatterylevel",
        "parameters": {},
        "output": True,
    },
    "delay": {
        "identifier": "is.workflow.actions.delay",
        "parameters": {"seconds": "WFDelayTime"},
        "defaults": {"seconds": 1},
        "value_types": {"seconds": "number"},
        "output": False,
    },
}


def _load_sourced_actions() -> dict[str, dict]:
    """Load sourced schemas that can be represented by the current compiler."""
    import json
    from importlib.resources import files

    data = json.loads(
        files("shortcutforge").joinpath("data/scpl_ios27_actions.json").read_text(
            encoding="utf-8"
        )
    )
    result: dict[str, dict] = {}
    for action in data["actions"]:
        alias = action["id"]
        if alias in CATALOG or alias in result:
            raise RuntimeError(f"duplicate generated action ID: {alias}")
        parameter_keys = [parameter["key"] for parameter in action["parameters"]]
        result[alias] = {
            "identifier": action["identifier"],
            "parameters": {key: key for key in parameter_keys},
            "required": (),
            "defaults": {
                parameter["key"]: parameter["defaultvalue"]
                for parameter in action["parameters"]
                if "defaultvalue" in parameter
            },
            "choices": {
                parameter["key"]: tuple(parameter["items"])
                for parameter in action["parameters"]
                if parameter.get("items")
                and all(isinstance(item, str) for item in parameter["items"])
            },
            "output": action["output"],
            "source_name": action["name"],
            "source_parameters": action["parameters"],
            "availability": {"27": "observed"},
        }
    return result


SOURCED_CATALOG = _load_sourced_actions()
CATALOG.update(SOURCED_CATALOG)
