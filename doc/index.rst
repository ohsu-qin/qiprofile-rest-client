========================================================
qiprofile-rest: Quantitative Imaging Profile REST server
========================================================

********
Synopsis
********
The Quantitative Imaging Profile (*QuIP*) REST client interacts with
the `QuIP REST server`_.

:API: https://qiprofile-rest-client.readthedocs.org/en/latest/api/index.html

:Git: https://github.com/ohsu-qin/qiprofile-rest-client


************
Installation
************
1. Install the Python_ pip_ package on your workstation, if necessary.

2. Start the `QuIP REST server`_, if necessary.

3. Add ``qiprofile-rest-client`` to your Python_ project setup.py
   ``install_requires``.

4. Update your project installation to reflect the REST client dependency.


*****
Usage
*****

See the `QuIP REST Data Model`_ and API documentation.


---------

.. container:: copyright

  Copyright (C) 2015 Oregon Health & Science University `Knight Cancer Institute`_.
  All rights reserved.


.. Targets:

.. _Knight Cancer Institute: http://www.ohsu.edu/xd/health/services/cancer

.. _MongoDB: http://django-mongodb.org

.. _pip: https://pypi.python.org/pypi/pip

.. _Python: http://www.python.org

.. _QuIP REST Data Model: https://github.com/ohsu-qin/qiprofile-rest-client/doc/quip_data_model.png

.. _QuIP REST server: https://github.com/ohsu-qin/qiprofile-rest

.. toctree::
  :hidden:
  
  api/index
