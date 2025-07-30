GraDiv
======


.. contents:: Table of Contents
    :depth: 2


GraDiv is a tool to lead diversity analysis on a pangenome graph.

It allows users to call variants from a pangenome graph indexed with GraTools, then compute diversity statistics from them.


Installation
============

.. code-block:: bash

    python3 -m pip install gradiv


Usage of GraDiv
=================

Commands available
------------------

.. code-block:: bash

    Usage: gradiv [OPTIONS] COMMAND [ARGS]...

      GraDiv tool for diversity analysis of pangenome graphs.

    Options:
      --help  Show this message and exit.

    Commands:
      call     Generate genotype tables from a GFA file and outputs them in a...
      compute  Compute statistics from a GraDiv directory.


Testing a small GFA
-------------------

A small test graph is available in test_data/. The GFA file and GraTools index are provided.

Figures are provided to visualize the graph's structure. It is displayed as four different sub-graphs.

.. image:: https://forge.ird.fr/phim/gradiv/-/raw/main/test_data/figures/indels.png?ref_type=heads



Authors
=======

* Margaux IMBERT (PHIM, UM)
* Sébastien RAVEL (PHIM, CIRAD)
* Christine TRANCHANT (DIADE, IRD)
* Stéphane DE MITA (PHIM, INRAE)
