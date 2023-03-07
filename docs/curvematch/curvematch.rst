.. _curvematch:

.. include:: ../symbols.rst
.. |Dij| replace:: :math:`D_{ij}`
.. |D0| replace:: :math:`D_0`
.. |Ddelta| replace:: :math:`D_{ij}-D_0`



The |curvematch| program
==========================

.. autosummary::
   :toctree: generated


The |curvematch| program quantifies the «similarity» of two curve sets. Consider the following figure with the |U1|, |I1|, and |U2| data measured from two different VFET power transistors. The data from the two transistors are represented by the red and blue surfaces in a 3-dimensional plot instead of the conventional curves plot:

.. image:: curvematch_surfaces.png
  :width: 658
  :alt: 3-dimensional representation of the (|U1|,\ |I1|,\ |U2|) curve data from two different VFET power transistors.

The «similarity» between the two data sets is defined as the RMS value of the vertical difference between the two surfaces (i.e., the RMS difference along the |U2| axis).

The procedure implemented in the |curvematch| program to calculate and report the similarity between the curve sets is as follows:

   #. For current-controlled DUTs (BJTs), the |U2| value is converted to the base current |IB|. For voltage controlled DUTs (FETs, tubes), the |U2| voltage is the gate/grid voltage |VG|.
   #. The |IB| or |VG| data of both DUTs are interpolated to a rectangular grid of |U1| and |I1| values.
   #. At each grid point :math:`(i,j)` the differences |Dij| of the |IB| or |VG| values are calculated.
   #. The RMS value of the |Dij| values is reported. A low RMS value indicates that the two curve data sets are similar to each other (i.e., the surfaces in the 3-dimensional plot are almost identical).
   #. The arithmetic mean |D0| of all |Dij| values is calculated, and the RMS value of |Ddelta| is reported. A low RMS value indicates that the curves of the two DUTs tend to be parallel to each other, but may exhibit a constant |VG| or |IB| offset (i.e., the surfaces in the 3-dimensional plot are parallel, but may be offset along the |U2| axis).

Optionally, the calculation of these RMS values can be restricted with the |curvematch| program to data points that lie within a certain range of interest of the |U1| and |I1| data.

The |curvematch| documentation can be accessed from the |curvematch| program directly:

.. code-block:: console

   curvematch --help
