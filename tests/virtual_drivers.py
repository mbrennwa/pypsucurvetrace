"""
Virtual PSU drivers for hardware-free tests.
"""


class VirtualPSUDriver:
    def __init__(
        self,
        model="VIRTUAL",
        read_sequence=None,
        vmin=0.0,
        vmax=30.0,
        imax=5.0,
        pmax=150.0,
        vres_set=0.01,
        ires_set=0.001,
        vres_read=0.01,
        ires_read=0.001,
        voffset_max=0.0,
        ioffset_max=0.0,
        max_settle_time=0.05,
        read_idle_time=0.0,
    ):
        self.MODEL = model
        self.VMIN = vmin
        self.VMAX = vmax
        self.IMAX = imax
        self.PMAX = pmax
        self.VRESSET = vres_set
        self.IRESSET = ires_set
        self.VRESREAD = vres_read
        self.IRESREAD = ires_read
        self.VOFFSETMAX = voffset_max
        self.IOFFSETMAX = ioffset_max
        self.MAXSETTLETIME = max_settle_time
        self.READIDLETIME = read_idle_time

        self.COMMANDSET = "KORAD"
        self.output_enabled = False
        self.last_voltage = 0.0
        self.last_current = 0.0
        self._read_sequence = list(read_sequence or [])

    def output(self, state):
        self.output_enabled = bool(state)

    def voltage(self, value):
        self.last_voltage = float(value)

    def current(self, value):
        self.last_current = float(value)

    def reading(self):
        if self._read_sequence:
            return self._read_sequence.pop(0)
        return (self.last_voltage, self.last_current, "CV")
