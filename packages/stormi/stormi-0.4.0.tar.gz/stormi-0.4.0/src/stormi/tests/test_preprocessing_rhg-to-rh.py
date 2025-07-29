import numpy as np

from stormi.preprocessing import rhg_to_rh_indexing

# Test data
region_tf_gene_triplets = [
    [1, 3000, 1803],
    [1, 3027, 1803],
    [1, 3127, 1803],
    [10, 3000, 55],
    [63, 3000, 2500],
    [22239, 3298, 235],
    # [22239,  3198,   235], # Test ValueError. Entry doesn't map to region_tf_pairs
    [43689, 3298, 3085],
    [43689, 3298, 1660],
    [49982, 3299, 1000],
    [49999, 3299, 2000],
]

region_tf_pairs = [
    [1, 3000],
    [10, 3000],
    [63, 3000],
    [1, 3027],
    [1, 3127],
    [22239, 3298],
    [32434, 3298],
    [43689, 3298],
    [49982, 3299],
    [49998, 3299],
    [49999, 3299],
]

# Apply function to retrieve indices for enries of region_tf_gene_triplets in region_tf_pairs
region_tf_indices = rhg_to_rh_indexing(region_tf_gene_triplets, region_tf_pairs)

# Indexing region_tf_pairs with region_tf_indices should retrieve [R, H] pairs in the same order as region_tf_gene_triplets
region_tf_gene_triplets = np.array(region_tf_gene_triplets)
region_tf_pairs = np.array(region_tf_pairs)
#
assert (region_tf_pairs[region_tf_indices, :] == region_tf_gene_triplets[:, :2]).all()
