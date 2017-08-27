#! /usr/bin/env python

import os
import sys
import re
import glob

def get_pbs_header(ppn = 1, hours = 1, restrict_nodes = False):
    reservation = ""
    if restrict_nodes:
        reservation = "#PBS -l jobflags=ADVRES:jro0014_lab.56281"
    return """#! /bin/sh
#PBS -l nodes=1:ppn={0}
#PBS -l walltime={1}:00:00
#PBS -j oe
{2}

if [ -n \"$PBS_JOBNAME\" ]
then
    source \"${{PBS_O_HOME}}/.bash_profile\"
    cd \"$PBS_O_WORKDIR\"
    condaenv on
    condaenv
fi
""".format(ppn, hours, reservation)

def main():
    ppn = 10
    hours = 50
    pair_file_pattern = re.compile(r"^samples-(?P<genus>[a-zA-Z]+)-(?P<sp1>[a-z\.]+)-(?P<sp2>[a-z\.]+)-(?P<isl1>[a-zA-Z]+)-(?P<isl2>[a-zA-Z]+)\.txt$")
    pair_paths = glob.glob(os.path.join("samples-[CG]*.txt"))
    for path in pair_paths:
        m = pair_file_pattern.match(path)
        if not m:
            sys.stderr.write("WARNING: odd file {0!r}... skipping!\n".format(
                    path))
            continue
        d = m.groupdict()
        d["g"] = d["genus"][0]
        branch_name = "{g}-{sp1}-{sp2}-{isl1}-{isl2}".format(**d)
        sh_branch_path = "ipyrad-branch-{0}.sh".format(branch_name)
        sh_branch_out_path = sh_branch_path + ".out"
        cmd = "ipyrad -p \"params-plates123.txt\" -b \"{branch_name}\" \"{pair_path}\" 1>\"{out_path}\" 2>&1".format(
                branch_name = branch_name,
                pair_path = path,
                out_path = sh_branch_out_path)
        with open(sh_branch_path, "w") as out:
            out.write("{0}\n".format(get_pbs_header()))
            out.write("{0}\n".format(cmd))

        sh_assemble_path = "ipyrad-steps67-{0}.sh".format(branch_name)
        sh_assemble_out_path = sh_assemble_path + ".out"
        cmd = "ipyrad -p \"params-{branch_name}.txt\" -s 67 -c {ppn} 1>\"{out_path}\" 2>&1".format(
                branch_name = branch_name,
                ppn = ppn,
                out_path = sh_assemble_out_path)
        with open(sh_assemble_path, "w") as out:
            out.write("{0}\n".format(get_pbs_header(
                    ppn = ppn,
                    hours = hours,
                    restrict_nodes = True)))
            out.write("{0}\n".format(cmd))

if __name__ == '__main__':
    main()

