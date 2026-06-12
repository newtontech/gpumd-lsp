from __future__ import annotations

from typing import Any

# Completion items for GPUMD run.in and nep.in keywords.
#
# Source provenance: Items reference official GPUMD documentation at
# https://gpumd.org/ . The wiki manifest at raw/assets/upstream-sources.md
# maps each command to its canonical documentation URL.

_RUN_IN_KEYWORDS: list[dict[str, str]] = [
    {
        "label": "potential",
        "detail": "potential <filename>",
        "documentation": "Set potential file (e.g. NEP model); must be first in run.in.",
    },
    {
        "label": "velocity",
        "detail": "velocity <T> <seed>",
        "documentation": "Initialize atomic velocities at temperature T with given random seed.",
    },
    {
        "label": "time_step",
        "detail": "time_step <dt>",
        "documentation": "Set the integration time step in femtoseconds.",
    },
    {
        "label": "ensemble",
        "detail": "ensemble <method> [params...]",
        "documentation": "Ensemble: nve, nvt_berendsen, nvt_nose_hoover, npt_berendsen, etc.",
    },
    {
        "label": "dump_thermo",
        "detail": "dump_thermo <interval>",
        "documentation": "Dump thermodynamic quantities every N steps.",
    },
    {
        "label": "dump_position",
        "detail": "dump_position <interval> <group>",
        "documentation": "Dump atomic positions every N steps for given group.",
    },
    {
        "label": "dump_velocity",
        "detail": "dump_velocity <interval> <group>",
        "documentation": "Dump atomic velocities every N steps for given group.",
    },
    {
        "label": "dump_force",
        "detail": "dump_force <interval> <group>",
        "documentation": "Dump atomic forces every N steps for given group.",
    },
    {
        "label": "dump_exyz",
        "detail": "dump_exyz <interval> <group>",
        "documentation": "Dump extended XYZ format every N steps.",
    },
    {
        "label": "compute_hac",
        "detail": "compute_hac <sample> <output_interval> <Nc>",
        "documentation": "Compute heat autocorrelation for thermal conductivity.",
    },
    {
        "label": "compute_hnemd",
        "detail": "compute_hnemd <Fe>",
        "documentation": "Compute thermal conductivity via HNEMD with driving force Fe.",
    },
    {
        "label": "compute_msd",
        "detail": "compute_msd <sample> <interval>",
        "documentation": "Compute mean square displacement.",
    },
    {
        "label": "compute_shc",
        "detail": "compute_shc <sample> <output_interval> <Nc> [sample_interval]",
        "documentation": "Compute spectral heat current.",
    },
    {
        "label": "compute_dos",
        "detail": "compute_dos <sample> <Nc>",
        "documentation": "Compute phonon density of states.",
    },
    {
        "label": "compute_phonon",
        "detail": "compute_phonon",
        "documentation": "Compute full phonon properties.",
    },
    {
        "label": "compute_sdc",
        "detail": "compute_sdc <sample> <interval>",
        "documentation": "Compute self diffusion coefficient.",
    },
    {
        "label": "compute_gkma",
        "detail": "compute_gkma <sample> <interval> <Nc>",
        "documentation": "Compute Green-Kubo modal analysis.",
    },
    {
        "label": "compute_heat",
        "detail": "compute_heat <sample> <interval>",
        "documentation": "Compute heat current.",
    },
    {"label": "fix", "detail": "fix <group>", "documentation": "Fix atoms in the given group."},
    {
        "label": "deform",
        "detail": "deform <direction> <strain_rate> <steps>",
        "documentation": "Apply deformation to the simulation box.",
    },
    {
        "label": "change_box",
        "detail": "change_box <params...>",
        "documentation": "Modify the simulation box dimensions.",
    },
    {
        "label": "replicate",
        "detail": "replicate <nx> <ny> <nz>",
        "documentation": "Replicate the simulation cell.",
    },
    {"label": "run", "detail": "run <N_steps>", "documentation": "Run N molecular dynamics steps."},
    {
        "label": "minimize",
        "detail": "minimize <method> <tolerance> <max_steps>",
        "documentation": "Energy minimization (e.g. minimize sd 1e-6 1000).",
    },
    {
        "label": "neighbor",
        "detail": "neighbor <skin> <update_freq>",
        "documentation": "Set neighbor list parameters.",
    },
    {
        "label": "group",
        "detail": "group <id> <type...>",
        "documentation": "Define an atom group by type.",
    },
    {"label": "space", "detail": "space <group>", "documentation": "Set the space group."},
    {
        "label": "plumed",
        "detail": "plumed <file>",
        "documentation": "Enable PLUMED integration with given input file.",
    },
    {
        "label": "dftd3",
        "detail": "dftd3 <params...>",
        "documentation": "Enable DFT-D3 dispersion correction.",
    },
]

_NEP_IN_KEYWORDS: list[dict[str, str]] = [
    {
        "label": "type",
        "detail": "type <N> <type1> [type2...]",
        "documentation": "Specify the number and names of atom types for NEP training.",
    },
    {
        "label": "version",
        "detail": "version <nep_version>",
        "documentation": "Set the NEP version (e.g. 3, 4).",
    },
    {
        "label": "cutoff",
        "detail": "cutoff <rc_radial> <rc_angular>",
        "documentation": "Set radial and angular cutoff radii in Angstroms.",
    },
    {
        "label": "n_max",
        "detail": "n_max <n_radial> <n_angular>",
        "documentation": "Set number of radial and angular basis functions.",
    },
    {
        "label": "l_max",
        "detail": "l_max <l_radial> <l_angular>",
        "documentation": "Set maximum angular momentum quantum numbers.",
    },
    {
        "label": "basis_size",
        "detail": "basis_size <size>",
        "documentation": "Set the size of the neuron basis.",
    },
    {
        "label": "lambda_e",
        "detail": "lambda_e <value>",
        "documentation": "Energy loss regularization parameter.",
    },
    {
        "label": "lambda_f",
        "detail": "lambda_f <value>",
        "documentation": "Force loss regularization parameter.",
    },
    {
        "label": "lambda_v",
        "detail": "lambda_v <value>",
        "documentation": "Virial loss regularization parameter.",
    },
    {"label": "batch_size", "detail": "batch_size <N>", "documentation": "Training batch size."},
    {
        "label": "population_size",
        "detail": "population_size <N>",
        "documentation": "Population size for evolutionary training.",
    },
    {
        "label": "generation",
        "detail": "generation <N>",
        "documentation": "Number of training generations.",
    },
    {
        "label": "train_file",
        "detail": "train_file <path>",
        "documentation": "Path to training data in train.xyz format.",
    },
    {
        "label": "test_file",
        "detail": "test_file <path>",
        "documentation": "Path to test data in test.xyz format.",
    },
    {
        "label": "zbl",
        "detail": "zbl <r_inner> <r_outer>",
        "documentation": "ZBL screening parameters for short-range repulsion.",
    },
    {
        "label": "weight",
        "detail": "weight <energy> <force> <virial>",
        "documentation": "Relative weights for energy, force, and virial losses.",
    },
    {
        "label": "prediction_csv",
        "detail": "prediction_csv",
        "documentation": "Output prediction results in CSV format.",
    },
]


def get_completions() -> list[dict[str, Any]]:
    """Return completion items for run.in keywords."""
    return list(_RUN_IN_KEYWORDS)


def get_nep_completions() -> list[dict[str, Any]]:
    """Return completion items for nep.in keywords."""
    return list(_NEP_IN_KEYWORDS)
