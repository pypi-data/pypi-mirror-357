""" Common functions for package biobb_mem.lipyphilic_biobb """
import numpy as np
from MDAnalysis.transformations.boxdimensions import set_dimensions


def calculate_box(u):
    print('Warning: trajectory probably has no box variable. Setting dimensions using the minimum and maximum positions of the atoms.')
    # Initialize min and max positions with extreme values
    min_pos = np.full(3, np.inf)
    max_pos = np.full(3, -np.inf)

    # Iterate over all frames to find the overall min and max positions
    for ts in u.trajectory:
        positions = u.atoms.positions
        min_pos = np.minimum(min_pos, positions.min())
        max_pos = np.maximum(max_pos, positions.max())

    # Calculate the dimensions of the box
    box_dimensions = max_pos - min_pos
    u.trajectory.add_transformations(set_dimensions([*box_dimensions, 90, 90, 90]))
