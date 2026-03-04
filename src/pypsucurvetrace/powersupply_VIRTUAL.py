"""
Virtual power supply driver for hardware-free runs.
"""

import math


class _VirtualDUTBus:
    """
    Shared state for VIRTUAL PSU channels.
    """

    channels = []


class VIRTUAL(object):
    """
    Minimal software-only PSU driver implementing the same API as real drivers.
    """

    def __init__(self, port, debug=False):
        _ = port
        _ = debug

        self.MODEL = "VIRTUAL"
        self.VMIN = 0.0
        self.VMAX = 300.0
        self.IMAX = 10.0
        self.PMAX = 300.0
        self.VRESSET = 0.001
        self.IRESSET = 0.001
        self.VRESREAD = 0.001
        self.IRESREAD = 0.001
        self.VOFFSETMAX = 0.0
        self.IOFFSETMAX = 0.0
        self.MAXSETTLETIME = 0.2
        self.READIDLETIME = 0.01

        self._out = False
        self._vset = 0.0
        self._iset = 0.0
        self._channel_idx = len(_VirtualDUTBus.channels)
        _VirtualDUTBus.channels.append(self)

        # Static triode model parameters (Koren-like softplus formulation).
        self._mu = 20.0
        self._kg1 = 1200.0
        self._kp = 300.0
        self._kvb = 300.0
        self._ex = 1.4
        self._kg2 = 1e-4
        self._eg = 1.5

    @staticmethod
    def _softplus(x):
        # Numerically stable log(1 + exp(x)).
        return math.log1p(math.exp(-abs(x))) + max(x, 0.0)

    def _effective_output_voltage(self):
        if not self._out:
            return 0.0
        sign = 1
        parent = getattr(self, "_PARENT_PSU", None)
        if parent is not None:
            sign = parent.TEST_POLARITY
        return sign * self._vset

    def output(self, state):
        self._out = bool(state)

    def voltage(self, voltage):
        if voltage > self.VMAX:
            voltage = self.VMAX
        if voltage < self.VMIN:
            voltage = self.VMIN
        self._vset = float(voltage)

    def current(self, current):
        if current > self.IMAX:
            current = self.IMAX
        if current < 0.0:
            current = 0.0
        self._iset = float(current)

    def reading(self):
        if not self._out:
            return 0.0, 0.0, "CV"

        # Use channel 0 as anode supply (Va), channel 1 as grid supply (Vg).
        # Additional channels are accepted and report zero current.
        Va = 0.0
        Vg = 0.0
        if len(_VirtualDUTBus.channels) > 0:
            ch_a = _VirtualDUTBus.channels[0]
            Va = ch_a._effective_output_voltage()
        if len(_VirtualDUTBus.channels) > 1:
            ch_g = _VirtualDUTBus.channels[1]
            Vg = ch_g._effective_output_voltage()

        # Static Koren-style triode model:
        # E1 = (Va/Kp) * ln(1 + exp(Kp * (1/mu + Vg/sqrt(Kvb + Va^2))))
        # Ia = E1^Ex / Kg1
        va = max(Va, 0.0)
        denom = math.sqrt(self._kvb + va * va)
        arg = self._kp * ((1.0 / self._mu) + (Vg / denom))
        e1 = (va / self._kp) * self._softplus(arg)
        ia = (max(e1, 0.0) ** self._ex) / self._kg1
        ig = self._kg2 * (max(Vg, 0.0) ** self._eg)

        if self._channel_idx == 0:
            current = ia
        elif self._channel_idx == 1:
            current = ig
        else:
            current = 0.0

        # Respect current compliance (iset acts as current limit).
        if self._iset <= 0.0:
            current = 0.0
            limiter = "CC"
        elif current > self._iset:
            current = self._iset
            limiter = "CC"
        else:
            limiter = "CV"

        return float(self._vset), float(current), limiter
