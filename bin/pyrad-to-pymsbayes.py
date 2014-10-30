#! /usr/bin/env python

import os
import sys

from seqsift.utils.pymsbayes_utils import PyMsBayesComparisons

import gekgo_util

_LOG = gekgo_util.RunLogger(name=__file__,
        log_to_stderr=True,
        log_to_file=False)

comparisons = [
        {'caluya': [
                'CDS_590_Gekko_mindorensis_Caluya.trimmed',
                'CDS_591_Gekko_mindorensis_Caluya.trimmed',
                'CDS_607_Gekko_mindorensis_Caluya.trimmed',
                'CDS_609_Gekko_mindorensis_Caluya.trimmed',
                'CDS_610_Gekko_mindorensis_Caluya.trimmed',
                ],
         'camiguin_sur': [
                'CDS_99_Gekko_mindorensis_CamiguinSur.trimmed',
                'CDS_100_Gekko_mindorensis_CamiguinSur.trimmed',
                'CDS_101_Gekko_mindorensis_CamiguinSur.trimmed',
                'CDS_102_Gekko_mindorensis_CamiguinSur.trimmed',
                ],
         },
        {'lubang': [
                'CDS_3866_Gekko_mindorensis_Lubang.trimmed',
                'CDS_3867_Gekko_mindorensis_Lubang.trimmed',
                'CDS_3868_Gekko_mindorensis_Lubang.trimmed',
                'CDS_3894_Gekko_mindorensis_Lubang.trimmed',
                'CDS_3895_Gekko_mindorensis_Lubang.trimmed',
                'CDS_3935_Gekko_mindorensis_Lubang.trimmed',
                'CDS_3936_Gekko_mindorensis_Lubang.trimmed',
                ],
         'mindoro_n': [
                'ELR_911_Gekko_mindorensis_Mindoro.trimmed',
                'ELR_1013_Gekko_mindorensis_Mindoro.trimmed',
                'ELR_1006_Gekko_mindorensis_Mindoro.trimmed',
                'ELR_1007_Gekko_mindorensis_Mindoro.trimmed',
                'ELR_1008_Gekko_mindorensis_Mindoro.trimmed',
                'ELR_1009_Gekko_mindorensis_Mindoro.trimmed',
                'ELR_1010_Gekko_mindorensis_Mindoro.trimmed',
                ],
         },
        {'maestre_de_campo': [
                'CDS_1459_Gekko_mindorensis_MaestreDeCampo.trimmed',
                'CDS_1461_Gekko_mindorensis_MaestreDeCampo.trimmed',
                'CDS_1462_Gekko_mindorensis_MaestreDeCampo.trimmed',
                'CDS_1463_Gekko_mindorensis_MaestreDeCampo.trimmed',
                ],
         'mindoro_s': [
                'CDS_1229_Gekko_mindorensis_Mindoro.trimmed',
                'CDS_1230_Gekko_mindorensis_Mindoro.trimmed',
                'CDS_1231_Gekko_mindorensis_Mindoro.trimmed',
                'RMB_4981_Gekko_mindorensis_Mindoro.trimmed',
                'RMB_4982_Gekko_mindorensis_Mindoro.trimmed',
                'RMB_5005_Gekko_mindorensis_Mindoro.trimmed',
                'RMB_5006_Gekko_mindorensis_Mindoro.trimmed',
                ],
         },
        {'masbate': [
                'CDS_754_Gekko_mindorensis_Masbate.trimmed',
                'CDS_755_Gekko_mindorensis_Masbate.trimmed',
                'CDS_757_Gekko_mindorensis_Masbate.trimmed',
                'CDS_758_Gekko_mindorensis_Masbate.trimmed',
                ],
         'panay_ne': [
                'CDS_63_Gekko_mindorensis_Panay.trimmed',
                'CDS_64_Gekko_mindorensis_Panay.trimmed',
                'CDS_65_Gekko_mindorensis_Panay.trimmed',
                'CDS_66_Gekko_mindorensis_Panay.trimmed',
                ],
         },
        {'negros': [
                'CDS_277_Gekko_mindorensis_Negros.trimmed',
                'CDS_278_Gekko_mindorensis_Negros.trimmed',
                'CDS_279_Gekko_mindorensis_Negros.trimmed',
                'CDSGS_39_Gekko_mindorensis_Negros.trimmed',
                'CDSGS_40_Gekko_mindorensis_Negros.trimmed',
                'CDSGS_41_Gekko_mindorensis_Negros.trimmed',
                ],
         'panay_sw': [
                'RMB_6425_Gekko_mindorensis_Panay.trimmed',
                'RMB_6429_Gekko_mindorensis_Panay.trimmed',
                'RMB_6430_Gekko_mindorensis_Panay.trimmed',
                'RMB_6431_Gekko_mindorensis_Panay.trimmed',
                'RMB_6448_Gekko_mindorensis_Panay.trimmed',
                'RMB_6449_Gekko_mindorensis_Panay.trimmed',
                'RMB_6479_Gekko_mindorensis_Panay.trimmed',
                ],
         },
        ]

def main():
    for d in [gekgo_util.PYMSBAYES_DIR, gekgo_util.PYMSBAYES_GM_DIR,
            gekgo_util.PYMSBAYES_GM_FASTA_DIR,
            gekgo_util.PYMSBAYES_GM_CONFIG_DIR]:
        if not os.path.isdir(d):
            os.mkdir(d)
    loci_file_path = os.path.join(gekgo_util.MSG_ASSEMBLY_DIR, 'outfiles',
            'd6q4c088s5h01.loci')
    nloci = PyMsBayesComparisons.process_loci_file(
            loci_file_obj = loci_file_path,
            pop_id_maps = comparisons,
            fasta_out_dir = gekgo_util.PYMSBAYES_GM_FASTA_DIR,
            config_out_dir = gekgo_util.PYMSBAYES_GM_CONFIG_DIR,
            minimum_sample_size = 3,
            minimum_alignment_length = 80,
            max_ambiguities_per_seq = 0.2,
            estimate_hky_parameters = False,
            require_shared_loci = True)

if __name__ == '__main__':
    main()


