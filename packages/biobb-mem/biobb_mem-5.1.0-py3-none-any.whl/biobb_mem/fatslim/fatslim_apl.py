#!/usr/bin/env python3

"""Module containing the FATSLiM Area per Lipid class and the command line interface."""
import argparse
from pathlib import PurePath
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import settings
from biobb_common.tools.file_utils import launchlogger
from biobb_common.tools import file_utils as fu
import MDAnalysis as mda
from biobb_mem.fatslim.common import calculate_box
import shutil


class FatslimAPL(BiobbObject):
    """
    | biobb_mem FatslimAPL
    | Wrapper of the `FATSLiM area per lipid <https://pythonhosted.org/fatslim/documentation/apl.html>`_ module for area per lipid calculation.
    | FATSLiM is designed to provide efficient and robust analysis of physical parameters from MD trajectories, with a focus on processing large trajectory files quickly.

    Args:
        input_top_path (str): Path to the input topology file. File type: input. `Sample file <https://github.com/bioexcel/biobb_mem/raw/main/biobb_mem/test/data/A01JD/A01JD.pdb>`_. Accepted formats: tpr (edam:format_2333), gro (edam:format_2033), g96 (edam:format_2033), pdb (edam:format_1476), brk (edam:format_2033), ent (edam:format_1476).
        input_traj_path (str) (Optional): Path to the GROMACS trajectory file. File type: input. `Sample file <https://github.com/bioexcel/biobb_mem/raw/main/biobb_mem/test/data/A01JD/A01JD.xtc>`_. Accepted formats: xtc (edam:format_3875), trr (edam:format_3910), cpt (edam:format_2333), gro (edam:format_2033), g96 (edam:format_2033), pdb (edam:format_1476), tng (edam:format_3876).
        input_ndx_path (str) (Optional): Path to the input index NDX file for lipid headgroups and the interacting group. File type: input. `Sample file <https://github.com/bioexcel/biobb_mem/raw/main/biobb_mem/test/data/A01JD/headgroups.ndx>`_. Accepted formats: ndx (edam:format_2033).
        output_csv_path (str): Path to the output CSV file. File type: output. `Sample file <https://github.com/bioexcel/biobb_mem/raw/main/biobb_mem/test/reference/fatslim/apl.ndx>`_. Accepted formats: csv (edam:format_3752).
        properties (dic - Python dictionary object containing the tool parameters, not input/output files):
            * **lipid_selection** (*str*) - ("not protein and element P") Headgroups MDAnalysis `selection <https://docs.mdanalysis.org/stable/documentation_pages/selections.html>`_.
            * **protein_selection** (*str*) - ("protein and not element H") Protein selection interacting with the membrane.
            * **cutoff** (*float*) - (3) This option allows user to specify the cutoff distance (in nm) to be used when performing the neighbor search needed by the APL calculation algorithm
            * **limit** (*float*) - (10) This option allows user to specify the upper limit (in nm2) for a valid area per lipid value.
            * **begin_frame** (*int*) - (-1) First frame index to be used for analysis.
            * **end_frame** (*int*) - (-1) Last frame index to be used for analysis.
            * **ignore_no_box** (*bool*) - (False) Ignore the absence of box information in the topology. If the topology does not contain box information, the box will be set to the minimum and maximum positions of the atoms.
            * **return_hydrogen** (*bool*) - (False) Include hydrogen atoms in the output index file.
            * **binary_path** (*str*) - ("fatslim") Path to the fatslim executable binary.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_mem.fatslim.fatslim_apl import fatslim_apl
            prop = {
                'lipid_selection': '(resname DPPC and name P8)',
                'cutoff': 3
            }
            fatslim_apl(input_top_path='/path/to/myTopology.tpr',
                              input_traj_path='/path/to/myTrajectory.xtc',
                              output_csv_path='/path/to/newIndex.ndx',
                              properties=prop)

    Info:
        * wrapped_software:
            * name: FATSLiM
            * version: 0.2.2
            * license: GNU
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(self, input_top_path, output_csv_path, input_traj_path=None, input_ndx_path=None, properties=None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {"input_top_path": input_top_path,
                   "input_traj_path": input_traj_path,
                   "input_ndx_path": input_ndx_path},
            "out": {"output_csv_path": output_csv_path}
        }

        # Properties specific for BB
        self.lipid_selection = properties.get('lipid_selection', "not protein and element P")
        self.protein_selection = properties.get('protein_selection', "protein and not element H")
        self.cutoff = properties.get('cutoff', 3)
        self.limit = properties.get('cutoff', 10)
        self.begin_frame = properties.get('begin_frame', -1)
        self.end_frame = properties.get('end_frame', -1)
        self.ignore_no_box = properties.get('ignore_no_box', False)
        self.binary_path = properties.get('binary_path', 'fatslim')
        self.properties = properties

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`FatslimAPL <fatslim.fatslim_apl.FatslimAPL>` fatslim.fatslim_apl.FatslimAPL object."""

        # Setup Biobb
        if self.check_restart():
            return 0
        self.stage_files()

        # Create index file using MDAnalysis
        u = mda.Universe(topology=self.stage_io_dict["in"]["input_top_path"],
                         coordinates=self.stage_io_dict["in"].get("input_traj_path"))
        if u.dimensions is None:
            # FATSLiM ValueError: Box does not correspond to PBC=xyz
            if self.ignore_no_box:
                calculate_box(u)
            else:
                print('The trajectory does not contain box information. Please set the ignore_no_box property to True to ignore this error.')

        # Build the index to select the atoms from the membrane
        if self.stage_io_dict["in"].get('input_ndx_path', None):
            self.tmp_ndx = self.stage_io_dict["in"]["input_ndx_path"]
        else:
            self.tmp_ndx = str(PurePath(fu.create_unique_dir()).joinpath('apl_inp.ndx'))
            with mda.selections.gromacs.SelectionWriter(self.tmp_ndx, mode='w') as ndx:
                ndx.write(u.select_atoms(self.lipid_selection), name='headgroups')
                ndx.write(u.select_atoms(self.protein_selection), name='protein')

        if self.stage_io_dict["in"]["input_top_path"].endswith('gro'):
            self.cfg = self.stage_io_dict["in"]["input_top_path"]
            self.cmd = []
        else:
            # Convert topology .gro and add box dimensions if not available in the topology
            self.cfg = str(PurePath(fu.create_unique_dir()).joinpath('output.gro'))
            self.tmp_files.extend([PurePath(self.cfg).parent])
            self.cmd = ['gmx', 'editconf',
                        '-f', self.stage_io_dict["in"]["input_top_path"],
                        '-o', self.cfg,
                        '-box', ' '.join(map(str, u.dimensions[:3])), ';',
                        ]
        self.tmp_csv = str(PurePath(self.stage_io_dict["unique_dir"]).joinpath('out.csv'))
        # Build command
        self.cmd.extend([
            self.binary_path, "apl",
            "-n", self.tmp_ndx,
            "-c", self.cfg,
            "--export-apl-raw", self.tmp_csv,
            "--apl-cutoff", str(self.cutoff),
            "--apl-limit", str(self.limit),
            "--begin-frame", str(self.begin_frame),
            "--end-frame", str(self.end_frame)
        ])

        # Run Biobb block
        self.run_biobb()
        shutil.move(self.tmp_csv[:-4]+'_frame_00000.csv', self.stage_io_dict["out"]["output_csv_path"])
        # Copy files to host
        self.copy_to_host()
        # Remove temporary files
        self.tmp_files.extend([
            self.stage_io_dict.get("unique_dir"),
            PurePath(self.tmp_ndx).parent
        ])
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)

        return self.return_code


def fatslim_apl(input_top_path: str, output_csv_path: str, input_traj_path: str = None, input_ndx_path: str = None, properties: dict = None, **kwargs) -> int:
    """Execute the :class:`FatslimAPL <fatslim.fatslim_apl.FatslimAPL>` class and
    execute the :meth:`launch() <fatslim.fatslim_apl.FatslimAPL.launch>` method."""

    return FatslimAPL(input_top_path=input_top_path,
                      input_traj_path=input_traj_path,
                      input_ndx_path=input_ndx_path,
                      output_csv_path=output_csv_path,
                      properties=properties, **kwargs).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description="Calculate the area per lipid.", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_top_path', required=True, help='Path to the input structure or topology file. Accepted formats: ent, gro, pdb, tpr.')
    required_args.add_argument('--output_csv_path', required=True, help='Path to the GROMACS index file. Accepted formats: ndx')
    parser.add_argument('--input_traj_path', required=False, help='Path to the input trajectory to be processed. Accepted formats: gro, pdb, tng, trr, xtc.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    fatslim_apl(input_top_path=args.input_top_path,
                output_csv_path=args.output_csv_path,
                properties=properties)


if __name__ == '__main__':
    main()
