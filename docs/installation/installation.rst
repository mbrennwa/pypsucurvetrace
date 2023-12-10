.. _installation:

************
Installation
************

.. autosummary::
   :toctree: generated

   pypsucurvetrace


**For the impatient:** If you are already familiar with installing Python packages, the following command may be everything you need to know to install ``pypsucurvetrace``:

.. code-block:: console

   pipx install git+https://github.com/mbrennwa/pypsucurvetrace

Otherwise, read on!


Prerequisites
-------------

The installation procedures described below used the Python package manager ``pipx``. Depending on your installation method (see below), you may also need ``git``:

   * To install these tools on Debian, Ubuntu or similar Linux distros, just run the following command:

      .. code-block:: console
   
         sudo apt install pipx git
      
   * On other Linux distros, Windows, or macOS, use the respective software installer channels or follow the instructions `here <http://pypa.github.io/pipx>`_  (for ``pipx``) and `here <http://git-scm.com/>`_ (for ``git``).
   
``pypsucurvetrace`` needs access to the serial ports of you PSUs. Make sure your user account has the required access permissions:

   * On Linux, add your username to the ``dialout`` group. If your user account is ``johndoe``, execute the following command:

      .. code-block:: console

         sudo adduser johndoe dialout
         
     Then reboot the computer for this to take effect.
      
   * On Windows, use the Device Manager program to control the COM port permissions.




Installing, upgrading, and uninstalling
---------------------------------------

To download and install ``pypsucurvetrace`` in one single command:

.. code-block:: console

   pipx install git+https://github.com/mbrennwa/pypsucurvetrace

To upgrade an existing installation of ``pypsucurvetrace``:

.. code-block:: console

   pipx upgrade pypsucurvetrace

You can also download the ``pypsucurvetrace`` code separately and then install from the local copy:

.. code-block:: console

   pipx install path/to/pypsucurvetrace

To uninstall ``pypsucurvetrace``:

.. code-block:: console

   pipx uninstall pypsucurvetrace
