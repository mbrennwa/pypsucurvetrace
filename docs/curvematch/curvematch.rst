.. _curvematch:

.. include:: ../symbols.rst
.. |Dij| replace:: :math:`D_{ij}`
.. |D0| replace:: :math:`D_0`
.. |Ddelta| replace:: :math:`D_{ij}-D_0`



The ``curvematch`` program
==========================

.. autosummary::
   :toctree: generated


The ``curvematch`` program calculates the «difference between two curve sets». This is useful to find parts with similar curves (part matching). The difference between the curve sets of two DUTs is calculated and expressed as follows:

   #. The values of the gate/grid voltage (|Vg|) or base current (|Ib|) of both DUTs are interpolated from the raw data to a rectangular grid of |U1| and |I1| values.
   #. The differences |Dij| of the |Vg| or |Ib| values are calculated at each grid point :math:`(i,j)`.
   #. The RMS value of the |Dij| values is reported. A low RMS value indicates a good overall match between the two DUTs.
   #. The mean |D0| of all |Dij| values is calculated, and the RMS value of |Ddelta| is reported. A low value indicates that the curves of the two DUTs tend to be parallel to each other, but may exhibit a constant |Vg| or |Ib| offset.

The calculation of these RMS values can be restricted to data within a certain range of |U1| and |I1| values.

The ``curvematch`` documentation can be accessed from the ``curvematch`` program directly:

.. code-block:: console

   curvematch --help