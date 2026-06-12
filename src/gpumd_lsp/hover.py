from __future__ import annotations

# Hover documentation for GPUMD/NEP keywords.
#
# Source provenance: _HOVER_DOCS entries reference the official GPUMD
# documentation at https://gpumd.org/ . The wiki manifest at
# raw/assets/upstream-sources.md maps each command to its canonical URL.

_HOVER_DOCS: dict[str, str] = {
    "potential": (
        "**potential** <filename>\n\n"
        "Specify the potential file to use for the simulation. "
        "This must be the first command in run.in. "
        "Commonly references a NEP model file (e.g., `nep.txt`)."
    ),
    "velocity": (
        "**velocity** <T> <seed>\n\n"
        "Initialize atomic velocities from a Maxwell-Boltzmann distribution "
        "at temperature T (K) using the given random seed."
    ),
    "time_step": (
        "**time_step** <dt>\n\n"
        "Set the MD integration time step in femtoseconds. "
        "Typical values: 1 fs for most systems."
    ),
    "ensemble": (
        "**ensemble** <method> [params...]\n\n"
        "Set the thermodynamic ensemble:\n"
        "- `nve` — microcanonical\n"
        "- `nvt_berendsen T T tau_T` — Berendsen thermostat\n"
        "- `nvt_nose_hoover T T tau_T` — Nosé-Hoover thermostat\n"
        "- `npt_berendsen T T tau_T pxx pyy pzz tau_p` — Berendsen barostat\n"
        "- `npt_mtk T T tau_T pxx pyy pzz tau_p` — MTK barostat\n"
        "- `heat_bc T1 T2 width` — heat boundary condition"
    ),
    "dump_thermo": (
        "**dump_thermo** <interval>\n\n"
        "Output thermodynamic quantities (temperature, pressure, etc.) "
        "every N integration steps to thermo.out."
    ),
    "dump_position": (
        "**dump_position** <interval> <group>\n\n"
        "Write atomic positions every N steps for the specified group."
    ),
    "dump_velocity": (
        "**dump_velocity** <interval> <group>\n\n"
        "Write atomic velocities every N steps for the specified group."
    ),
    "dump_force": (
        "**dump_force** <interval> <group>\n\n"
        "Write atomic forces every N steps for the specified group."
    ),
    "dump_exyz": (
        "**dump_exyz** <interval> <group>\n\nDump trajectory in extended XYZ format every N steps."
    ),
    "compute_hac": (
        "**compute_hac** <sample> <output_interval> <Nc>\n\n"
        "Compute heat autocorrelation for thermal conductivity via "
        "Green-Kubo formalism. Nc is the number of correlation steps."
    ),
    "compute_hnemd": (
        "**compute_hnemd** <Fe>\n\n"
        "Compute thermal conductivity using the HNEMD method "
        "with driving force parameter Fe."
    ),
    "compute_msd": (
        "**compute_msd** <sample> <interval>\n\n"
        "Compute mean square displacement for diffusion analysis."
    ),
    "compute_shc": (
        "**compute_shc** <sample> <output_interval> <Nc> [sample_interval]\n\n"
        "Compute spectral heat current for frequency-dependent thermal conductivity."
    ),
    "compute_dos": (
        "**compute_dos** <sample> <Nc>\n\n"
        "Compute phonon density of states via velocity autocorrelation."
    ),
    "compute_phonon": (
        "**compute_phonon**\n\nCompute full phonon dispersion and related properties."
    ),
    "compute_sdc": (
        "**compute_sdc** <sample> <interval>\n\n"
        "Compute self diffusion coefficient from velocity autocorrelation."
    ),
    "compute_gkma": (
        "**compute_gkma** <sample> <interval> <Nc>\n\n"
        "Compute Green-Kubo modal analysis for modal thermal conductivity."
    ),
    "compute_heat": ("**compute_heat** <sample> <interval>\n\nCompute per-atom heat current."),
    "fix": ("**fix** <group>\n\nFix atoms belonging to the specified group in place."),
    "deform": (
        "**deform** <direction> <strain_rate> <steps>\n\n"
        "Apply uniaxial deformation to the simulation box."
    ),
    "change_box": ("**change_box** <params...>\n\nModify simulation box dimensions or shape."),
    "replicate": ("**replicate** <nx> <ny> <nz>\n\nReplicate the simulation cell nx×ny×nz times."),
    "run": (
        "**run** <N_steps>\n\n"
        "Execute N molecular dynamics integration steps. "
        "Use `run 0` for a single-point energy evaluation."
    ),
    "minimize": (
        "**minimize** <method> <tolerance> <max_steps>\n\n"
        "Energy minimization. Method options: sd (steepest descent), "
        "fire (FIRE algorithm). Example: `minimize sd 1e-6 1000`."
    ),
    "neighbor": (
        "**neighbor** <skin> <update_freq>\n\n"
        "Configure the Verlet neighbor list with given skin distance "
        "and update frequency."
    ),
    "group": (
        "**group** <id> <type...>\n\n"
        "Define an atom group by specifying which atom types belong to it."
    ),
    "space": ("**space** <group>\n\nSet the space group symmetry for the simulation."),
    "plumed": ("**plumed** <file>\n\nEnable PLUMED metadynamics/bias with the given input file."),
    "dftd3": ("**dftd3** <params...>\n\nEnable DFT-D3 dispersion corrections to the potential."),
    # NEP keywords
    "type": (
        "**type** <N> <type1> [type2...]\n\n"
        "Specify the number of atom types and their labels for NEP training. "
        "Example: `type 2 C H`."
    ),
    "version": (
        "**version** <nep_version>\n\nSet the NEP model version. Currently supported: 3, 4."
    ),
    "cutoff": (
        "**cutoff** <rc_radial> <rc_angular>\n\n"
        "Set the radial and angular cutoff distances in Angstroms. "
        "Typical values: cutoff 5 4."
    ),
    "n_max": (
        "**n_max** <n_radial> <n_angular>\n\n"
        "Number of radial and angular basis functions. "
        "Controls the complexity of the NEP descriptor."
    ),
    "l_max": (
        "**l_max** <l_radial> <l_angular>\n\n"
        "Maximum angular momentum quantum numbers for radial and angular terms."
    ),
    "basis_size": ("**basis_size** <size>\n\nSize of the neuron basis in the NEP neural network."),
    "lambda_e": ("**lambda_e** <value>\n\nL2 regularization parameter for the energy loss term."),
    "lambda_f": ("**lambda_f** <value>\n\nL2 regularization parameter for the force loss term."),
    "lambda_v": ("**lambda_v** <value>\n\nL2 regularization parameter for the virial loss term."),
    "batch_size": (
        "**batch_size** <N>\n\nNumber of training structures per mini-batch during NEP training."
    ),
    "population_size": (
        "**population_size** <N>\n\nNumber of candidate models in the evolutionary population."
    ),
    "generation": (
        "**generation** <N>\n\nTotal number of evolutionary generations for NEP training."
    ),
    "train_file": ("**train_file** <path>\n\nPath to the training dataset in extended XYZ format."),
    "test_file": ("**test_file** <path>\n\nPath to the test dataset in extended XYZ format."),
    "zbl": (
        "**zbl** <r_inner> <r_outer>\n\n"
        "Enable ZBL short-range repulsion between r_inner and r_outer Angstroms."
    ),
    "weight": (
        "**weight** <energy> <force> <virial>\n\n"
        "Relative loss weights for energy, force, and virial components."
    ),
    "prediction_csv": (
        "**prediction_csv**\n\nOutput prediction results in CSV format during NEP evaluation."
    ),
}


def get_hover(keyword: str) -> str | None:
    """Return hover documentation for a GPUMD/NEP keyword, or None."""
    return _HOVER_DOCS.get(keyword)
