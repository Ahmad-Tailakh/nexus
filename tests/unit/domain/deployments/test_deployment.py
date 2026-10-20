from datetime import timezone
from uuid import UUID

import pytest

from nexus.domain.deployments.deployment import Deployment
from nexus.domain.deployments.exceptions import (
    InvalidDeploymentServiceIdError,
    InvalidDeploymentTransitionError,
)


def test_deployment_can_be_created_with_valid_service_id():
    # Business rule:
    # A Deployment must belong to a valid Service.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    assert deployment.service_id == service_id


def test_deployment_generates_uuid_automatically():
    # Business rule:
    # Every Deployment must receive its own identity automatically.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    assert isinstance(deployment.id, UUID)


def test_two_deployments_receive_different_uuids():
    # Business rule:
    # Separate Deployments must have distinct identities.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment1 = Deployment(service_id=service_id)
    deployment2 = Deployment(service_id=service_id)

    assert deployment1.id != deployment2.id


def test_deployment_rejects_invalid_service_id():
    # Business rule:
    # A Deployment must reference a valid Service identity.
    with pytest.raises(InvalidDeploymentServiceIdError):
        Deployment(
            service_id="not-a-uuid",
        )


def test_deployment_initial_status_is_pending():
    # Business rule:
    # Every new Deployment starts in the PENDING state.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    assert deployment.status.value == "pending"


def test_deployment_created_at_is_timezone_aware_utc():
    # Business rule:
    # Deployment creation timestamps must unambiguously represent UTC.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    assert deployment.created_at.tzinfo == timezone.utc


def test_deployment_updated_at_is_timezone_aware_utc():
    # Business rule:
    # Deployment update timestamps must unambiguously represent UTC.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    assert deployment.updated_at.tzinfo == timezone.utc


def test_new_deployment_created_at_equals_updated_at():
    # Business rule:
    # A newly created Deployment has not been updated yet.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    assert deployment.created_at == deployment.updated_at


def test_pending_deployment_can_be_started():
    # Business rule:
    # A PENDING Deployment can transition to RUNNING.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    deployment.start()

    assert deployment.status.value == "running"


def test_running_deployment_can_succeed():
    # Business rule:
    # A RUNNING Deployment can transition to SUCCEEDED.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    deployment.start()
    deployment.succeed()

    assert deployment.status.value == "succeeded"


def test_running_deployment_can_fail():
    # Business rule:
    # A RUNNING Deployment can transition to FAILED.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    deployment.start()
    deployment.fail()

    assert deployment.status.value == "failed"


def test_failed_deployment_can_be_retried():
    # Business rule:
    # A FAILED Deployment can be retried and returns to PENDING.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    deployment.start()
    deployment.fail()
    deployment.retry()

    assert deployment.status.value == "pending"


def test_pending_deployment_cannot_succeed():
    # Business rule:
    # A PENDING Deployment cannot skip the RUNNING state.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    with pytest.raises(InvalidDeploymentTransitionError):
        deployment.succeed()

    assert deployment.status.value == "pending"


def test_pending_deployment_cannot_fail():
    # Business rule:
    # A PENDING Deployment cannot transition directly to FAILED.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    with pytest.raises(InvalidDeploymentTransitionError):
        deployment.fail()

    assert deployment.status.value == "pending"


def test_running_deployment_cannot_be_started_again():
    # Business rule:
    # A RUNNING Deployment cannot be started twice.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    deployment.start()

    with pytest.raises(InvalidDeploymentTransitionError):
        deployment.start()

    assert deployment.status.value == "running"


def test_succeeded_deployment_cannot_be_started():
    # Business rule:
    # A completed Deployment cannot be started again.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    deployment.start()
    deployment.succeed()

    with pytest.raises(InvalidDeploymentTransitionError):
        deployment.start()

    assert deployment.status.value == "succeeded"


def test_succeeded_deployment_cannot_fail():
    # Business rule:
    # A successful Deployment cannot transition to FAILED.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    deployment.start()
    deployment.succeed()

    with pytest.raises(InvalidDeploymentTransitionError):
        deployment.fail()

    assert deployment.status.value == "succeeded"


def test_succeeded_deployment_cannot_be_retried():
    # Business rule:
    # Only failed Deployments can be retried.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    deployment.start()
    deployment.succeed()

    with pytest.raises(InvalidDeploymentTransitionError):
        deployment.retry()

    assert deployment.status.value == "succeeded"


def test_failed_deployment_cannot_succeed_directly():
    # Business rule:
    # A FAILED Deployment must be retried before it can run again.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    deployment.start()
    deployment.fail()

    with pytest.raises(InvalidDeploymentTransitionError):
        deployment.succeed()

    assert deployment.status.value == "failed"


def test_failed_transition_does_not_modify_deployment():
    # Business rule:
    # A failed state transition must leave the Deployment unchanged.
    service_id = UUID("12345678-1234-5678-1234-567812345678")

    deployment = Deployment(
        service_id=service_id,
    )

    with pytest.raises(InvalidDeploymentTransitionError):
        deployment.succeed()

    assert deployment.status.value == "pending"

def test_start_updates_timestamp():
    deployment = Deployment(
        service_id=UUID("12345678-1234-5678-1234-567812345678"),
    )
    previous_updated_at = deployment.updated_at

    deployment.start()

    assert deployment.updated_at >= previous_updated_at


def test_succeed_updates_timestamp():
    deployment = Deployment(
        service_id=UUID("12345678-1234-5678-1234-567812345678"),
    )
    deployment.start()
    previous_updated_at = deployment.updated_at

    deployment.succeed()

    assert deployment.updated_at >= previous_updated_at


def test_fail_updates_timestamp():
    deployment = Deployment(
        service_id=UUID("12345678-1234-5678-1234-567812345678"),
    )
    deployment.start()
    previous_updated_at = deployment.updated_at

    deployment.fail()

    assert deployment.updated_at >= previous_updated_at


def test_retry_updates_timestamp():
    deployment = Deployment(
        service_id=UUID("12345678-1234-5678-1234-567812345678"),
    )
    deployment.start()
    deployment.fail()
    previous_updated_at = deployment.updated_at

    deployment.retry()

    assert deployment.updated_at >= previous_updated_at