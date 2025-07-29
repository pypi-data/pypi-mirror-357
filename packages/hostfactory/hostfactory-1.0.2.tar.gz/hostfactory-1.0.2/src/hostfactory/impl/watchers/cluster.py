"""Top level cluster watcher"""

import logging
import pathlib

from hostfactory import fsutils

logger = logging.getLogger(__name__)


def handle_event(
    workdir: pathlib.Path, _postprocess_event, _event_path, event: dict
) -> None:
    """Update the event status in the events directory."""
    data = event["object"]
    event_type = event["type"]

    if data.kind == "Event":
        involved_object = data.involved_object
        if not involved_object.name:
            logger.warning(
                "Missing Involved object name. Skipping event %s.",
                data.metadata.name,
            )
            return
        logger.info(
            "Event: %s %s %s %s",
            event_type,
            data.metadata.name,
            involved_object.kind,
            involved_object.name,
        )
    else:
        logger.info("Event: %s %s %s", event_type, data.kind, data.metadata.name)

    if event_type == "ERROR":
        logger.error("An error was encountered in the events: %s", data)
        return
    event_path = _event_path(workdir, data)

    if event_path:
        if event_type in ("ADDED", "MODIFIED"):
            fsutils.atomic_write(data, event_path)
        elif event_type == "DELETED":
            event_path.unlink(missing_ok=True)
        else:
            logger.warning(
                "Unknown event type: %s. Skipping event %s.",
                event_type,
                data.metadata.name,
            )
            return

    _postprocess_event(workdir, event)
