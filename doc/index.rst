===============================================================
qiprofile-rest-client: Quantitative Imaging Profile REST client
===============================================================

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
1. Install the `QuIP REST server`_.

2. Add ``qiprofile-rest-client`` to your Python_ project setup.py
   ``install_requires``.

3. Update your project installation to reflect the REST client dependency.

4. Start the `QuIP REST server`_.


*****
Usage
*****

See the `QuIP REST Data Model`_ and API documentation.


***********
Development
***********

Testing is performed with the nose_ package, which must be installed separately.

Documentation is built automatically by ReadTheDocs_ when the project is pushed
to GitHub. Documentation can be generated locally as follows:

* Install Sphinx_, if necessary.

* Run the following in the ``doc`` subdirectory::

      make html


---------

.. container:: copyright


.. Targets:

.. _Knight Cancer Institute: http://www.ohsu.edu/xd/health/services/cancer

.. _MongoDB: http://django-mongodb.org

.. _nose: https://nose.readthedocs.org/en/latest/

.. _Python: http://www.python.org

.. _QuIP REST Data Model: http://qiprofile-rest-client.readthedocs.org/en/latest/data_model.html

.. _QuIP REST server: http://qiprofile-rest.readthedocs.org/en/latest/

.. _ReadTheDocs: https://www.readthedocs.org

.. _Sphinx: http://sphinx-doc.org/index.html

.. toctree::
  :hidden:
  
  api/index
  data_model
  