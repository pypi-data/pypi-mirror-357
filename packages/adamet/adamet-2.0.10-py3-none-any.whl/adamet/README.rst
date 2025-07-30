The AdaMet Package
==================

**Adaptive Metropolis for Bayesian Analysis**

.. image:: https://img.shields.io/pypi/v/adamet.svg
        :target: https://pypi.org/project/adamet/
.. image:: https://img.shields.io/badge/arXiv-1208.3522-orange.svg
    :target: https://arxiv.org/abs/1208.3522
.. image:: https://img.shields.io/badge/DOI-10.1093/mnras/stt562-green.svg
    :target: https://doi.org/10.1093/mnras/stt562

AdaMet is a well-tested Python implementation by 
`Cappellari et al. (2013) <https://ui.adsabs.harvard.edu/abs/2013MNRAS.432.1709C>`_ 
of the Adaptive Metropolis algorithm by
`Haario H., Saksman E., Tamminen J. (2001) <https://doi.org/10.2307/3318737>`_.
It was used in several published papers in the astrophysics literature.

.. contents:: :depth: 2

Attribution
-----------

If you use this software for your research, please cite at least
`Cappellari et al. (2013)`_ where the implementation was introduced. 
The BibTeX entry for the paper is::

    @ARTICLE{Cappellari2013a,
        author = {{Cappellari}, M. and {Scott}, N. and {Alatalo}, K. and
            {Blitz}, L. and {Bois}, M. and {Bournaud}, F. and {Bureau}, M. and
            {Crocker}, A.~F. and {Davies}, R.~L. and {Davis}, T.~A. and {de Zeeuw},
            P.~T. and {Duc}, P.-A. and {Emsellem}, E. and {Khochfar}, S. and
            {Krajnovi{\'c}}, D. and {Kuntschner}, H. and {McDermid}, R.~M. and
            {Morganti}, R. and {Naab}, T. and {Oosterloo}, T. and {Sarzi}, M. and
            {Serra}, P. and {Weijmans}, A.-M. and {Young}, L.~M.},
        title = "{The ATLAS$^{3D}$ project - XV. Benchmark for early-type
            galaxies scaling relations from 260 dynamical models: mass-to-light
            ratio, dark matter, Fundamental Plane and Mass Plane}",
        journal = {MNRAS},
        eprint = {1208.3522},
        year = 2013,
        volume = 432,
        pages = {1709-1741},
        doi = {10.1093/mnras/stt562}
    }

Installation
------------

install with::

    pip install adamet

Without writing access to the global ``site-packages`` directory, use::

    pip install --user adamet

Documentation
-------------

The documentation is in the docstring of the file ``adamet.py``
or on `PyPi <https://pypi.org/project/adamet/>`_.

###########################################################################
