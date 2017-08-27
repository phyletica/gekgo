#! /usr/bin/env python

import os
import sys
import shutil
import re
import glob

def main():
    pop_file_option_pattern = re.compile(r"^\s+##\s*\[28\].*$")
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
        branch_name = branch_name.replace(".", "_")
        params_path = os.path.join(os.curdir, "params-{0}.txt".format(branch_name))
        tmp_params_path = "tmp-" + params_path
        if not os.path.exists(params_path):
            sys.stderr.out("WARNING: {0!r} does not exist... skipping!\n".format(params_path))
            continue
        with open(tmp_params_path, "w") as out:
            with open(params_path, "r") as stream:
                for line in stream:
                    if pop_file_option_pattern.match(line):
                        out.write("{0} ## [28] [pop_assign_file]: Path to population assignment file\n".format(
                                os.path.join(os.curdir, path)))
                    else:
                        out.write(line)
        shutil.move(tmp_params_path, params_path)

if __name__ == '__main__':
    main()

