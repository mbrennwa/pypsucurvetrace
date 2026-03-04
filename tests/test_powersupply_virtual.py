import pypsucurvetrace.powersupply as ps_mod
import pytest

from tests.virtual_drivers import VirtualPSUDriver


@pytest.mark.virtual_hw
def test_set_current_uses_current_resolution(monkeypatch):
    drv = VirtualPSUDriver(vres_set=0.1, ires_set=0.25)
    monkeypatch.setattr(ps_mod.powersupply_KORAD, "KORAD", lambda *a, **k: drv)

    psu = ps_mod.PSU(port="VIRTUAL", commandset="KORAD", label="PSU1")
    psu.setCurrent(0.37, wait_stable=False)

    assert drv.last_current == 0.25


@pytest.mark.virtual_hw
def test_set_current_wait_unstable_does_not_crash(monkeypatch):
    # Always read low current in CC mode -> never converges to target current.
    drv = VirtualPSUDriver(
        read_sequence=[(1.0, 0.0, "CC")] * 8,
        ires_read=1e-6,
        max_settle_time=0.001,
        read_idle_time=0.0,
    )
    monkeypatch.setattr(ps_mod.powersupply_KORAD, "KORAD", lambda *a, **k: drv)
    monkeypatch.setattr(ps_mod.time, "sleep", lambda *_: None)

    psu = ps_mod.PSU(port="VIRTUAL", commandset="KORAD", label="PSU1")
    psu.setCurrent(1.0, wait_stable=True)


@pytest.mark.virtual_hw
def test_read_averages_consistent_measurements(monkeypatch):
    drv = VirtualPSUDriver(
        read_sequence=[
            (1.00, 0.10, "CV"),
            (1.01, 0.11, "CV"),
            (1.01, 0.11, "CV"),
        ],
        vres_read=0.01,
        ires_read=0.01,
        read_idle_time=0.0,
    )
    monkeypatch.setattr(ps_mod.powersupply_KORAD, "KORAD", lambda *a, **k: drv)
    monkeypatch.setattr(ps_mod.time, "sleep", lambda *_: None)

    psu = ps_mod.PSU(port="VIRTUAL", commandset="KORAD", label="PSU1")
    v, i, limit = psu.read(N=2)

    assert abs(v - 1.005) < 1e-9
    assert abs(i - 0.105) < 1e-9
    assert limit == "CV"


@pytest.mark.virtual_hw
def test_composite_psu_uses_longest_read_idle_time(monkeypatch):
    drvs = [
        VirtualPSUDriver(read_idle_time=0.05),
        VirtualPSUDriver(read_idle_time=0.2),
    ]

    def _factory(*args, **kwargs):
        return drvs.pop(0)

    monkeypatch.setattr(ps_mod.powersupply_KORAD, "KORAD", _factory)

    psu = ps_mod.PSU(
        port=("VIRTUAL_A", "VIRTUAL_B"),
        commandset=("KORAD", "KORAD"),
        label="PSU_STACK",
    )
    assert psu.READIDLETIME == 0.2


@pytest.mark.virtual_hw
def test_runtime_virtual_commandset_smoke():
    psu = ps_mod.PSU(port="VIRTUAL", commandset="VIRTUAL", label="PSU1")
    psu.turnOn()
    psu.setVoltage(1.234, wait_stable=False)
    psu.setCurrent(10.0, wait_stable=False)
    v, i, limiter = psu.read()
    assert abs(v - 1.234) < 1e-9
    assert i >= 0.0
    assert limiter == "CV"


@pytest.mark.virtual_hw
def test_runtime_virtual_triode_coupling_between_anode_and_grid():
    anode = ps_mod.PSU(port="VIRTUAL_A", commandset="VIRTUAL", label="PSU1")
    grid = ps_mod.PSU(port="VIRTUAL_G", commandset="VIRTUAL", label="PSU2")

    anode.turnOn()
    grid.turnOn()
    anode.setCurrent(10.0, wait_stable=False)
    grid.setCurrent(10.0, wait_stable=False)
    anode.setVoltage(200.0, wait_stable=False)

    grid.setVoltage(-2.0, wait_stable=False)
    _, ia_low, _ = anode.read()

    grid.setVoltage(2.0, wait_stable=False)
    _, ia_high, _ = anode.read()

    assert ia_high > ia_low


@pytest.mark.virtual_hw
def test_runtime_virtual_triode_respects_psu_polarity_mapping():
    anode = ps_mod.PSU(port="VIRTUAL_A", commandset="VIRTUAL", label="PSU1")
    grid = ps_mod.PSU(port="VIRTUAL_G", commandset="VIRTUAL", label="PSU2")

    anode.turnOn()
    grid.turnOn()
    anode.setCurrent(10.0, wait_stable=False)
    grid.setCurrent(10.0, wait_stable=False)
    anode.setVoltage(200.0, wait_stable=False)

    # Inverted polarity means positive PSU2 setpoint maps to negative effective Vg.
    grid.TEST_POLARITY = -1

    grid.setVoltage(0.5, wait_stable=False)
    _, ia_less_negative_grid, _ = anode.read()

    grid.setVoltage(2.0, wait_stable=False)
    _, ia_more_negative_grid, _ = anode.read()

    assert ia_more_negative_grid < ia_less_negative_grid
