.. _curveprocess:

.. include:: ../symbols.rst




.. role:: custom-math(raw)
   :format: latex html

:custom-math:`\mycustomsymbol`





The ``curveprocess`` program
============================

.. autosummary::
   :toctree: generated


The ``curveprocess`` program extracts and calculates DUT parameters from the curve data in ``pypsucurvetrace`` files:

   * Gate/grid voltage |VG| or base current |IB| corresponding to a given operating point (|U1|, |I1|)

   * Transconductance |gm| or current gain |hfe| at a given operating point (|U1|, |I1|):
    .. math::
    	g_{\rm m} = ∂I_1/∂U_2 \textrm{  or  } h_{\rm fe} = ∂I_1/∂I_2  
   * Output conductance (or output transresistance) |go| at a given operating point (|U1|, |I1|):
    .. math::
    	g_{\rm o} = ∂I_1/∂U_1

The ``curveprocess`` documentation can be accessed from the ``curveprocess`` program directly :custom-math:`\mycustomsymbol`:

.. code-block:: console

   curveprocess --help
