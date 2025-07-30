#!/usr/bin/env python3

"""Module containing the GROMACS order class and the command line interface."""
import argparse
from pathlib import PurePath
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import settings
from biobb_common.tools.file_utils import launchlogger


class GMXOrder(BiobbObject):
    """
    | biobb_mem GMXOrder
    | Wrapper of the GROMACS order module for computing lipid order parameters per atom for carbon tails.
    | `GROMCAS order <https://manual.gromacs.org/current/onlinehelp/gmx-order.html>`_ only works for saturated carbons and united atom force fields.

    Args:
        input_top_path (str): Path to the input structure or topology file. File type: input. `Sample file <https://github.com/bioexcel/biobb_mem/raw/main/biobb_mem/test/data/ambertools/topology.tpr>`_. Accepted formats: tpr (edam:format_2333).
        input_traj_path (str): Path to the input trajectory to be processed. File type: input. `Sample file <https://github.com/bioexcel/biobb_mem/raw/main/biobb_mem/test/data/ambertools/trajectory.xtc>`_. Accepted formats: xtc (edam:format_3875), trr (edam:format_3910), cpt (edam:format_2333), gro (edam:format_2033), g96 (edam:format_2033), pdb (edam:format_1476), tng (edam:format_3876)..
        input_index_path (str): Path to the GROMACS index file. File type: input. `Sample file <https://github.com/bioexcel/biobb_mem/raw/main/biobb_mem/test/data/       >`_. Accepted formats: ndx (edam:format_2033).
        output_deuter_path (str): Path to deuterium order parameters xvgr/xmgr file. File type: output. `Sample file <https://github.com/bioexcel/biobb_mem/raw/main/biobb_mem/test/data/gromacs/deuter.xvg>`_. Accepted formats: xvg (edam:format_2330).
        output_order_path (str) (Optional): Path to order tensor diagonal elements xvgr/xmgr file. File type: output. `Sample file <https://github.com/bioexcel/biobb_mem/raw/main/biobb_mem/test/data/gromacs/order.xvg>`_. Accepted formats: xvg (edam:format_2330).
        properties (dic - Python dictionary object containing the tool parameters, not input/output files):
            * **d** (*str*) - ("z") Direction of the normal on the membrane: z, x, y.
            * **binary_path** (*str*) - ("cpptraj") Path to the cpptraj executable binary.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_mem.ambertools.gmx_order import gmx_order
            prop = {
                'd': 'z'
            }
            gmx_order(input_top_path='/path/to/myTopology.top',
                      input_traj_path='/path/to/myTrajectory.xtc',
                      output_deuter_path='/path/to/deuterAnalysis.xvg',
                      output_order_path='/path/to/orderAnalysis.xvg',
                      properties=prop)

    Info:
        * wrapped_software:
            * name: GROMACS order
            * version: 2024.2
            * license: LGPL 2.1
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(self, input_top_path, input_traj_path, input_index_path=None,
                 output_deuter_path=None, output_order_path=None, properties=None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {
                "input_top_path": input_top_path,
                "input_traj_path": input_traj_path,
                "input_index_path": input_index_path
            },
            "out": {
                "output_deuter_path": output_deuter_path,
                "output_order_path": output_order_path
            }
        }

        # Properties specific for BB
        self.d = properties.get('d', 'z')
        self.binary_path = properties.get('binary_path', 'gmx')
        self.properties = properties

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`GMXOrder <gromacs.gmx_order.GMXOrder>` gromacs.gmx_order.GMXOrder object."""

        # Setup Biobb
        if self.check_restart():
            return 0
        self.stage_files()

        # Create cmd and launch execution
        cmd = [self.binary_path, 'order',
               '-s', self.stage_io_dict["in"]["input_top_path"],
               '-f', self.stage_io_dict["in"]["input_traj_path"],
               '-n', self.stage_io_dict["in"]["input_index_path"],
               '-od', self.stage_io_dict["out"]["output_deuter_path"],
               '-d', self.d]

        if self.stage_io_dict["out"].get("output_order_path"):
            cmd.extend(['-o', self.stage_io_dict["out"]["output_order_path"]])
        else:
            cmd.extend(['-o', str(PurePath(self.stage_io_dict["unique_dir"]).joinpath('order.xvg'))])

        self.cmd = cmd

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # Remove temporary folder(s)
        self.tmp_files.append(self.stage_io_dict.get("unique_dir"))

        self.remove_tmp_files()

        return self.return_code


def gmx_order(input_top_path: str, input_traj_path: str, input_index_path: str = None,
              output_deuter_path: str = None, output_order_path: str = None,
              properties: dict = None, **kwargs) -> int:
    """Create :class:`GMXOrder <gromacs.gmx_order.GMXOrder>` class and
    execute :meth:`launch() <gromacs.gmx_order.GMXOrder.launch>` method"""

    return GMXOrder(input_top_path=input_top_path,
                    input_traj_path=input_traj_path,
                    input_index_path=input_index_path,
                    output_deuter_path=output_deuter_path,
                    output_order_path=output_order_path,
                    properties=properties, **kwargs).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description="Compute lipid order parameters using GROMACS order tool.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_top_path', required=True, help='Path to the input structure or topology file.')
    required_args.add_argument('--input_traj_path', required=True, help='Path to the input trajectory to be processed.')
    parser.add_argument('--input_index_path', required=False, help='Path to the GROMACS index file.')
    parser.add_argument('--output_deuter_path', required=False, help='Path to deuterium order parameters output file.')
    parser.add_argument('--output_order_path', required=False, help='Path to order tensor diagonal elements output file.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    gmx_order(input_top_path=args.input_top_path,
              input_traj_path=args.input_traj_path,
              input_index_path=args.input_index_path,
              output_deuter_path=args.output_deuter_path,
              output_order_path=args.output_order_path,
              properties=properties)


if __name__ == '__main__':
    main()
