.. _curveprocess:

.. include:: ../symbols.rst

The ``curveprocess`` program
============================

.. autosummary::
   :toctree: generated


The ``curveprocess`` program extracts and calculates DUT parameters from the curve data in ``pypsucurvetrace`` files:

   * Gate/grid voltage |VG| or base current |IB| corresponding to a given operating point (|U1|, |I1|)
   * Transconductance |gm| or current gain |hfe| at a given operating point (|U1|, |I1|)
   * Output conductance |go| or output transresistance |ro| at a given operating point (|U1|, |I1|)

The ``curveprocess`` documentation can be accessed from the ``curveprocess`` program directly:

.. code-block:: console

   curveprocess --help
