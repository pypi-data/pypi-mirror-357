# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import pytest
import scipp as sc
import scippnexus as snx

from ess.loki import data
from ess.loki.live import LokiMonitorTestWorkflow
from ess.reduce.nexus.json_generator import event_data_generator
from ess.reduce.nexus.json_nexus import JSONGroup


def test_can_create_loki_monitor_workflow() -> None:
    filename = data.loki_tutorial_sample_run_60250()
    _ = LokiMonitorTestWorkflow(filename)


def _call_workflow(wf: LokiMonitorTestWorkflow, **kwargs: dict) -> sc.DataGroup:
    nxevent_data = {
        f'/entry/instrument/{k}/{k}_events': JSONGroup(v) for k, v in kwargs.items()
    }
    return sc.DataGroup(wf(nxevent_data, {}))


def test_workflow_processes_monitor_event_data_chunks() -> None:
    filename = data.loki_tutorial_sample_run_60250()
    mon1 = snx.load(filename, root='entry/instrument/monitor_1/monitor_1_events')
    mon2 = snx.load(filename, root='entry/instrument/monitor_2/monitor_2_events')
    generator1 = event_data_generator(mon1)
    generator2 = event_data_generator(mon2)
    wf = LokiMonitorTestWorkflow(filename)

    group1 = next(generator1)
    group2 = next(generator2)
    result = _call_workflow(wf, monitor_1=group1, monitor_2=group2)
    assert list(result) == ['Incident Monitor', 'Transmission Monitor']

    # If we pass the same data again, we should get the same result, there is no
    # accumulation in this workflow.
    same = _call_workflow(wf, monitor_1=group1, monitor_2=group2)
    assert sc.identical(same, result)

    group1 = next(generator1)
    group2 = next(generator2)
    different = _call_workflow(wf, monitor_1=group1, monitor_2=group2)
    assert not sc.identical(different, result)


def test_workflow_raises_if_event_data_missing() -> None:
    filename = data.loki_tutorial_sample_run_60250()
    mon1 = snx.load(filename, root='entry/instrument/monitor_1/monitor_1_events')
    mon2 = snx.load(filename, root='entry/instrument/monitor_2/monitor_2_events')
    generator1 = event_data_generator(mon1)
    generator2 = event_data_generator(mon2)
    wf = LokiMonitorTestWorkflow(filename)

    result = _call_workflow(wf, monitor_1=next(generator1), monitor_2=next(generator2))
    assert list(result) == ['Incident Monitor', 'Transmission Monitor']

    with pytest.raises(KeyError, match="monitor_1"):
        _call_workflow(wf, monitor_2=next(generator2))


def test_workflow_raises_if_event_data_not_updated() -> None:
    filename = data.loki_tutorial_sample_run_60250()
    mon1 = snx.load(filename, root='entry/instrument/monitor_1/monitor_1_events')
    mon2 = snx.load(filename, root='entry/instrument/monitor_2/monitor_2_events')
    generator1 = event_data_generator(mon1)
    generator2 = event_data_generator(mon2)
    wf = LokiMonitorTestWorkflow(filename)

    result = _call_workflow(wf, monitor_1=next(generator1), monitor_2=next(generator2))
    assert list(result) == ['Incident Monitor', 'Transmission Monitor']

    # First call will set keys in workflow...
    _call_workflow(wf, monitor_1=next(generator1), monitor_2=next(generator2))
    # ... but second call should raise instead of reusing it, since it would use same
    # events twice, which can break accumulators or other assumptions.
    with pytest.raises(KeyError, match="monitor_1"):
        _call_workflow(wf, monitor_2=next(generator2))


def test_workflow_ignores_extra_event_data() -> None:
    filename = data.loki_tutorial_sample_run_60250()
    mon1 = snx.load(filename, root='entry/instrument/monitor_1/monitor_1_events')
    mon2 = snx.load(filename, root='entry/instrument/monitor_2/monitor_2_events')
    generator1 = event_data_generator(mon1)
    generator2 = event_data_generator(mon2)
    wf = LokiMonitorTestWorkflow(filename)

    result = _call_workflow(
        wf,
        monitor_1=next(generator1),
        monitor_2=next(generator2),
        monitor_3=next(generator1),
    )
    assert list(result) == ['Incident Monitor', 'Transmission Monitor']
