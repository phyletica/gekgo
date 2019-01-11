#! /usr/bin/env python

import os
import sys
import re
from seqsift.utils import dataio
from seqsift.utils import alphabets
from seqsift.seqops import seqstats

import gekgo_util

def get_pop_gen_stats(path,
        pop_label_is_prefix = False,
        pop_label_delimiter = "_",
        per_site = True,
        ignore_gaps = False,
        data_format = "nexus",
        data_type = "dna",
        character_alphabet = None):
    seqs = dataio.get_seq_iter([path],
            format = data_format,
            data_type = data_type)
    label_to_seqs = {}
    labels = []
    for s in seqs:
        if pop_label_is_prefix:
            label = s.id.split(pop_label_delimiter)[0]
        else:
            label = s.id.split(pop_label_delimiter)[-1]
        if label in label_to_seqs:
            label_to_seqs[label].append(s)
        else:
            # sys.stderr.write("Found pop label {0} in {1}\n".format(label, path))
            label_to_seqs[label] = [s]
            labels.append(label)
        if len(label_to_seqs) > 2:
            raise Exception("Too many pop labels found: {0}".format(
                    ", ".join(label_to_seqs.keys())))

    if not character_alphabet:
        character_alphabet = alphabets.DnaAlphabet()
    sequences_1 = label_to_seqs[labels[0]]
    sequences_2 = label_to_seqs[labels[1]]
    sum_stats = seqstats.get_population_pair_diversity_summary(
            seq_iter1 = sequences_1,
            seq_iter2 = sequences_2,
            per_site = per_site,
            aligned = True,
            ignore_gaps = ignore_gaps,
            alphabet = character_alphabet)
    sum_stats["sample_size_1"] = len(sequences_1)
    sum_stats["sample_size_2"] = len(sequences_2)
    return labels, sum_stats


class LabelParser(object):
    name_str = "^(?P<genus>[CG])-(?P<epithet1>[A-Za-z_]+)-(?P<epithet2>[A-Za-z_]+)-(?P<island1>[A-Za-z_]+)-(?P<island2>[A-Za-z_]+)\.nex$"
    name_pattern = re.compile(name_str)
    
    def parse_label(self, alignment_path):
        m = self.name_pattern.match(os.path.basename(alignment_path))
        if not m:
            raise Exception("Could not parse name from alignment path {0}".format(alignment_path))
        d = m.groupdict()
        d["pretty_epithet1"] = self.format_epithet(d["epithet1"])
        d["pretty_epithet2"] = self.format_epithet(d["epithet2"])
        if d["epithet1"] == d["epithet2"]:
            label = "\\textit{{{genus}.\\ {pretty_epithet1}}}".format(**d)
        else:
            label = "\\textit{{{genus}.\\ {pretty_epithet1}-{pretty_epithet2}}}".format(**d)
        d["pretty_island1"] = self.format_camel_case(d["island1"])
        d["pretty_island2"] = self.format_camel_case(d["island2"])
        return label, d

    def format_camel_case(self, string):
        return " ".join(re.findall("[A-Z][^A-Z]*", string))

    def format_epithet(self, string):
        return string.replace("_", ".\ ")


def main():
    alignment_names = [
            "C-annulatus-annulatus-Bohol-CamiguinSur.nex",
            "C-baluensis-redimiculus-Kinabalu-Palawan.nex",
            "C-gubaot-sumuroi-Leyte-Samar.nex",
            "C-philippinicus-philippinicus-BabuyanClaro-Luzon.nex",
            "C-philippinicus-philippinicus-CamiguinNorte-Luzon.nex",
            "C-philippinicus-philippinicus-Luzon-Polillo.nex",
            "C-philippinicus-philippinicus-Negros-Panay.nex",
            "C-philippinicus-philippinicus-Sibuyan-Tablas.nex",
            "G-crombota-rossi-BabuyanClaro-Calayan.nex",
            "G-gigante-gigante-NorthGigante-SouthGigante.nex",
            "G-mindorensis-mindorensis-Lubang-Luzon.nex",
            "G-mindorensis-mindorensis-Masbate-Panay.nex",
            "G-mindorensis-mindorensis-Negros-Panay.nex",
            "G-porosus-porosus-Batan-Sabtang.nex",
            "G-romblon-romblon-Romblon-Tablas.nex",
            "G-sp_a-sp_b-Dalupiri-CamiguinNorte.nex",
            ]
    alignment_paths = []
    for n in alignment_names:
        alignment_paths.append(os.path.join(gekgo_util.ECOEVOLITY_ALIGNMENT_DIR, n))

    label_resolver = LabelParser()
    sys.stdout.write("Species & Island 1 & Island 2 & $\\pi_1$ & $\\pi_2$ & $\\pi_{between}$ \\\\\n\\hline\n")
    sys.stdout.flush()
    for path in alignment_paths:
        species, label_dict = label_resolver.parse_label(path)
        islands, sum_stats = get_pop_gen_stats(path)
        if islands[0].startswith(label_dict["island1"]):
            isl_1 = "island1"
            isl_2 = "island2"
        elif islands[0].startswith(label_dict["island2"]):
            isl_1 = "island2"
            isl_2 = "island1"
        else:
            raise Exception("Problem with island name {0}".format(islands[0]))
        sys.stdout.write("{species} & {island_1} & {island_2} & {pi_1:.5f} ({ss_1}) & {pi_2:.5f} ({ss_2}) & {pi_between:.5f} \\\\\n".format(
                species = species,
                island_1 = label_dict["pretty_" + isl_1],
                island_2 = label_dict["pretty_" + isl_2],
                pi_1 = sum_stats["pi_1"],
                ss_1 = sum_stats["sample_size_1"],
                pi_2 = sum_stats["pi_2"],
                ss_2 = sum_stats["sample_size_2"],
                pi_between = sum_stats["pi_between"],
                ))
        sys.stdout.flush()
    sys.stdout.write("\\hline\n")


if __name__ == "__main__":
    main()
