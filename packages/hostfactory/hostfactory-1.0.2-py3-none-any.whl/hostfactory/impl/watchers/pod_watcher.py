"""Watch pods"""

import json
import logging
import pathlib

from hostfactory import events as hfevents
from hostfactory import fsutils
from hostfactory import k8sutils
from hostfactory.impl.watchers import cluster

_HF_K8S_LABEL_KEY = "symphony/hostfactory-reqid"

logger = logging.getLogger(__name__)


def watch(workdir: pathlib.Path) -> None:
    """Watch the status of pod associated with the hostfactory requests."""
    k8sutils.watch_pods(
        workdir=workdir,
        _postprocess_event=_postprocess_event,
        _event_path=_event_path,
        label_selector=_HF_K8S_LABEL_KEY,
        handler=cluster.handle_event,
        namespace=k8sutils.get_namespace(),
    )


def _event_path(workdir: pathlib.Path, data: dict) -> pathlib.Path:
    """If None is returned, event should not be saved"""
    return workdir / "pods" / data.metadata.name


def _find_node_id(workdir: pathlib.Path, node_name) -> str | None:
    """If available, grab stored node id"""
    node_path = workdir / "nodes" / node_name
    try:
        node_obj = json.loads(node_path.read_text())
        return node_obj["metadata"]["uid"]
    except FileNotFoundError:
        logger.info("Unknown node at: %s", node_path)
        return None


def _postprocess_event(workdir: pathlib.Path, event: dict) -> None:
    """Push pod event to db."""
    logger.debug("Processing pod event %s in workdir %s", event, workdir)
    event_type = event["type"]
    pod_id = event["object"].metadata.name

    if event_type == "DELETED":
        # If the pod is deleted, we need to update the symlink
        logger.info("Deleted pod %s marking it in the pods-status", pod_id)
        fsutils.atomic_symlink("deleted", workdir / "pods-status" / pod_id)
    else:
        current_pod_status = fsutils.fetch_pod_status(workdir, pod_id)
        event_pod_status = event["object"].status.phase.lower()

        if current_pod_status != "deleted":
            logger.debug(
                "Pod %s status changed from %s to %s",
                pod_id,
                current_pod_status,
                event_pod_status,
            )
            fsutils.atomic_symlink(event_pod_status, workdir / "pods-status" / pod_id)

    # We now publish the events to track it in the database
    _track_pod_event(workdir, event)


def _track_pod_event(workdir, event: dict) -> None:
    """Track events happening to a pod"""
    pod_id = event["object"].metadata.name
    with hfevents.EventsBuffer() as events:
        events.post(
            category="pod",
            id=pod_id,
            event=event,
        )

        events.post(
            category="pod",
            id=pod_id,
            status=event["object"].status.phase.lower(),
        )

        if event["object"].metadata.creation_timestamp:
            events.post(
                category="pod",
                id=pod_id,
                status="created",
            )

        if event["object"].metadata.deletion_timestamp:
            events.post(
                category="pod",
                id=pod_id,
                status="deleted",
            )

        if event["object"].spec.node_name:
            node_id = _find_node_id(workdir, event["object"].spec.node_name)
            events.post(
                category="pod",
                id=pod_id,
                node_name=str(event["object"].spec.node_name),
                node_id=node_id,
            )

        for condition in event["object"].status.conditions or ():
            if condition.type == "PodScheduled" and condition.status == "True":
                events.post(
                    category="pod",
                    id=pod_id,
                    status="scheduled",
                )
            if condition.type == "Ready" and condition.status == "True":
                events.post(
                    category="pod",
                    id=pod_id,
                    status="ready",
                )
            if condition.type == "DisruptionTarget":
                events.post(
                    category="pod",
                    id=pod_id,
                    status="disrupted",
                    disrupted_reason=str(condition.reason),
                    disrupted_message=str(condition.message),
                )

        pod_cpu_core_request, pod_cpu_core_limit = k8sutils.get_total_pod_cpu(
            event["object"]
        )
        pod_memory_mib_request, pod_memory_mib_limit = k8sutils.get_total_pod_memory(
            event["object"]
        )

        events.post(
            category="pod",
            id=pod_id,
            cpu_requested=str(pod_cpu_core_request),
            cpu_limit=str(pod_cpu_core_limit),
            memory_requested=str(pod_memory_mib_request),
            memory_limit=str(pod_memory_mib_limit),
        )

        container_statuses = k8sutils.get_pod_container_statuses(event["object"])
        if container_statuses:
            events.post(
                category="pod",
                id=pod_id,
                container_statuses=json.dumps(container_statuses),
            )
