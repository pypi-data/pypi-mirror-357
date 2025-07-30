# pytacs: Python Topology-Aware Convoluting Spots -
#  an improved version of TopACT (https://gitlab.com/kfbenjamin/topact)
#  implementation.

# Author: Liu X., 2024.12

# Novelty so far:
# - Self-discovered prior knowledge;
# - Improved cell shape approximation;
# - Independency from imaging segmentation information;
# - Improved local classifier strategy - higher inferencing accuracy;


__author__ = "Liu, Xindong"
__version__ = "2025.6.24"  # alpha

from .utils import chunk_spatial
from .data import AnnDataPreparer, downsample_cells, compare_umap
from .classifier import (
    SVM,
    # GaussianNaiveBayes,
    # QProximityClassifier,
    # CosineSimilarityClassifier,
    # JaccardClassifier,
)
from .spatial import (
    rw_aggregate,
    rw_aggregate_sequential,
    extract_celltypes_full,
    extract_cell_sizes_full,
    cluster_spatial_domain,
    spatial_distances,
    SpatialTypeAnnCntMtx,
    celltype_refined_bin,
    ctrbin_cellseg,
    ctrbin_cellseg_parallel,
    SpTypeSizeAnnCntMtx,
    aggregate_spots_to_cells,
    aggregate_spots_to_cells_parallel,
)
from .plot import (
    SpAnnPoints,
    get_boundaries,
    plot_boundaries,
    plot_boundaries_on_grids,
)

# TODO: Add recipe module for user-friendliness
