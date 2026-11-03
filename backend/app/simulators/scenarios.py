
from uuid import UUID

from app.schemas.incident import (
    IncidentCreate,
    IncidentScenario,
    IncidentSeverity,
)
from app.schemas.log import IncidentLog
from app.schemas.metric import IncidentMetric
from app.simulators.auth_simulator import generate_auth_failure_logs
from app.simulators.cache_simulator import (
    generate_cache_outage_logs,
    generate_cache_outage_metrics,
)
from app.simulators.database_simulator import (
    generate_database_pool_logs,
    generate_database_pool_metrics,
)
from app.simulators.metrics_simulator import (
    generate_auth_failure_metrics,
)


_LOG_GENERATORS = {
    IncidentScenario.AUTH_FAILURE: generate_auth_failure_logs,
    IncidentScenario.DATABASE_POOL_EXHAUSTION: generate_database_pool_logs,
    IncidentScenario.CACHE_OUTAGE: generate_cache_outage_logs,
}

_METRIC_GENERATORS = {
    IncidentScenario.AUTH_FAILURE: generate_auth_failure_metrics,
    IncidentScenario.DATABASE_POOL_EXHAUSTION: generate_database_pool_metrics,
    IncidentScenario.CACHE_OUTAGE: generate_cache_outage_metrics,
}


SAMPLE_INCIDENTS = {
    IncidentScenario.AUTH_FAILURE: IncidentCreate(
        title="Authentication service failure",
        description="Users receive 401 errors after deployment",
        severity=IncidentSeverity.HIGH,
        scenario=IncidentScenario.AUTH_FAILURE,
    ),
    IncidentScenario.DATABASE_POOL_EXHAUSTION: IncidentCreate(
        title="Order API timing out",
        description="Checkout requests fail with 504 errors",
        severity=IncidentSeverity.CRITICAL,
        scenario=IncidentScenario.DATABASE_POOL_EXHAUSTION,
    ),
    IncidentScenario.CACHE_OUTAGE: IncidentCreate(
        title="Product catalog is slow",
        description="Catalog pages take several seconds to load",
        severity=IncidentSeverity.MEDIUM,
        scenario=IncidentScenario.CACHE_OUTAGE,
    ),
}


def generate_logs(
    scenario: IncidentScenario,
    incident_id: UUID,
) -> list[IncidentLog]:
    return _LOG_GENERATORS[scenario](incident_id)


def generate_metrics(
    scenario: IncidentScenario,
    incident_id: UUID,
) -> list[IncidentMetric]:
    return _METRIC_GENERATORS[scenario](incident_id)
