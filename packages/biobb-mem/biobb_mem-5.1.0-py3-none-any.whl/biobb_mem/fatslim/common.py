from MDAnalysis.transformations.boxdimensions import set_dimensions


def calculate_box(u):
    print('Setting box dimensions using the minimum and maximum positions of the atoms.')
    # Calculate the dimensions of the box
    positions = u.atoms.positions
    box_dimensions = positions.max(axis=0) - positions.min(axis=0)
    u.trajectory.add_transformations(set_dimensions([*box_dimensions, 90, 90, 90]))
