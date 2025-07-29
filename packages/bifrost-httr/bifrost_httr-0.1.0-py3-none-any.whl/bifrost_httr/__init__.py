"""BIFROST HTTr Analysis Package.

This package provides tools for analyzing high-throughput transcriptomics (HTTr) data
using the BIFROST (Bayesian Inference of Fold Response and Omics Statistical Testing)
methodology.

Version: 0.1.0
"""

from .core.analysis import gen_plotting_data, run_concentration_response_analysis
from .core.data_processing import (
    filter_percent_mapped_reads,
    filter_total_mapped_reads,
    generate_bifrost_inputs,
    process_batches,
    process_data,
    validate_config,
    validate_counts_table,
    validate_filter_dict,
    validate_meta_data,
    validate_output_directory,
    validate_substances_cell_types,
    write_bifrost_input,
)
from .core.model import fit_model
from .visualization.data import BifrostData, ProbeData
from .visualization.report import BifrostMultiQCReport

__all__ = [
    "BifrostData",
    "BifrostMultiQCReport",
    "ProbeData",
    "filter_percent_mapped_reads",
    "filter_total_mapped_reads",
    "fit_model",
    "gen_plotting_data",
    "generate_bifrost_inputs",
    "process_batches",
    "process_data",
    "run_concentration_response_analysis",
    "validate_config",
    "validate_counts_table",
    "validate_filter_dict",
    "validate_meta_data",
    "validate_output_directory",
    "validate_substances_cell_types",
    "write_bifrost_input",
]
