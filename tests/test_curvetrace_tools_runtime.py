import pytest

import pypsucurvetrace.curvetrace_tools as tools


class _DummyLogger:
    def info(self, *_args, **_kwargs):
        pass

    def warning(self, *_args, **_kwargs):
        pass

    def error(self, *_args, **_kwargs):
        pass


class _DummyPowerSupplyFactory:
    def __init__(self):
        self.last = None

    def __call__(self, port=None, commandset=None, label=None, *_args):
        class _DummyPSU:
            CONNECTED = False

            def __init__(self):
                self.port = port
                self.commandset = commandset
                self.label = label
                self.NSTABLEREADINGS = None

        self.last = _DummyPSU()
        return self.last


@pytest.mark.virtual_hw
def test_connect_psu_parses_stacked_tuple_literals(monkeypatch):
    import pypsucurvetrace.powersupply as powersupply_mod

    factory = _DummyPowerSupplyFactory()
    monkeypatch.setattr(powersupply_mod, "PSU", factory)

    config = {
        "PSU1": {
            "COMPORT": "('VIRTUAL_A','VIRTUAL_B')",
            "TYPE": "('KORAD','VIRTUAL')",
            "NUMSTABLEREAD": "3",
        }
    }
    p = tools.connect_PSU(config, "PSU1", _DummyLogger())
    assert p.port == ("VIRTUAL_A", "VIRTUAL_B")
    assert p.commandset == ("KORAD", "VIRTUAL")
    assert p.NSTABLEREADINGS == 3


@pytest.mark.virtual_hw
def test_connect_psu_rejects_non_tuple_type_when_stacked():
    config = {
        "PSU1": {
            "COMPORT": "('VIRTUAL_A','VIRTUAL_B')",
            "TYPE": "'KORAD'",
        }
    }
    with pytest.raises(SystemExit):
        tools.connect_PSU(config, "PSU1", _DummyLogger())


class _FakePSU:
    def __init__(self, *, regulate):
        self.CONFIGURED = True
        self.CONNECTED = True
        self.LABEL = "PSU_REG" if regulate else "PSU_FIX"
        self.TEST_POLARITY = 1
        self.VRESREAD = 0.001
        self.IRESREAD = 0.001
        self.TEST_ILIMIT = 10.0
        self.TEST_PIDLELIMIT = 100.0
        self.TEST_VIDLE = 0.5 if regulate else 1.0
        self.TEST_IIDLE = 0.0 if regulate else 1.0
        self.TEST_VIDLE_MIN = 0.0 if regulate else 1.0
        self.TEST_VIDLE_MAX = 1.0 if regulate else 1.0
        self.TEST_IDLE_GM = 0.1 if regulate else None
        self._regulate = regulate
        self.last_voltage = None

    def setCurrent(self, *_args, **_kwargs):
        return None

    def setVoltage(self, value, *_args, **_kwargs):
        self.last_voltage = value

    def read(self):
        if self._regulate:
            return (self.TEST_VIDLE, 0.0, "CV")
        # Return low current compared to TEST_IIDLE -> dIf < 0 -> pushes REG upwards.
        return (1.0, 0.0, "CV")


class _FakeHeater:
    def get_temperature_string(self, do_read=False):
        _ = do_read
        return "25.0"

    def wait_for_stable_T(self, **_kwargs):
        return 0.0


@pytest.mark.virtual_hw
def test_do_idle_upper_clamp_uses_max(monkeypatch):
    reg = _FakePSU(regulate=True)
    fix = _FakePSU(regulate=False)

    clock = {"t": 0.0}

    def fake_time():
        clock["t"] += 0.02
        return clock["t"]

    monkeypatch.setattr(tools.time, "time", fake_time)
    monkeypatch.setattr(tools.time, "sleep", lambda *_: None)

    tools.do_idle(reg, fix, _FakeHeater(), seconds=0.05, file=None, wait_for_TEMP=False)

    assert reg.TEST_VIDLE == reg.TEST_VIDLE_MAX
    assert reg.last_voltage == reg.TEST_VIDLE_MAX
