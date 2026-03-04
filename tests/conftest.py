import sys
import types
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


# Allow importing hardware driver modules in environments without instrument libs.
if "minimalmodbus" not in sys.modules:
    class _DummyInstrument:  # pragma: no cover - not used by virtual tests
        def __init__(self, *args, **kwargs):
            pass

    sys.modules["minimalmodbus"] = types.SimpleNamespace(Instrument=_DummyInstrument)

if "serial" not in sys.modules:
    class _DummySerial:  # pragma: no cover - not used by virtual tests
        def __init__(self, *args, **kwargs):
            pass

    sys.modules["serial"] = types.SimpleNamespace(
        Serial=_DummySerial,
        __version__="3.5",
        SerialTimeoutException=RuntimeError,
    )


@pytest.fixture(autouse=True)
def _reset_virtual_bus():
    try:
        import pypsucurvetrace.powersupply_VIRTUAL as virtual_mod

        virtual_mod._VirtualDUTBus.channels = []
    except Exception:
        pass
    yield
