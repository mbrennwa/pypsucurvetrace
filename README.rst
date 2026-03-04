###################
``pypsucurvetrace``
###################

See index.html or https://mbrennwa.github.io/pypsucurvetrace.

This software is licensed under the GNU General Public License v3.0 (GPL-3.0).

The Routed Gothic and National Park fonts are licensed under the SIL Open Font License (OFL). The FreeSans font is licensed under the GPL-3 License.


########################
Testing and Validation
########################

Virtual PSU driver tests validate control logic without requiring physical instruments.

For runtime experiments without instruments, set PSU type to ``VIRTUAL`` in the tester configuration.
The built-in virtual DUT model is a static triode-like model (no temperature / warm-up variation).
Virtual DUT voltage mapping is polarity-aware: effective DUT voltage is ``TEST_POLARITY * PSU_voltage``.

Virtual runtime example files are in ``examples/``:

- ``examples/curvetrace_config_virtual.txt`` (tester / PSU config)
- ``examples/virtual_dut_triode_static.txt`` (DUT sweep config)

To run a virtual trace, first copy the tester config to the location expected by ``curvetrace``:

- ``cp examples/curvetrace_config_virtual.txt "$HOME/curvetrace_config.txt"``
- ``curvetrace -c examples/virtual_dut_triode_static.txt --nohello``

- Install test dependencies: ``pip install -e .[test]``
- Run all tests: ``python3 -m pytest tests``
- Run virtual hardware tests only: ``python3 -m pytest tests -m virtual_hw``
- Hardware-in-the-loop tests (if available) should be marked separately as ``hw``.
