pymodaq_plugins_datamixer
#########################

.. image:: https://img.shields.io/pypi/v/pymodaq_plugins_datamixer.svg
   :target: https://pypi.org/project/pymodaq_plugins_datamixer/
   :alt: Latest Version

.. image:: https://readthedocs.org/projects/pymodaq/badge/?version=latest
   :target: https://pymodaq.readthedocs.io/en/stable/?badge=latest
   :alt: Documentation Status

.. image:: https://github.com/PyMoDAQ/pymodaq_plugins_datamixer/workflows/Upload%20Python%20Package/badge.svg
    :target: https://github.com/PyMoDAQ/pymodaq_plugins_datamixer

.. image:: https://github.com/PyMoDAQ/pymodaq_plugins_datamixer/actions/workflows/Test.yml/badge.svg
    :target: https://github.com/PyMoDAQ/pymodaq_plugins_datamixer/actions/workflows/Test.yml


Plugin exposing an extension to the DashBoard: the DataMixer allowing to mix data from other DashBoard detectors using
scripted formula from the full name of the data or from more complex model allowing a form of live post-analysis. The
data out of the formula or out of the models can be used within the DashBoard for other extensions (for instance live
plots in a scan)


Authors
=======

* Sebastien J. Weber  (sebastien.weber@cemes.fr)



Instruments
===========

Below is the list of instruments included in this plugin


Viewer0D
++++++++

* **DataMixer**: Fake detector allowing to display the results of the extension calculations within
  the DashBoard, hence allowing those data to be used within other extensions aka the DAQ_Scan


Extensions
==========

* DataMixer: extension to the DashBoard: the DataMixer. It allows to mix data from other
  DashBoard detectors using scripted formula from the full name of the data or from more complex model allowing a form
  of live post-analysis. The data out of the formula or out of the models can be used within the DashBoard for other
  extensions (for instance live plots in a scan)


Installation instructions
=========================

* pymodaq >= 5.0.1
* pymodaq_data >= 0.0.1