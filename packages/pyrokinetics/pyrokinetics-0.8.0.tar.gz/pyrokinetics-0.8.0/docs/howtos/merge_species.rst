.. _sec-merge-species-docs:

=============================================
 Merge (multiple) species into a base species
=============================================

In the interest of computational gain, it may be useful to combine multiple species into a single species. A simple approach is to perform a density-weighted average which preserves quasineutrality. The attributes density (:math:`n`), charge (:math:`z`), density gradient (:math:`1/L_n`) and mass (:math:`M`) of the new species can be calculated as (for example):

.. math::

   \begin{align*}
            n_m &= \sum_s n_s \\
            z_m &= \frac{\sum_s (z_s n_s)}{ n_m } \\
            M_m &= \frac{\sum_s (M_s n_s)} {n_m} \\
            1/L_{n_m} &= \frac{\sum_s (z_s n_s(1/L_{n_s}))} { z_m n_m }
   \end{align*}

The summation :math:`\sum_s` is over all the species :math:`s` participating in the merge, whereas the subscript :math:`m` represents the merged-species. The optional argument ``keep_base_species_z = True`` preserves the charge of the base species and adjusts the merged density, whereas ``keep_base_species_z = False`` preserves the number density of the ions (before and after the merge) and adjusts the charge state to ensure a quasineutral plasma. Both methods give the same density gradient. We can either choose to retain the mass of the base species by setting ``keep_base_species_mass = True``, or if ``False``, then depending on the logical value of ``keep_base_species_z`` (affects density), the new merged mass can assume (very) different values.

.. attention::
   The flag ``keep_base_species_z = False`` preserves the kinetic pressure before and after the merge along with ensuring quasineutrality.  However, the option ``keep_base_species_z = True`` changes the total pressure contained in the species as quasineutrality is maintained.


This is achieved in ``pyrokinetics`` as follows:

.. code-block:: python

    >>> from pyrokinetics import template_dir, Pyro
    >>>
    >>>  # point to equilibrium and kinetics files
    >>> eq_file = template_dir / "test.geqdsk"
    >>> kinetics_file = template_dir / "jetto.jsp"
    >>>
    >>> # create pyro object which contains global properties
    >>> pyro = Pyro(
        eq_file=eq_file,
        kinetics_file=kinetics_file,
        kinetics_type="JETTO",
        kinetics_kwargs={"time": 550},
    )
    >>>
    >>> # generate local parameters at psi_n=0.5
    >>> pyro.load_local(psi_n=0.5, local_geometry="Miller")
    >>>
    >>> # merge species `impurity1` into `deuterium` (and remove impurity1 attributes)
    >>> # by calling the merge_local method
    >>> pyro.local_species.merge_species('deuterium',['impurity1'])
    >>>
    >>> # now write to your choice of GK code input (e.g. GENE)
    >>> pyro.write_gk_file(file_name="input.gene", gk_code="GENE")

A script `example_merge_species.py` is provided which does this.
