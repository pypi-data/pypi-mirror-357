rhodent
=======

**rhodent** is a tool for analyzing hot-carrier distributions based on input from real-time time-dependent density functional theory simulations.
A detailed description of the functionality provided as well as tutorials can be found in the `user guide <https://rhodent.materialsmodeling.org/>`_.

**rhodent** can be installed via `pip`::

    pip3 install rhodent

**rhodent** has been developed at the `Department of Physics <https://www.chalmers.se/en/departments/physics/>`_ at `Chalmers University of Technology <https://www.chalmers.se/>`_ (Gothenburg, Sweden) in the `Condensed Matter and Materials Theory division <http://www.materialsmodeling.org>`_.


Development
-----------

The test suite is run using `pytest`::

  pytest tests/

The tests should also pass in parallel MPI execution, on any number of ranks::

  mpirun -np 2 pytest -x tests/
  mpirun -np 3 pytest -x tests/
  mpirun -np 4 pytest -x tests/
  mpirun -np 5 pytest -x tests/
  mpirun -np 6 pytest -x tests/

Tests are configured such that they are skipped if the number of ranks is incompatible with the particular test.

Only a subset of data required for testing is included in the repository.
Large data files are included in a `zenodo record <https://doi.org/10.5281/zenodo.14832606>`_ that needs to be extracted into the `tests/data` directory.

The subset of tests that does not require the large data files (mostly unit-tests) can be run via::

  pytest -m 'not bigdata' tests/
