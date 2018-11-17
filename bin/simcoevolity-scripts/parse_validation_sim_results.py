#! /usr/bin/env python

import sys
import os
import re
import math
import logging
import glob
import argparse

import pycoevolity

sys.path.append("../")
import gekgo_util

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
_LOG = logging.getLogger(os.path.basename(__file__))


def line_count(path):
    count = 0
    with open(path) as stream:
        for line in stream:
            count += 1
    return count

def get_parameter_names(number_of_comparisons, dpp = True):
    p = ["ln_likelihood"]
    if dpp:
        p.append("concentration")
    else:
        p.append("split_weight")
    p.append("number_of_events")
    for i in range(number_of_comparisons):
        p.append("ln_likelihood_c{0}sp1".format(i + 1))
        p.append("root_height_c{0}sp1".format(i + 1))
        p.append("mutation_rate_c{0}sp1".format(i + 1))
        p.append("freq_1_c{0}sp1".format(i + 1))
        p.append("pop_size_c{0}sp1".format(i + 1))
        p.append("pop_size_c{0}sp2".format(i + 1))
        p.append("pop_size_root_c{0}sp1".format(i + 1))
    return p

def get_results_header(number_of_comparisons, dpp = True):
    h = [
            "batch",
            "sim",
            "sample_size",
            "mean_run_time",
            "mean_n_var_sites",
            "true_model",
            "map_model",
            "true_model_cred_level",
            "map_model_p",
            "true_model_p",
            "true_num_events",
            "map_num_events",
            "true_num_events_cred_level",
        ]

    for i in range(number_of_comparisons):
        h.append("num_events_{0}_p".format(i+1))

    for i in range(number_of_comparisons):
        h.append("n_var_sites_c{0}".format(i+1))

    for p in get_parameter_names(number_of_comparisons, dpp = dpp):
        h.append("true_{0}".format(p))
        h.append("true_{0}_rank".format(p))
        h.append("mean_{0}".format(p))
        h.append("median_{0}".format(p))
        h.append("stddev_{0}".format(p))
        h.append("hpdi_95_lower_{0}".format(p))
        h.append("hpdi_95_upper_{0}".format(p))
        h.append("eti_95_lower_{0}".format(p))
        h.append("eti_95_upper_{0}".format(p))
        h.append("ess_{0}".format(p))
        h.append("ess_sum_{0}".format(p))
        h.append("psrf_{0}".format(p))
    return h

def get_empty_results_dict(number_of_comparisons, dpp = True):
    h = get_results_header(number_of_comparisons, dpp = dpp)
    return dict(zip(h, ([] for i in range(len(h)))))

def get_results_from_sim_rep(
        posterior_paths,
        stdout_paths,
        true_path,
        parameter_names,
        number_of_comparisons,
        batch_number,
        sim_number,
        expected_number_of_samples = 1501,
        burnin = 301):
    posterior_paths = sorted(posterior_paths)
    stdout_paths = sorted(stdout_paths)
    nchains = len(posterior_paths)
    assert(nchains == len(stdout_paths))
    if nchains > 1:
        lc = line_count(posterior_paths[0])
        for i in range(1, nchains):
            assert(lc == line_count(posterior_paths[i]))

    results = {}
    post_sample = pycoevolity.posterior.PosteriorSample(
            posterior_paths,
            burnin = burnin)
    nsamples_per_chain = expected_number_of_samples - burnin
    assert(post_sample.number_of_samples == nchains * nsamples_per_chain)

    true_values = pycoevolity.parsing.get_dict_from_spreadsheets(
            [true_path],
            sep = "\t",
            header = None)
    for v in true_values.values():
        assert(len(v) == 1)

    results["batch"] = batch_number
    results["sim"] = sim_number
    results["sample_size"] = post_sample.number_of_samples

    stdout = pycoevolity.parsing.EcoevolityStdOut(stdout_paths[0])
    assert(number_of_comparisons == stdout.number_of_comparisons)
    results["mean_n_var_sites"] = stdout.get_mean_number_of_variable_sites()
    for i in range(number_of_comparisons):
        results["n_var_sites_c{0}".format(i + 1)] = stdout.get_number_of_variable_sites(i)
    run_times = [stdout.run_time]
    for i in range(1, len(stdout_paths)):
        so = pycoevolity.parsing.EcoevolityStdOut(stdout_paths[i])
        run_times.append(so.run_time)
        for j in range(number_of_comparisons):
            assert(results["n_var_sites_c{0}".format(j + 1)] == so.get_number_of_variable_sites(j))
    results["mean_run_time"] = sum(run_times) / float(len(run_times))
    
    true_model = tuple(int(true_values[h][0]) for h in post_sample.height_index_keys)
    true_model_p = post_sample.get_model_probability(true_model)
    true_model_cred = post_sample.get_model_credibility_level(true_model)
    map_models = post_sample.get_map_models()
    map_model = map_models[0]
    if len(map_models) > 1:
        if true_model in map_models:
            map_model = true_model
    map_model_p = post_sample.get_model_probability(map_model)
    results["true_model"] = "".join((str(i) for i in true_model))
    results["map_model"] = "".join((str(i) for i in map_model))
    results["true_model_cred_level"] = true_model_cred
    results["map_model_p"] = map_model_p
    results["true_model_p"] = true_model_p
    
    true_nevents = int(true_values["number_of_events"][0])
    true_nevents_p = post_sample.get_number_of_events_probability(true_nevents)
    true_nevents_cred = post_sample.get_number_of_events_credibility_level(true_nevents)
    map_numbers_of_events = post_sample.get_map_numbers_of_events()
    map_nevents = map_numbers_of_events[0]
    if len(map_numbers_of_events) > 1:
        if true_nevents in map_numbers_of_events:
            map_nevents = true_nevents
    results["true_num_events"] = true_nevents
    results["map_num_events"] = map_nevents
    results["true_num_events_cred_level"] = true_nevents_cred
    for i in range(number_of_comparisons):
        results["num_events_{0}_p".format(i + 1)] = post_sample.get_number_of_events_probability(i + 1)
    
    for p in parameter_names:
        true_val = float(true_values[p][0])
        true_val_rank = post_sample.get_rank(p, true_val)
        ss = pycoevolity.stats.get_summary(post_sample.parameter_samples[p])
        ess = pycoevolity.stats.effective_sample_size(
                post_sample.parameter_samples[p])
        ess_sum = 0.0
        samples_by_chain = []
        for i in range(nchains):
            chain_samples = post_sample.parameter_samples[p][i * nsamples_per_chain : (i + 1) * nsamples_per_chain]
            assert(len(chain_samples) == nsamples_per_chain)
            ess_sum += pycoevolity.stats.effective_sample_size(chain_samples)
            if nchains > 1:
                samples_by_chain.append(chain_samples)
        psrf = -1.0
        if nchains > 1:
            psrf = pycoevolity.stats.potential_scale_reduction_factor(samples_by_chain)
        results["true_{0}".format(p)] = true_val
        results["true_{0}_rank".format(p)] = true_val_rank
        results["mean_{0}".format(p)] = ss["mean"]
        results["median_{0}".format(p)] = ss["median"]
        results["stddev_{0}".format(p)] = math.sqrt(ss["variance"])
        results["hpdi_95_lower_{0}".format(p)] = ss["hpdi_95"][0]
        results["hpdi_95_upper_{0}".format(p)] = ss["hpdi_95"][1]
        results["eti_95_lower_{0}".format(p)] = ss["qi_95"][0]
        results["eti_95_upper_{0}".format(p)] = ss["qi_95"][1]
        results["ess_{0}".format(p)] = ess
        results["ess_sum_{0}".format(p)] = ess_sum
        results["psrf_{0}".format(p)] = psrf

    return results

def parse_simulation_results(
        expected_number_of_runs = 4,
        expected_number_of_samples = 1501,
        burnin = 501):
    batch_number_pattern = re.compile(r'batch(?P<batch_number>\d+)')
    sim_number_pattern = re.compile(r'-sim-(?P<sim_number>\d+)-')
    val_sim_dirs = glob.glob(os.path.join(gekgo_util.ECOEVOLITY_SIM_DIR, '*'))
    for val_sim_dir in sorted(val_sim_dirs):
        dpp = True
        sim_name = os.path.basename(val_sim_dir)
        number_of_comparisons = 8
        parameter_names = get_parameter_names(number_of_comparisons, dpp = dpp)
        header = get_results_header(number_of_comparisons, dpp = dpp)

        batch_dirs = glob.glob(os.path.join(val_sim_dir, "batch*"))
        for batch_dir in sorted(batch_dirs):
            batch_number_matches = batch_number_pattern.findall(batch_dir)
            assert(len(batch_number_matches) == 1)
            batch_number_str = batch_number_matches[0]
            batch_number = int(batch_number_str)

            results_path = os.path.join(batch_dir, "results.csv")
            if (os.path.exists(results_path) or
                    (os.path.exists(results_path + ".gz"))):
                _LOG.warning("WARNING: Results path {0} already exists; skipping!".format(
                        results_path))
                continue

            results = get_empty_results_dict(number_of_comparisons, dpp = dpp)

            posterior_paths = glob.glob(os.path.join(batch_dir,
                    "run-1-simcoevolity-sim-*-config-state-run-1.log*"))
            for posterior_path in sorted(posterior_paths):
                sim_number_matches = sim_number_pattern.findall(posterior_path)
                assert(len(sim_number_matches) == 1)
                sim_number_str = sim_number_matches[0]
                sim_number = int(sim_number_str)
                sys.stdout.write("Parsing {0} batch {1} sim {2}...\n".format(
                        sim_name,
                        batch_number_str,
                        sim_number_str))
                post_paths = glob.glob(os.path.join(batch_dir,
                        "run-*-simcoevolity-sim-{0}-config-state-run-1.log*".format(
                                sim_number_str)))
                assert (len(post_paths) == expected_number_of_runs), (
                        "Found {0} state logs for {1}".format(
                                len(post_paths), posterior_path))
                true_paths = glob.glob(os.path.join(batch_dir,
                        "simcoevolity-sim-{0}-true-values.txt*".format(
                                sim_number_str)))
                assert(len(true_paths) == 1)
                true_path = true_paths[0]
                assert(os.path.exists(true_path))
                stdout_paths = glob.glob(os.path.join(batch_dir,
                        "run-*-simcoevolity-sim-{0}-config.yml.out*".format(
                                sim_number_str)))
                assert(len(stdout_paths) == expected_number_of_runs)
                rep_results = get_results_from_sim_rep(
                        posterior_paths = post_paths,
                        stdout_paths = stdout_paths,
                        true_path = true_path,
                        parameter_names = parameter_names,
                        number_of_comparisons = number_of_comparisons,
                        batch_number = batch_number,
                        sim_number = sim_number,
                        expected_number_of_samples = expected_number_of_samples,
                        burnin = burnin)
                for k, v in rep_results.items():
                    results[k].append(v)

            assert(not os.path.exists(results_path))
            with open(results_path, 'w') as out:
                for line in pycoevolity.parsing.dict_line_iter(
                        results,
                        sep = '\t',
                        header = header):
                    out.write(line)

def main_cli(argv = sys.argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--expected-number-of-runs',
            action = 'store',
            type = int,
            default = 4,
            help = 'Number of MCMC chains that were run for each sim rep.')
    parser.add_argument('-s', '--expected-number-of-samples',
            action = 'store',
            type = int,
            default = 1501,
            help = ('Number of MCMC samples that should be found in the log '
                    'file of each analysis.'))
    parser.add_argument('--burnin',
            action = 'store',
            type = int,
            default = 501,
            help = ('Number of MCMC samples to be ignored as burnin from the '
                    'beginning of every chain.'))

    if argv == sys.argv:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argv)

    parse_simulation_results(
            expected_number_of_runs = args.expected_number_of_runs,
            expected_number_of_samples = args.expected_number_of_samples,
            burnin = args.burnin)


if __name__ == "__main__":
    main_cli()
