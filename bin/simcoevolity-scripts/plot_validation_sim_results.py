#! /usr/bin/env python

import sys
import os
import re
import math
import glob
import logging

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
_LOG = logging.getLogger(os.path.basename(__file__))

import pycoevolity

sys.path.append("../")
import gekgo_util as project_util

import matplotlib as mpl

# Use TrueType (42) fonts rather than Type 3 fonts
mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["ps.fonttype"] = 42
tex_font_settings = {
        "text.usetex": True,
        "font.family": "sans-serif",
        "text.latex.preamble" : [
                "\\usepackage[T1]{fontenc}",
                "\\usepackage[cm]{sfmath}",
                ]
}

mpl.rcParams.update(tex_font_settings)

import matplotlib.pyplot as plt
from matplotlib import gridspec
import scipy.stats
import numpy


class HistogramData(object):
    def __init__(self, x = []):
        self._x = x

    @classmethod
    def init(cls, results, parameters, parameter_is_discrete):
        d = cls()
        d._x = []
        for parameter_str in parameters:
            if parameter_is_discrete:
                d._x.extend(int(x) for x in results["{0}".format(parameter_str)])
            else:
                d._x.extend(float(x) for x in results["{0}".format(parameter_str)])
        return d

    def _get_x(self):
        return self._x
    x = property(_get_x)


class ScatterData(object):
    def __init__(self,
            x = [],
            y = [],
            y_lower = [],
            y_upper = [],
            highlight_values = [],
            highlight_threshold = None,
            highlight_greater_than = True):
        self._x = x
        self._y = y
        self._y_lower = y_lower
        self._y_upper = y_upper
        self._highlight_values = highlight_values
        self._highlight_threshold = highlight_threshold
        self._highlight_greater_than = highlight_greater_than
        self._vet_data()
        self._highlight_indices = []
        self._populate_highlight_indices()
        self.highlight_color = (184 / 255.0, 90 / 255.0, 13 / 255.0) # pauburn

    @classmethod
    def init(cls, results, parameters,
            highlight_parameter_prefix = None,
            highlight_threshold = None,
            highlight_greater_than = True):
        d = cls()
        d._x = []
        d._y = []
        d._y_lower = []
        d._y_upper = []
        d._highlight_threshold = highlight_threshold
        d._highlight_values = []
        d._highlight_indices = []
        for parameter_str in parameters:
            d._x.extend(float(x) for x in results["true_{0}".format(parameter_str)])
            d._y.extend(float(x) for x in results["mean_{0}".format(parameter_str)])
            d._y_lower.extend(float(x) for x in results["eti_95_lower_{0}".format(parameter_str)])
            d._y_upper.extend(float(x) for x in results["eti_95_upper_{0}".format(parameter_str)])
            if highlight_parameter_prefix:
                d._highlight_values.extend(float(x) for x in results["{0}_{1}".format(
                        highlight_parameter_prefix,
                        parameter_str)])
        d._vet_data()
        d._populate_highlight_indices()
        return d

    def _vet_data(self):
        assert len(self._x) == len(self._y)
        if self._y_lower:
            assert len(self._x) == len(self._y_lower)
        if self._y_upper:
            assert len(self._x) == len(self._y_upper)
        if self._highlight_values:
            assert len(self._x) == len(self._highlight_values)

    def _populate_highlight_indices(self):
        if (self._highlight_values) and (self._highlight_threshold is not None):
            for i in range(len(self._x)):
                if self.highlight(i):
                    self._highlight_indices.append(i)

    def has_y_ci(self):
        return bool(self.y_lower) and bool(self.y_upper)

    def has_highlights(self):
        return bool(self._highlight_indices)

    def _get_x(self):
        return self._x
        # return [self._x[i] for i in range(len(self._x)) if i not in self._highlight_indices]
    x = property(_get_x)

    def _get_y(self):
        return self._y
        # return [self._y[i] for i in range(len(self._y)) if i not in self._highlight_indices]
    y = property(_get_y)

    def _get_y_lower(self):
        return self._y_lower
        # return [self._y_lower[i] for i in range(len(self._y_lower)) if i not in self._highlight_indices]
    y_lower = property(_get_y_lower)

    def _get_y_upper(self):
        return self._y_upper
        # return [self._y_upper[i] for i in range(len(self._y_upper)) if i not in self._highlight_indices]
    y_upper = property(_get_y_upper)

    def _get_highlight_indices(self):
        return self._highlight_indices
    highlight_indices = property(_get_highlight_indices)

    def _get_highlight_x(self):
        return [self._x[i] for i in self._highlight_indices]
    highlight_x = property(_get_highlight_x)

    def _get_highlight_y(self):
        return [self._y[i] for i in self._highlight_indices]
    highlight_y = property(_get_highlight_y)

    def _get_highlight_y_lower(self):
        return [self._y_lower[i] for i in self._highlight_indices]
    highlight_y_lower = property(_get_highlight_y_lower)

    def _get_highlight_y_upper(self):
        return [self._y_upper[i] for i in self._highlight_indices]
    highlight_y_upper = property(_get_highlight_y_upper)

    def highlight(self, index):
        if (not self._highlight_values) or (self._highlight_threshold is None):
            return False

        if self._highlight_greater_than:
            if self._highlight_values[index] > self._highlight_threshold:
                return True
            else:
                return False
        else:
            if self._highlight_values[index] < self._highlight_threshold:
                return True
            else:
                return False
        return False


def get_abs_error(true, estimate):
    return math.fabs(true - estimate)

def get_relative_estimate(true, estimate):
    return estimate / float(true)

def get_relative_error(true, estimate):
    return math.fabs(true - estimate) / true

def get_coal_units_vs_error(results, height_parameters, size_parameters,
        error_func = get_relative_error,
        psrf_as_response = False):
    assert len(height_parameters) == len(size_parameters)
    x = []
    y = []
    psrf = []
    for sp_index in range(len(height_parameters)):
        # Ensure we are getting the height and size for the same population
        assert height_parameters[sp_index].split("_")[-1] == size_parameters[sp_index].split("_")[-1]
        true_height_key = "true_{0}".format(height_parameters[sp_index])
        true_size_key = "true_{0}".format(size_parameters[sp_index])
        mean_height_key = "mean_{0}".format(height_parameters[sp_index])
        psrf_height_key = "psrf_{0}".format(height_parameters[sp_index])
        psrf_size_key = "psrf_{0}".format(size_parameters[sp_index])
        nsims = len(results[true_height_key])
        assert nsims == len(results[true_size_key])
        assert nsims == len(results[mean_height_key])
        for sim_index in range(nsims):
            t = float(results[true_height_key][sim_index])
            t_mean = float(results[mean_height_key][sim_index])
            err = error_func(t, t_mean)
            N = float(results[true_size_key][sim_index])
            coal_units = t / (2.0 * N)
            x.append(coal_units)
            y.append(err)
            psrf_value = max(
                    float(results[psrf_height_key][sim_index]), 
                    float(results[psrf_size_key][sim_index])) 
            psrf.append(psrf_value)
    if psrf_as_response:
        return x, psrf
    return x, y, psrf


def plot_gamma(shape = 1.0,
        scale = 1.0,
        offset = 0.0,
        x_min = 0.0,
        x_max = None,
        number_of_points = 1000,
        x_label = "Relative root size",
        include_x_label = True,
        include_y_label = True,
        include_title = True,
        plot_width = 3.5,
        plot_height = 3.0,
        xy_label_size = 16.0,
        title_size = 16.0,
        pad_left = 0.2,
        pad_right = 0.99,
        pad_bottom = 0.18,
        pad_top = 0.9,
        plot_file_prefix = None):
    if x_max is None:
        x_max = scipy.stats.gamma.ppf(0.999, shape, scale = scale)
        x_max_plot = x_max + offset
    else:
        x_max_plot = x_max
    x = numpy.linspace(x_min, x_max, number_of_points)
    d = scipy.stats.gamma.pdf(x, shape, scale = scale)

    x_plot = [v + offset for v in x]

    plt.close('all')
    fig = plt.figure(figsize = (plot_width, plot_height))
    gs = gridspec.GridSpec(1, 1,
            wspace = 0.0,
            hspace = 0.0)
    ax = plt.subplot(gs[0, 0])
    line = ax.plot(x_plot, d)
    ax.set_xlim(x_min, x_max_plot)
    plt.setp(line,
            color = (57 / 255.0, 115 / 255.0, 124 / 255.0),
            linestyle = '-',
            linewidth = 1.5,
            marker = '',
            zorder = 100)
    ax.axvline(x = 1.0,
            color = (184 / 255.0, 90 / 255.0, 13 / 255.0),
            linestyle = '--',
            linewidth = 1.0,
            marker = '',
            zorder = 0)
    if include_x_label:
        ax.set_xlabel(
                "{0}".format(x_label),
                fontsize = xy_label_size)
    if include_y_label:
        ax.set_ylabel(
                "Density",
                fontsize = xy_label_size)
    if include_title:
        # col_header = "$\\textrm{{\\sffamily Gamma}}({0:.0f}, \\textrm{{\\sffamily mean}} = {1:.1f})$".format(shape, (shape * scale) + offset)
        if offset == 0.0:
            col_header = "$\\textrm{{\\sffamily Gamma}}({0:.0f}, {1})$\n$\\textrm{{\\sffamily mean}} = {2}$".format(shape, scale, (shape * scale) + offset)
        else:
            col_header = "$\\textrm{{\\sffamily Gamma}}({0:.0f}, {1})$\n$\\textrm{{\\sffamily offset}} = {2}$ $\\textrm{{\\sffamily mean}} = {3}$".format(shape, scale, offset, (shape * scale) + offset)
        ax.set_title(col_header,
                fontsize = title_size)

    gs.update(
            left = pad_left,
            right = pad_right,
            bottom = pad_bottom,
            top = pad_top)

    plot_dir = os.path.join(project_util.ECOEVOLITY_SIM_DIR, "plots")
    if not os.path.exists(plot_dir):
        os.mkdir(plot_dir)
    plot_path = os.path.join(plot_dir,
            "{0}-gamma.pdf".format(plot_file_prefix))
    plt.savefig(plot_path)
    _LOG.info("Plot written to {0!r}\n".format(plot_path))

def get_nevents_probs(
        results_paths,
        nevents = 1):
    probs = []
    prob_key = "num_events_{0}_p".format(nevents)
    for d in pycoevolity.parsing.spreadsheet_iter(results_paths):
        probs.append((
                float(d[prob_key]),
                int(int(d["true_num_events"]) == nevents)
                ))
    return probs

def bin_prob_correct_tuples(probability_correct_tuples, nbins = 20):
    bin_upper_limits = list(get_sequence_iter(0.0, 1.0, nbins+1))[1:]
    bin_width = (bin_upper_limits[1] - bin_upper_limits[0]) / 2.0
    bins = [[] for i in range(nbins)]
    n = 0
    for (p, t) in probability_correct_tuples:
        n += 1
        binned = False
        for i, l in enumerate(bin_upper_limits):
            if p < l:
                bins[i].append((p, t))
                binned = True
                break
        if not binned:
            bins[i].append((p, t))
    total = 0
    for b in bins:
        total += len(b)
    assert total == n
    assert len(bins) == nbins
    est_true_tups = []
    for i, b in enumerate(bins):
        ests = [p for (p, t) in b]
        est = sum(ests) / float(len(ests))
        correct = [t for (p, t) in b]
        true = sum(correct) / float(len(correct))
        est_true_tups.append((est, true))
    return bins, est_true_tups

def get_nevents_estimated_true_probs(
        results_paths,
        nevents = 1,
        nbins = 20):
    nevent_probs = get_nevents_probs(
            results_paths = results_paths,
            nevents = nevents)
    _LOG.info("\tparsed results for {0} simulations".format(len(nevent_probs)))
    bins, tups = bin_prob_correct_tuples(nevent_probs, nbins = nbins)
    _LOG.info("\tbin sample sizes: {0}".format(
            ", ".join(str(len(b)) for b in bins)
            ))
    return bins, tups

def plot_nevents_estimated_vs_true_probs(
        results_paths,
        nevents = 1,
        nbins = 20,
        plot_file_prefix = ""):
    bins, est_true_probs = get_nevents_estimated_true_probs(
            results_paths = results_paths,
            nevents = nevents,
            nbins = nbins)

    plt.close('all')
    fig = plt.figure(figsize = (4.0, 3.5))
    ncols = 1
    nrows = 1
    gs = gridspec.GridSpec(nrows, ncols,
            wspace = 0.0,
            hspace = 0.0)

    ax = plt.subplot(gs[0, 0])
    x = [e for (e, t) in est_true_probs]
    y = [t for (e, t) in est_true_probs]
    sample_sizes = [len(b) for b in bins]
    line, = ax.plot(x, y)
    plt.setp(line,
            marker = 'o',
            markerfacecolor = 'none',
            markeredgecolor = '0.35',
            markeredgewidth = 0.7,
            markersize = 3.5,
            linestyle = '',
            zorder = 100,
            rasterized = False)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    for i, (label, lx, ly) in enumerate(zip(sample_sizes, x, y)):
        if i == 0:
            ax.annotate(
                    str(label),
                    xy = (lx, ly),
                    xytext = (1, 1),
                    textcoords = "offset points",
                    horizontalalignment = "left",
                    verticalalignment = "bottom")
        elif i == len(x) - 1:
            ax.annotate(
                    str(label),
                    xy = (lx, ly),
                    xytext = (-1, -1),
                    textcoords = "offset points",
                    horizontalalignment = "right",
                    verticalalignment = "top")
        else:
            ax.annotate(
                    str(label),
                    xy = (lx, ly),
                    xytext = (-1, 1),
                    textcoords = "offset points",
                    horizontalalignment = "right",
                    verticalalignment = "bottom")
    ylabel_text = ax.set_ylabel("True probability", size = 14.0)
    ax.text(0.5, -0.14,
            "Posterior probability of one divergence",
            horizontalalignment = "center",
            verticalalignment = "top",
            size = 14.0)
    identity_line, = ax.plot(
            [0.0, 1.0],
            [0.0, 1.0])
    plt.setp(identity_line,
            color = '0.8',
            linestyle = '-',
            linewidth = 1.0,
            marker = '',
            zorder = 0)

    gs.update(left = 0.10, right = 0.995, bottom = 0.18, top = 0.91)

    plot_dir = os.path.join(project_util.ECOEVOLITY_SIM_DIR, "plots")
    if not os.path.exists(plot_dir):
        os.mkdir(plot_dir)
    plot_file_name = "est-vs-true-prob-nevent-1.pdf"
    if plot_file_prefix:
        plot_file_name = plot_file_prefix + "-" + plot_file_name
    plot_path = os.path.join(plot_dir,
            plot_file_name)
    plt.savefig(plot_path)
    _LOG.info("Plots written to {0!r}\n".format(plot_path))

def get_sequence_iter(start = 0.0, stop = 1.0, n = 10):
    assert(stop > start)
    step = (stop - start) / float(n - 1)
    return ((start + (i * step)) for i in range(n))

def truncate_color_map(cmap, min_val = 0.0, max_val = 10, n = 100):
    new_cmap = mpl.colors.LinearSegmentedColormap.from_list(
            'trunc({n},{a:.2f},{b:.2f})'.format(
                    n = cmap.name,
                    a = min_val,
                    b = max_val),
            cmap(list(get_sequence_iter(min_val, max_val, n))))
    return new_cmap

def get_root_gamma_parameters(root_shape_string, root_scale_string):
    shape = float(root_shape_string)
    denom = float("1" + ("0" * (len(root_scale_string) - 1)))
    scale = float(root_scale_string) / denom
    return shape, scale

root_gamma_pattern = re.compile(r'root-(?P<alpha_setting>\d+)-(?P<scale_setting>\d+)-')
def get_root_gamma_label(sim_dir):
    m = root_gamma_pattern.search(sim_dir)
    root_shape, root_scale = get_root_gamma_parameters(
            root_shape_string = m.group("alpha_setting"),
            root_scale_string = m.group("scale_setting"))
    mean_decimal_places = 1
    gamma_mean = root_shape * root_scale
    if gamma_mean < 0.49:
        mean_decimal_places = 2
    return "$\\textrm{{\\sffamily Gamma}}({shape}, \\textrm{{\\sffamily mean}} = {mean:.{mean_decimal_places}f})$".format(
            shape = int(root_shape),
            mean = gamma_mean,
            mean_decimal_places = mean_decimal_places)

def get_errors(values, lowers, uppers):
    n = len(values)
    assert(n == len(lowers))
    assert(n == len(uppers))
    return [[values[i] - lowers[i] for i in range(n)],
            [uppers[i] - values[i] for i in range(n)]]

def ci_width_iter(results, parameter_str):
    n = len(results["eti_95_upper_{0}".format(parameter_str)])
    for i in range(n):
        upper = float(results["eti_95_upper_{0}".format(parameter_str)][i])
        lower = float(results["eti_95_lower_{0}".format(parameter_str)][i])
        yield upper - lower

def absolute_error_iter(results, parameter_str):
    n = len(results["true_{0}".format(parameter_str)])
    for i in range(n):
        t = float(results["true_{0}".format(parameter_str)][i])
        e = float(results["mean_{0}".format(parameter_str)][i])
        yield math.fabs(t - e)


def plot_ess_versus_error(
        parameters,
        results_grid,
        column_labels = None,
        row_labels = None,
        parameter_label = "event time",
        plot_file_prefix = None):
    _LOG.info("Generating ESS vs CI scatter plots for {0}...".format(parameter_label))

    assert(len(parameters) == len(set(parameters)))
    if row_labels:
        assert len(row_labels) ==  len(results_grid)
    if column_labels:
        assert len(column_labels) == len(results_grid[0])

    nrows = len(results_grid)
    ncols = len(results_grid[0])

    if not plot_file_prefix:
        plot_file_prefix = parameters[0] 
    plot_file_prefix_ci = plot_file_prefix + "-ess-vs-ci-width"
    plot_file_prefix_error = plot_file_prefix + "-ess-vs-error"

    # Very inefficient, but parsing all results to get min/max for parameter
    ess_min = float('inf')
    ess_max = float('-inf')
    ci_width_min = float('inf')
    ci_width_max = float('-inf')
    error_min = float('inf')
    error_max = float('-inf')
    for row_index, results_grid_row in enumerate(results_grid):
        for column_index, results in enumerate(results_grid_row):
            for parameter_str in parameters:
                ci_widths = tuple(ci_width_iter(results, parameter_str))
                errors = tuple(absolute_error_iter(results, parameter_str))
                ess_min = min(ess_min,
                        min(float(x) for x in results["ess_sum_{0}".format(parameter_str)]))
                ess_max = max(ess_max,
                        max(float(x) for x in results["ess_sum_{0}".format(parameter_str)]))
                ci_width_min = min(ci_width_min, min(ci_widths))
                ci_width_max = max(ci_width_max, max(ci_widths))
                error_min = min(error_min, min(errors))
                error_max = max(error_max, max(errors))
    ess_axis_buffer = math.fabs(ess_max - ess_min) * 0.05
    ess_axis_min = ess_min - ess_axis_buffer
    ess_axis_max = ess_max + ess_axis_buffer
    ci_width_axis_buffer = math.fabs(ci_width_max - ci_width_min) * 0.05
    ci_width_axis_min = ci_width_min - ci_width_axis_buffer
    ci_width_axis_max = ci_width_max + ci_width_axis_buffer
    error_axis_buffer = math.fabs(error_max - error_min) * 0.05
    error_axis_min = error_min - error_axis_buffer
    error_axis_max = error_max + error_axis_buffer

    plt.close('all')
    w = 1.6
    h = 1.5
    fig_width = (ncols * w) + 1.0
    fig_height = (nrows * h) + 0.7
    fig = plt.figure(figsize = (fig_width, fig_height))
    gs = gridspec.GridSpec(nrows, ncols,
            wspace = 0.0,
            hspace = 0.0)

    for row_index, results_grid_row in enumerate(results_grid):
        for column_index, results in enumerate(results_grid_row):

            x = []
            y = []
            for parameter_str in parameters:
                x.extend(float(x) for x in results["ess_sum_{0}".format(parameter_str)])
                y.extend(ci_width_iter(results, parameter_str))

            assert(len(x) == len(y))
            ax = plt.subplot(gs[row_index, column_index])
            line, = ax.plot(x, y)
            plt.setp(line,
                    marker = 'o',
                    markerfacecolor = 'none',
                    markeredgecolor = '0.35',
                    markeredgewidth = 0.7,
                    markersize = 2.5,
                    linestyle = '',
                    zorder = 100,
                    rasterized = True)
            ax.set_xlim(ess_axis_min, ess_axis_max)
            ax.set_ylim(ci_width_axis_min, ci_width_axis_max)
            if column_labels and (row_index == 0):
                col_header = column_labels[column_index]
                ax.text(0.5, 1.015,
                        col_header,
                        horizontalalignment = "center",
                        verticalalignment = "bottom",
                        transform = ax.transAxes)
            if row_labels and (column_index == (ncols - 1)):
                row_label = row_labels[row_index]
                ax.text(1.015, 0.5,
                        row_label,
                        horizontalalignment = "left",
                        verticalalignment = "center",
                        rotation = 270.0,
                        transform = ax.transAxes)

    # show only the outside ticks
    all_axes = fig.get_axes()
    for ax in all_axes:
        if not ax.is_last_row():
            ax.set_xticks([])
        if not ax.is_first_col():
            ax.set_yticks([])

    # show tick labels only for lower-left plot 
    all_axes = fig.get_axes()
    for ax in all_axes:
        if ax.is_last_row() and ax.is_first_col():
            continue
        xtick_labels = ["" for item in ax.get_xticklabels()]
        ytick_labels = ["" for item in ax.get_yticklabels()]
        ax.set_xticklabels(xtick_labels)
        ax.set_yticklabels(ytick_labels)

    # avoid doubled spines
    all_axes = fig.get_axes()
    for ax in all_axes:
        for sp in ax.spines.values():
            sp.set_visible(False)
            sp.set_linewidth(2)
        if ax.is_first_row():
            ax.spines['top'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
        else:
            ax.spines['bottom'].set_visible(True)
        if ax.is_first_col():
            ax.spines['left'].set_visible(True)
            ax.spines['right'].set_visible(True)
        else:
            ax.spines['right'].set_visible(True)

    fig.text(0.5, 0.001,
            "Effective sample size of {0}".format(parameter_label),
            horizontalalignment = "center",
            verticalalignment = "bottom",
            size = 18.0)
    fig.text(0.005, 0.5,
            "CI width {0}".format(parameter_label),
            horizontalalignment = "left",
            verticalalignment = "center",
            rotation = "vertical",
            size = 18.0)

    gs.update(left = 0.08, right = 0.98, bottom = 0.08, top = 0.97)

    plot_dir = os.path.join(project_util.ECOEVOLITY_SIM_DIR, "plots")
    if not os.path.exists(plot_dir):
        os.mkdir(plot_dir)
    plot_path = os.path.join(plot_dir,
            "{0}-scatter.pdf".format(plot_file_prefix_ci))
    plt.savefig(plot_path, dpi=600)
    _LOG.info("Plots written to {0!r}\n".format(plot_path))


    _LOG.info("Generating ESS vs error scatter plots for {0}...".format(parameter_label))
    plt.close('all')
    w = 1.6
    h = 1.5
    fig_width = (ncols * w) + 1.0
    fig_height = (nrows * h) + 0.7
    fig = plt.figure(figsize = (fig_width, fig_height))
    gs = gridspec.GridSpec(nrows, ncols,
            wspace = 0.0,
            hspace = 0.0)

    for row_index, results_grid_row in enumerate(results_grid):
        for column_index, results in enumerate(results_grid_row):
            x = []
            y = []
            for parameter_str in parameters:
                x.extend(float(x) for x in results["ess_sum_{0}".format(parameter_str)])
                y.extend(absolute_error_iter(results, parameter_str))
                

            assert(len(x) == len(y))
            ax = plt.subplot(gs[row_index, column_index])
            line, = ax.plot(x, y)
            plt.setp(line,
                    marker = 'o',
                    markerfacecolor = 'none',
                    markeredgecolor = '0.35',
                    markeredgewidth = 0.7,
                    markersize = 2.5,
                    linestyle = '',
                    zorder = 100,
                    rasterized = True)
            ax.set_xlim(ess_axis_min, ess_axis_max)
            ax.set_ylim(error_axis_min, error_axis_max)
            if column_labels and (row_index == 0):
                col_header = column_labels[column_index]
                ax.text(0.5, 1.015,
                        col_header,
                        horizontalalignment = "center",
                        verticalalignment = "bottom",
                        transform = ax.transAxes)
            if row_labels and (column_index == (ncols - 1)):
                row_label = row_labels[row_index]
                ax.text(1.015, 0.5,
                        row_label,
                        horizontalalignment = "left",
                        verticalalignment = "center",
                        rotation = 270.0,
                        transform = ax.transAxes)

    # show only the outside ticks
    all_axes = fig.get_axes()
    for ax in all_axes:
        if not ax.is_last_row():
            ax.set_xticks([])
        if not ax.is_first_col():
            ax.set_yticks([])

    # show tick labels only for lower-left plot 
    all_axes = fig.get_axes()
    for ax in all_axes:
        if ax.is_last_row() and ax.is_first_col():
            continue
        xtick_labels = ["" for item in ax.get_xticklabels()]
        ytick_labels = ["" for item in ax.get_yticklabels()]
        ax.set_xticklabels(xtick_labels)
        ax.set_yticklabels(ytick_labels)

    # avoid doubled spines
    all_axes = fig.get_axes()
    for ax in all_axes:
        for sp in ax.spines.values():
            sp.set_visible(False)
            sp.set_linewidth(2)
        if ax.is_first_row():
            ax.spines['top'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
        else:
            ax.spines['bottom'].set_visible(True)
        if ax.is_first_col():
            ax.spines['left'].set_visible(True)
            ax.spines['right'].set_visible(True)
        else:
            ax.spines['right'].set_visible(True)

    fig.text(0.5, 0.001,
            "Effective sample size of {0}".format(parameter_label),
            horizontalalignment = "center",
            verticalalignment = "bottom",
            size = 18.0)
    fig.text(0.005, 0.5,
            "Absolute error of {0}".format(parameter_label),
            horizontalalignment = "left",
            verticalalignment = "center",
            rotation = "vertical",
            size = 18.0)

    gs.update(left = 0.08, right = 0.98, bottom = 0.08, top = 0.97)

    plot_path = os.path.join(plot_dir,
            "{0}-scatter.pdf".format(plot_file_prefix_error))
    plt.savefig(plot_path, dpi=600)
    _LOG.info("Plots written to {0!r}\n".format(plot_path))


def generate_scatter_plots(
        data_grid,
        plot_file_prefix,
        parameter_symbol = "t",
        column_labels = None,
        row_labels = None,
        plot_width = 1.9,
        plot_height = 1.8,
        pad_left = 0.1,
        pad_right = 0.98,
        pad_bottom = 0.12,
        pad_top = 0.92,
        x_label = None,
        x_label_size = 18.0,
        y_label = None,
        y_label_size = 18.0,
        force_shared_x_range = True,
        force_shared_y_range = True,
        force_shared_xy_ranges = True,
        force_shared_spines = True,
        include_coverage = True,
        include_rmse = True,
        include_identity_line = True,
        include_error_bars = True):
    if force_shared_spines:
        force_shared_x_range = True
        force_shared_y_range = True

    if row_labels:
        assert len(row_labels) ==  len(data_grid)
    if column_labels:
        assert len(column_labels) == len(data_grid[0])

    nrows = len(data_grid)
    ncols = len(data_grid[0])

    x_min = float('inf')
    x_max = float('-inf')
    y_min = float('inf')
    y_max = float('-inf')
    for row_index, data_grid_row in enumerate(data_grid):
        for column_index, data in enumerate(data_grid_row):
            x_min = min(x_min, min(data.x))
            x_max = max(x_max, max(data.x))
            y_min = min(y_min, min(data.y))
            y_max = max(y_max, max(data.y))
    if force_shared_xy_ranges:
        mn = min(x_min, y_min)
        mx = max(x_max, y_max)
        x_min = mn
        y_min = mn
        x_max = mx
        y_max = mx
    x_buffer = math.fabs(x_max - x_min) * 0.025
    x_axis_min = x_min - x_buffer
    x_axis_max = x_max + x_buffer
    y_buffer = math.fabs(y_max - y_min) * 0.025
    y_axis_min = y_min - y_buffer
    y_axis_max = y_max + y_buffer


    plt.close('all')
    w = plot_width
    h = plot_height
    fig_width = (ncols * w)
    fig_height = (nrows * h)
    fig = plt.figure(figsize = (fig_width, fig_height))
    if force_shared_spines:
        gs = gridspec.GridSpec(nrows, ncols,
                wspace = 0.0,
                hspace = 0.0)
    else:
        gs = gridspec.GridSpec(nrows, ncols)

    for row_index, data_grid_row in enumerate(data_grid):
        for column_index, data in enumerate(data_grid_row):
            proportion_within_ci = 0.0
            if include_coverage and data.has_y_ci():
                proportion_within_ci = pycoevolity.stats.get_proportion_of_values_within_intervals(
                        data.x,
                        data.y_lower,
                        data.y_upper)
            rmse = 0.0
            if include_rmse:
                rmse = pycoevolity.stats.root_mean_square_error(data.x, data.y)
            ax = plt.subplot(gs[row_index, column_index])
            if include_error_bars and data.has_y_ci():
                line = ax.errorbar(
                        x = data.x,
                        y = data.y,
                        yerr = get_errors(data.y, data.y_lower, data.y_upper),
                        ecolor = '0.65',
                        elinewidth = 0.5,
                        capsize = 0.8,
                        barsabove = False,
                        marker = 'o',
                        linestyle = '',
                        markerfacecolor = 'none',
                        markeredgecolor = '0.35',
                        markeredgewidth = 0.7,
                        markersize = 2.5,
                        zorder = 100,
                        rasterized = True)
                if data.has_highlights():
                    # line = ax.errorbar(
                    #         x = data.highlight_x,
                    #         y = data.highlight_y,
                    #         yerr = get_errors(data.highlight_y,
                    #                 data.highlight_y_lower,
                    #                 data.highlight_y_upper),
                    #         ecolor = data.highlight_color,
                    #         elinewidth = 0.5,
                    #         capsize = 0.8,
                    #         barsabove = False,
                    #         marker = 'o',
                    #         linestyle = '',
                    #         markerfacecolor = 'none',
                    #         markeredgecolor = data.highlight_color,
                    #         markeredgewidth = 0.7,
                    #         markersize = 2.5,
                    #         zorder = 200,
                    #         rasterized = True)
                    line, = ax.plot(data.highlight_x, data.highlight_y)
                    plt.setp(line,
                            marker = 'o',
                            linestyle = '',
                            markerfacecolor = 'none',
                            markeredgecolor = data.highlight_color,
                            markeredgewidth = 0.7,
                            markersize = 2.5,
                            zorder = 200,
                            rasterized = True)
            else:
                line, = ax.plot(data.x, data.y)
                plt.setp(line,
                        marker = 'o',
                        linestyle = '',
                        markerfacecolor = 'none',
                        markeredgecolor = '0.35',
                        markeredgewidth = 0.7,
                        markersize = 2.5,
                        zorder = 100,
                        rasterized = True)
                if data.has_highlights():
                    line, = ax.plot(data.highlight_x, data.highlight_y)
                    plt.setp(line,
                            marker = 'o',
                            linestyle = '',
                            markerfacecolor = 'none',
                            markeredgecolor = data.highlight_color,
                            markeredgewidth = 0.7,
                            markersize = 2.5,
                            zorder = 200,
                            rasterized = True)
            plot_min = min(min(data.x), min(data.y))
            plot_max = max(max(data.x), max(data.y))
            plot_axis_buffer = (plot_max - plot_min) * 0.025
            if force_shared_x_range:
                ax.set_xlim(x_axis_min, x_axis_max)
            elif force_shared_xy_ranges:
                ax.set_xlim(plot_min - plot_axis_buffer, plot_max + plot_axis_buffer)
            else:
                x_buffer = (max(data.x) - min(data.x)) * 0.025
                ax.set_xlim(min(data.x) - x_buffer, max(data.x) + x_buffer)
            if force_shared_y_range:
                ax.set_ylim(y_axis_min, y_axis_max)
            elif force_shared_xy_ranges:
                ax.set_ylim(plot_min - plot_axis_buffer, plot_max + plot_axis_buffer)
            else:
                y_buffer = (max(data.y) - min(data.y)) * 0.025
                ay.set_ylim(min(data.y) - y_buffer, max(data.y) + y_buffer)
            if include_identity_line:
                identity_line, = ax.plot(
                        [x_axis_min, x_axis_max],
                        [y_axis_min, y_axis_max])
                plt.setp(identity_line,
                        color = '0.7',
                        linestyle = '-',
                        linewidth = 1.0,
                        marker = '',
                        zorder = 0)
            if include_coverage:
                ax.text(0.02, 0.97,
                        "\\scriptsize\\noindent$p({0:s} \\in \\textrm{{\\sffamily CI}}) = {1:.3f}$".format(
                                parameter_symbol,
                                proportion_within_ci),
                        horizontalalignment = "left",
                        verticalalignment = "top",
                        transform = ax.transAxes,
                        size = 6.0,
                        zorder = 300)
            if include_rmse:
                text_y = 0.97
                if include_coverage:
                    text_y = 0.87
                ax.text(0.02, text_y,
                        "\\scriptsize\\noindent RMSE = {0:.2e}".format(
                                rmse),
                        horizontalalignment = "left",
                        verticalalignment = "top",
                        transform = ax.transAxes,
                        size = 6.0,
                        zorder = 300)
            if column_labels and (row_index == 0):
                col_header = column_labels[column_index]
                ax.text(0.5, 1.015,
                        col_header,
                        horizontalalignment = "center",
                        verticalalignment = "bottom",
                        transform = ax.transAxes)
            if row_labels and (column_index == (ncols - 1)):
                row_label = row_labels[row_index]
                ax.text(1.015, 0.5,
                        row_label,
                        horizontalalignment = "left",
                        verticalalignment = "center",
                        rotation = 270.0,
                        transform = ax.transAxes)

    if force_shared_spines:
        # show only the outside ticks
        all_axes = fig.get_axes()
        for ax in all_axes:
            if not ax.is_last_row():
                ax.set_xticks([])
            if not ax.is_first_col():
                ax.set_yticks([])

        # show tick labels only for lower-left plot 
        all_axes = fig.get_axes()
        for ax in all_axes:
            if ax.is_last_row() and ax.is_first_col():
                continue
            xtick_labels = ["" for item in ax.get_xticklabels()]
            ytick_labels = ["" for item in ax.get_yticklabels()]
            ax.set_xticklabels(xtick_labels)
            ax.set_yticklabels(ytick_labels)

        # avoid doubled spines
        all_axes = fig.get_axes()
        for ax in all_axes:
            for sp in ax.spines.values():
                sp.set_visible(False)
                sp.set_linewidth(2)
            if ax.is_first_row():
                ax.spines['top'].set_visible(True)
                ax.spines['bottom'].set_visible(True)
            else:
                ax.spines['bottom'].set_visible(True)
            if ax.is_first_col():
                ax.spines['left'].set_visible(True)
                ax.spines['right'].set_visible(True)
            else:
                ax.spines['right'].set_visible(True)
    else:
        fig.tight_layout()

    if x_label:
        fig.text(0.5, 0.001,
                x_label,
                horizontalalignment = "center",
                verticalalignment = "bottom",
                size = x_label_size)
    if y_label:
        fig.text(0.005, 0.5,
                y_label,
                horizontalalignment = "left",
                verticalalignment = "center",
                rotation = "vertical",
                size = y_label_size)

    gs.update(left = pad_left,
            right = pad_right,
            bottom = pad_bottom,
            top = pad_top)

    plot_dir = os.path.join(project_util.ECOEVOLITY_SIM_DIR, "plots")
    if not os.path.exists(plot_dir):
        os.mkdir(plot_dir)
    plot_path = os.path.join(plot_dir,
            "{0}-scatter.pdf".format(plot_file_prefix))
    plt.savefig(plot_path, dpi=600)
    _LOG.info("Plots written to {0!r}\n".format(plot_path))

def generate_specific_scatter_plot(
        data,
        plot_file_prefix,
        parameter_symbol = "t",
        title = None,
        title_size = 16.0,
        x_label = None,
        x_label_size = 16.0,
        y_label = None,
        y_label_size = 16.0,
        plot_width = 3.5,
        plot_height = 3.0,
        pad_left = 0.2,
        pad_right = 0.99,
        pad_bottom = 0.18,
        pad_top = 0.9,
        force_shared_xy_ranges = True,
        include_coverage = True,
        include_rmse = True,
        include_identity_line = True,
        include_error_bars = True):

    x_min = min(data.x)
    x_max = max(data.x)
    y_min = min(data.y)
    y_max = max(data.y)
    if force_shared_xy_ranges:
        mn = min(x_min, y_min)
        mx = max(x_max, y_max)
        x_min = mn
        y_min = mn
        x_max = mx
        y_max = mx
    x_buffer = math.fabs(x_max - x_min) * 0.05
    x_axis_min = x_min - x_buffer
    x_axis_max = x_max + x_buffer
    y_buffer = math.fabs(y_max - y_min) * 0.05
    y_axis_min = y_min - y_buffer
    y_axis_max = y_max + y_buffer

    plt.close('all')
    fig = plt.figure(figsize = (plot_width, plot_height))
    gs = gridspec.GridSpec(1, 1,
            wspace = 0.0,
            hspace = 0.0)

    proportion_within_ci = 0.0
    if include_coverage and data.has_y_ci():
        proportion_within_ci = pycoevolity.stats.get_proportion_of_values_within_intervals(
                data.x,
                data.y_lower,
                data.y_upper)
    rmse = 0.0
    if include_rmse:
        rmse = pycoevolity.stats.root_mean_square_error(data.x, data.y)
    ax = plt.subplot(gs[0, 0])
    if include_error_bars and data.has_y_ci():
        line = ax.errorbar(
                x = data.x,
                y = data.y,
                yerr = get_errors(data.y, data.y_lower, data.y_upper),
                ecolor = '0.65',
                elinewidth = 0.5,
                capsize = 0.8,
                barsabove = False,
                marker = 'o',
                linestyle = '',
                markerfacecolor = 'none',
                markeredgecolor = '0.35',
                markeredgewidth = 0.7,
                markersize = 2.5,
                zorder = 100,
                rasterized = True)
        if data.has_highlights():
            # line = ax.errorbar(
            #         x = data.highlight_x,
            #         y = data.highlight_y,
            #         yerr = get_errors(data.highlight_y,
            #                 data.highlight_y_lower,
            #                 data.highlight_y_upper),
            #         ecolor = data.highlight_color,
            #         elinewidth = 0.5,
            #         capsize = 0.8,
            #         barsabove = False,
            #         marker = 'o',
            #         linestyle = '',
            #         markerfacecolor = 'none',
            #         markeredgecolor = data.highlight_color,
            #         markeredgewidth = 0.7,
            #         markersize = 2.5,
            #         zorder = 200,
            #         rasterized = True)
            line, = ax.plot(data.highlight_x, data.highlight_y)
            plt.setp(line,
                    marker = 'o',
                    linestyle = '',
                    markerfacecolor = 'none',
                    markeredgecolor = data.highlight_color,
                    markeredgewidth = 0.7,
                    markersize = 2.5,
                    zorder = 200,
                    rasterized = True)
    else:
        line, = ax.plot(data.x, data.y)
        plt.setp(line,
                marker = 'o',
                linestyle = '',
                markerfacecolor = 'none',
                markeredgecolor = '0.35',
                markeredgewidth = 0.7,
                markersize = 2.5,
                zorder = 100,
                rasterized = True)
        if data.has_highlights():
            line, = ax.plot(x = data.highlight_x, y = data.highlight_y)
            plt.setp(line,
                    marker = 'o',
                    linestyle = '',
                    markerfacecolor = 'none',
                    markeredgecolor = data.highlight_color,
                    markeredgewidth = 0.7,
                    markersize = 2.5,
                    zorder = 200,
                    rasterized = True)
    ax.set_xlim(x_axis_min, x_axis_max)
    ax.set_ylim(y_axis_min, y_axis_max)
    if include_identity_line:
        identity_line, = ax.plot(
                [x_axis_min, x_axis_max],
                [y_axis_min, y_axis_max])
        plt.setp(identity_line,
                color = '0.7',
                linestyle = '-',
                linewidth = 1.0,
                marker = '',
                zorder = 0)
    if include_coverage:
        ax.text(0.02, 0.97,
                "\\normalsize\\noindent$p({0:s} \\in \\textrm{{\\sffamily CI}}) = {1:.3f}$".format(
                        parameter_symbol,
                        proportion_within_ci),
                horizontalalignment = "left",
                verticalalignment = "top",
                transform = ax.transAxes,
                size = 8.0,
                zorder = 300)
    if include_rmse:
        text_y = 0.97
        if include_coverage:
            text_y = 0.87
        ax.text(0.02, text_y,
                "\\normalsize\\noindent RMSE = {0:.2e}".format(
                        rmse),
                horizontalalignment = "left",
                verticalalignment = "top",
                transform = ax.transAxes,
                size = 8.0,
                zorder = 300)
    if x_label is not None:
        ax.set_xlabel(
                x_label,
                fontsize = x_label_size)
    if y_label is not None:
        ax.set_ylabel(
                y_label,
                fontsize = y_label_size)
    if title is not None:
        ax.set_title(plot_title,
                fontsize = title_size)

    gs.update(
            left = pad_left,
            right = pad_right,
            bottom = pad_bottom,
            top = pad_top)

    plot_dir = os.path.join(project_util.ECOEVOLITY_SIM_DIR, "plots")
    if not os.path.exists(plot_dir):
        os.mkdir(plot_dir)
    plot_path = os.path.join(plot_dir,
            "{0}-scatter.pdf".format(plot_file_prefix))
    plt.savefig(plot_path, dpi=600)
    _LOG.info("Plots written to {0!r}\n".format(plot_path))


def generate_histograms(
        data_grid,
        plot_file_prefix,
        column_labels = None,
        row_labels = None,
        parameter_label = "Number of variable sites",
        range_key = "range",
        number_of_digits = 0,
        plot_width = 1.9,
        plot_height = 1.8,
        pad_left = 0.1,
        pad_right = 0.98,
        pad_bottom = 0.12,
        pad_top = 0.92,
        force_shared_x_range = True,
        force_shared_bins = True,
        force_shared_y_range = True,
        force_shared_spines = True,
        ):
    if force_shared_spines:
        force_shared_x_range = True
        force_shared_y_range = True

    if row_labels:
        assert len(row_labels) ==  len(data_grid)
    if column_labels:
        assert len(column_labels) == len(data_grid[0])

    nrows = len(data_grid)
    ncols = len(data_grid[0])

    x_min = float('inf')
    x_max = float('-inf')
    for row_index, data_grid_row in enumerate(data_grid):
        for column_index, data in enumerate(data_grid_row):
            x_min = min(x_min, min(data.x))
            x_max = max(x_max, max(data.x))

    axis_buffer = math.fabs(x_max - x_min) * 0.05
    axis_min = x_min - axis_buffer
    axis_max = x_max + axis_buffer

    plt.close('all')
    w = plot_width
    h = plot_height
    fig_width = (ncols * w)
    fig_height = (nrows * h)
    fig = plt.figure(figsize = (fig_width, fig_height))
    if force_shared_spines:
        gs = gridspec.GridSpec(nrows, ncols,
                wspace = 0.0,
                hspace = 0.0)
    else:
        gs = gridspec.GridSpec(nrows, ncols)

    hist_bins = None
    x_range = None
    if force_shared_x_range:
        x_range = (x_min, x_max)
    for row_index, data_grid_row in enumerate(data_grid):
        for column_index, data in enumerate(data_grid_row):
            summary = pycoevolity.stats.get_summary(data.x)
            _LOG.info("0.025, 0.975 quantiles: {0:.2f}, {1:.2f}".format(
                    summary["qi_95"][0],
                    summary["qi_95"][1]))

            ax = plt.subplot(gs[row_index, column_index])
            n, bins, patches = ax.hist(data.x,
                    weights = [1.0 / float(len(data.x))] * len(data.x),
                    bins = hist_bins,
                    range = x_range,
                    cumulative = False,
                    histtype = 'bar',
                    align = 'mid',
                    orientation = 'vertical',
                    rwidth = None,
                    log = False,
                    color = None,
                    edgecolor = '0.5',
                    facecolor = '0.5',
                    fill = True,
                    hatch = None,
                    label = None,
                    linestyle = None,
                    linewidth = None,
                    zorder = 10,
                    )
            if (hist_bins is None) and force_shared_bins:
                hist_bins = bins
            ax.text(0.98, 0.98,
                    "\\scriptsize {mean:,.{ndigits}f} ({lower:,.{ndigits}f}--{upper:,.{ndigits}f})".format(
                            mean = summary["mean"],
                            lower = summary[range_key][0],
                            upper = summary[range_key][1],
                            ndigits = number_of_digits),
                    horizontalalignment = "right",
                    verticalalignment = "top",
                    transform = ax.transAxes,
                    zorder = 200)

            if column_labels and (row_index == 0):
                col_header = column_labels[column_index]
                ax.text(0.5, 1.015,
                        col_header,
                        horizontalalignment = "center",
                        verticalalignment = "bottom",
                        transform = ax.transAxes)
            if row_labels and (column_index == (ncols - 1)):
                row_label = row_labels[row_index]
                ax.text(1.015, 0.5,
                        row_label,
                        horizontalalignment = "left",
                        verticalalignment = "center",
                        rotation = 270.0,
                        transform = ax.transAxes)

    if force_shared_y_range:
        all_axes = fig.get_axes()
        # y_max = float('-inf')
        # for ax in all_axes:
        #     ymn, ymx = ax.get_ylim()
        #     y_max = max(y_max, ymx)
        for ax in all_axes:
            ax.set_ylim(0.0, 1.0)

    if force_shared_spines:
        # show only the outside ticks
        all_axes = fig.get_axes()
        for ax in all_axes:
            if not ax.is_last_row():
                ax.set_xticks([])
            if not ax.is_first_col():
                ax.set_yticks([])

        # show tick labels only for lower-left plot 
        all_axes = fig.get_axes()
        for ax in all_axes:
            if ax.is_last_row() and ax.is_first_col():
                continue
            xtick_labels = ["" for item in ax.get_xticklabels()]
            ytick_labels = ["" for item in ax.get_yticklabels()]
            ax.set_xticklabels(xtick_labels)
            ax.set_yticklabels(ytick_labels)

        # avoid doubled spines
        all_axes = fig.get_axes()
        for ax in all_axes:
            for sp in ax.spines.values():
                sp.set_visible(False)
                sp.set_linewidth(2)
            if ax.is_first_row():
                ax.spines['top'].set_visible(True)
                ax.spines['bottom'].set_visible(True)
            else:
                ax.spines['bottom'].set_visible(True)
            if ax.is_first_col():
                ax.spines['left'].set_visible(True)
                ax.spines['right'].set_visible(True)
            else:
                ax.spines['right'].set_visible(True)
    else:
        fig.tight_layout()

    fig.text(0.5, 0.001,
            parameter_label,
            horizontalalignment = "center",
            verticalalignment = "bottom",
            size = 18.0)
    fig.text(0.005, 0.5,
            # "Density",
            "Frequency",
            horizontalalignment = "left",
            verticalalignment = "center",
            rotation = "vertical",
            size = 18.0)

    gs.update(left = pad_left,
            right = pad_right,
            bottom = pad_bottom,
            top = pad_top)

    plot_dir = os.path.join(project_util.ECOEVOLITY_SIM_DIR, "plots")
    if not os.path.exists(plot_dir):
        os.mkdir(plot_dir)
    plot_path = os.path.join(plot_dir,
            "{0}-histograms.pdf".format(plot_file_prefix))
    plt.savefig(plot_path)
    _LOG.info("Plots written to {0!r}\n".format(plot_path))


def generate_model_plots(
        results_grid,
        column_labels = None,
        row_labels = None,
        number_of_comparisons = 3,
        plot_width = 1.6,
        plot_height = 1.5,
        pad_left = 0.1,
        pad_right = 0.98,
        pad_bottom = 0.12,
        pad_top = 0.92,
        y_label_size = 18.0,
        y_label = None,
        number_font_size = 12.0,
        include_median = True,
        include_cs = True,
        include_prop_correct = True,
        filter_parameter_prefix = None,
        filter_threshold = None,
        plot_file_prefix = None):
    _LOG.info("Generating model plots...")

    cmap = truncate_color_map(plt.cm.binary, 0.0, 0.65, 100)

    if row_labels:
        assert len(row_labels) ==  len(results_grid)
    if column_labels:
        assert len(column_labels) == len(results_grid[0])

    nrows = len(results_grid)
    ncols = len(results_grid[0])

    plt.close('all')
    w = plot_width
    h = plot_height
    fig_width = (ncols * w)
    fig_height = (nrows * h)
    fig = plt.figure(figsize = (fig_width, fig_height))
    gs = gridspec.GridSpec(nrows, ncols,
            wspace = 0.0,
            hspace = 0.0)

    for row_index, results_grid_row in enumerate(results_grid):
        for column_index, results in enumerate(results_grid_row):
            indices_to_plot = range(len(results["true_num_events"]))
            if filter_parameter_prefix:
                for i in range(len(results["true_num_events"])):
                    for k, v in results.items():
                        if k.startswith(filter_parameter_prefix) and (float(results[k][i]) > filter_threshold):
                            indices_to_plot.remove(i)
                            break
                _LOG.info("{0} sim reps removed for {1}-row{2}-col{3} due to {4}".format(
                        len(results["true_num_events"]) - len(indices_to_plot),
                        plot_file_prefix,
                        row_index,
                        column_index,
                        filter_parameter_prefix))

            true_map_nevents = []
            true_map_nevents_probs = []
            for i in range(number_of_comparisons):
                true_map_nevents.append([0 for i in range(number_of_comparisons)])
                true_map_nevents_probs.append([[] for i in range(number_of_comparisons)])
            true_nevents = tuple(int(results["true_num_events"][i]) for i in indices_to_plot)
            map_nevents = tuple(int(results["map_num_events"][i]) for i in indices_to_plot)
            true_nevents_cred_levels = tuple(float(results["true_num_events_cred_level"][i]) for i in indices_to_plot)
            # true_model_cred_levels = tuple(float(x) for x in results["true_model_cred_level"])
            assert(len(true_nevents) == len(indices_to_plot))
            assert(len(true_nevents) == len(map_nevents))
            assert(len(true_nevents) == len(true_nevents_cred_levels))
            # assert(len(true_nevents) == len(true_model_cred_levels))

            true_nevents_probs = []
            map_nevents_probs = []
            for i in range(len(indices_to_plot)):
                true_nevents_probs.append(float(
                    results["num_events_{0}_p".format(true_nevents[i])][indices_to_plot[i]]))
                map_nevents_probs.append(float(
                    results["num_events_{0}_p".format(map_nevents[i])][indices_to_plot[i]]))
            assert(len(true_nevents) == len(true_nevents_probs))
            assert(len(true_nevents) == len(map_nevents_probs))

            mean_true_nevents_prob = sum(true_nevents_probs) / len(true_nevents_probs)
            median_true_nevents_prob = pycoevolity.stats.median(true_nevents_probs)

            nevents_within_95_cred = 0
            # model_within_95_cred = 0
            ncorrect = 0
            for i in range(len(true_nevents)):
                true_map_nevents[map_nevents[i] - 1][true_nevents[i] - 1] += 1
                true_map_nevents_probs[map_nevents[i] - 1][true_nevents[i] - 1].append(map_nevents_probs[i])
                if true_nevents_cred_levels[i] <= 0.95:
                    nevents_within_95_cred += 1
                # if true_model_cred_levels[i] <= 0.95:
                #     model_within_95_cred += 1
                if true_nevents[i] == map_nevents[i]:
                    ncorrect += 1
            p_nevents_within_95_cred = nevents_within_95_cred / float(len(true_nevents))
            # p_model_within_95_cred = model_within_95_cred / float(len(true_nevents))
            p_correct = ncorrect / float(len(true_nevents))

            _LOG.info("p(nevents within CS) = {0:.4f}".format(p_nevents_within_95_cred))
            # _LOG.info("p(model within CS) = {0:.4f}".format(p_model_within_95_cred))
            ax = plt.subplot(gs[row_index, column_index])

            ax.imshow(true_map_nevents,
                    origin = 'lower',
                    cmap = cmap,
                    interpolation = 'none',
                    aspect = 'auto'
                    # extent = [0.5, 3.5, 0.5, 3.5]
                    )
            for i, row_list in enumerate(true_map_nevents):
                for j, num_events in enumerate(row_list):
                    ax.text(j, i,
                            str(num_events),
                            horizontalalignment = "center",
                            verticalalignment = "center",
                            size = number_font_size)
            if include_cs:
                ax.text(0.98, 0.02,
                        "\\scriptsize$p(k \\in \\textrm{{\\sffamily CS}}) = {0:.3f}$".format(
                                p_nevents_within_95_cred),
                        horizontalalignment = "right",
                        verticalalignment = "bottom",
                        transform = ax.transAxes)
            if include_prop_correct:
                ax.text(0.02, 0.98,
                        "\\scriptsize$p(\\hat{{k}} = k) = {0:.3f}$".format(
                                p_correct),
                        horizontalalignment = "left",
                        verticalalignment = "top",
                        transform = ax.transAxes)
            if include_median:
                ax.text(0.98, 0.98,
                        "\\scriptsize$\\widetilde{{p(k|\\mathbf{{D}})}} = {0:.3f}$".format(
                                median_true_nevents_prob),
                        horizontalalignment = "right",
                        verticalalignment = "top",
                        transform = ax.transAxes)
            if column_labels and (row_index == 0):
                col_header = column_labels[column_index]
                ax.text(0.5, 1.015,
                        col_header,
                        horizontalalignment = "center",
                        verticalalignment = "bottom",
                        transform = ax.transAxes)
            if row_labels and (column_index == (ncols - 1)):
                row_label = row_labels[row_index]
                ax.text(1.015, 0.5,
                        row_label,
                        horizontalalignment = "left",
                        verticalalignment = "center",
                        rotation = 270.0,
                        transform = ax.transAxes)

    # show only the outside ticks
    all_axes = fig.get_axes()
    for ax in all_axes:
        if not ax.is_last_row():
            ax.set_xticks([])
        if not ax.is_first_col():
            ax.set_yticks([])

    # show tick labels only for lower-left plot 
    all_axes = fig.get_axes()
    for ax in all_axes:
        # Make sure ticks correspond only with number of events
        ax.xaxis.set_ticks(range(number_of_comparisons))
        ax.yaxis.set_ticks(range(number_of_comparisons))
        if ax.is_last_row() and ax.is_first_col():
            xtick_labels = [item for item in ax.get_xticklabels()]
            for i in range(len(xtick_labels)):
                xtick_labels[i].set_text(str(i + 1))
            ytick_labels = [item for item in ax.get_yticklabels()]
            for i in range(len(ytick_labels)):
                ytick_labels[i].set_text(str(i + 1))
            ax.set_xticklabels(xtick_labels)
            ax.set_yticklabels(ytick_labels)
        else:
            xtick_labels = ["" for item in ax.get_xticklabels()]
            ytick_labels = ["" for item in ax.get_yticklabels()]
            ax.set_xticklabels(xtick_labels)
            ax.set_yticklabels(ytick_labels)

    # avoid doubled spines
    all_axes = fig.get_axes()
    for ax in all_axes:
        for sp in ax.spines.values():
            sp.set_visible(False)
            sp.set_linewidth(2)
        if ax.is_first_row():
            ax.spines['top'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
        else:
            ax.spines['bottom'].set_visible(True)
        if ax.is_first_col():
            ax.spines['left'].set_visible(True)
            ax.spines['right'].set_visible(True)
        else:
            ax.spines['right'].set_visible(True)

    fig.text(0.5, 0.001,
            "True number of events ($k$)",
            horizontalalignment = "center",
            verticalalignment = "bottom",
            size = 18.0)
    if y_label is None:
        y_label = "Estimated number of events ($\\hat{{k}}$)"
    fig.text(0.005, 0.5,
            y_label,
            horizontalalignment = "left",
            verticalalignment = "center",
            rotation = "vertical",
            size = 18.0)

    gs.update(left = pad_left,
            right = pad_right,
            bottom = pad_bottom,
            top = pad_top)

    plot_dir = os.path.join(project_util.ECOEVOLITY_SIM_DIR, "plots")
    if not os.path.exists(plot_dir):
        os.mkdir(plot_dir)
    if plot_file_prefix:
        plot_path = os.path.join(plot_dir,
                "{0}-nevents.pdf".format(plot_file_prefix))
    else:
        plot_path = os.path.join(plot_dir,
                "nevents.pdf")
    plt.savefig(plot_path)
    _LOG.info("Plots written to {0!r}\n".format(plot_path))

def generate_specific_model_plots(
        results,
        number_of_comparisons = 3,
        plot_title = None,
        include_x_label = True,
        include_y_label = True,
        include_median = True,
        include_cs = True,
        include_prop_correct = True,
        plot_width = 3.5,
        plot_height = 3.0,
        xy_label_size = 16.0,
        title_size = 16.0,
        pad_left = 0.2,
        pad_right = 0.99,
        pad_bottom = 0.18,
        pad_top = 0.9,
        lower_annotation_y = 0.02,
        upper_annotation_y = 0.92,
        plot_file_prefix = None):
    _LOG.info("Generating model plots...")

    cmap = truncate_color_map(plt.cm.binary, 0.0, 0.65, 100)

    plt.close('all')
    fig = plt.figure(figsize = (plot_width, plot_height))
    gs = gridspec.GridSpec(1, 1,
            wspace = 0.0,
            hspace = 0.0)

    true_map_nevents = []
    true_map_nevents_probs = []
    for i in range(number_of_comparisons):
        true_map_nevents.append([0 for i in range(number_of_comparisons)])
        true_map_nevents_probs.append([[] for i in range(number_of_comparisons)])
    true_nevents = tuple(int(x) for x in results["true_num_events"])
    map_nevents = tuple(int(x) for x in results["map_num_events"])
    true_nevents_cred_levels = tuple(float(x) for x in results["true_num_events_cred_level"])
    # true_model_cred_levels = tuple(float(x) for x in results["true_model_cred_level"])
    assert(len(true_nevents) == len(map_nevents))
    assert(len(true_nevents) == len(true_nevents_cred_levels))
    # assert(len(true_nevents) == len(true_model_cred_levels))

    true_nevents_probs = []
    map_nevents_probs = []
    for i in range(len(true_nevents)):
        true_nevents_probs.append(float(
            results["num_events_{0}_p".format(true_nevents[i])][i]))
        map_nevents_probs.append(float(
            results["num_events_{0}_p".format(map_nevents[i])][i]))
    assert(len(true_nevents) == len(true_nevents_probs))
    assert(len(true_nevents) == len(map_nevents_probs))

    mean_true_nevents_prob = sum(true_nevents_probs) / len(true_nevents_probs)
    median_true_nevents_prob = pycoevolity.stats.median(true_nevents_probs)

    nevents_within_95_cred = 0
    model_within_95_cred = 0
    ncorrect = 0
    for i in range(len(true_nevents)):
        true_map_nevents[map_nevents[i] - 1][true_nevents[i] - 1] += 1
        true_map_nevents_probs[map_nevents[i] - 1][true_nevents[i] - 1].append(map_nevents_probs[i])
        if true_nevents_cred_levels[i] <= 0.95:
            nevents_within_95_cred += 1
        # if true_model_cred_levels[i] <= 0.95:
        #     model_within_95_cred += 1
        if true_nevents[i] == map_nevents[i]:
            ncorrect += 1
    p_nevents_within_95_cred = nevents_within_95_cred / float(len(true_nevents))
    # p_model_within_95_cred = model_within_95_cred / float(len(true_nevents))
    p_correct = ncorrect / float(len(true_nevents))

    _LOG.info("p(nevents within CS) = {0:.4f}".format(p_nevents_within_95_cred))
    # _LOG.info("p(model within CS) = {0:.4f}".format(p_model_within_95_cred))
    ax = plt.subplot(gs[0, 0])

    ax.imshow(true_map_nevents,
            origin = 'lower',
            cmap = cmap,
            interpolation = 'none',
            aspect = 'auto'
            )
    for i, row_list in enumerate(true_map_nevents):
        for j, num_events in enumerate(row_list):
            ax.text(j, i,
                    str(num_events),
                    horizontalalignment = "center",
                    verticalalignment = "center")
    if include_cs:
        ax.text(0.98, lower_annotation_y,
                "$p(k \\in \\textrm{{\\sffamily CS}}) = {0:.3f}$".format(
                        p_nevents_within_95_cred),
                horizontalalignment = "right",
                verticalalignment = "bottom",
                transform = ax.transAxes)
    if include_prop_correct:
        ax.text(0.02, upper_annotation_y,
                "$p(\\hat{{k}} = k) = {0:.3f}$".format(
                        p_correct),
                horizontalalignment = "left",
                verticalalignment = "bottom",
                transform = ax.transAxes)
    if include_median:
        ax.text(0.98, upper_annotation_y,
                "$\\widetilde{{p(k|\\mathbf{{D}})}} = {0:.3f}$".format(
                        median_true_nevents_prob),
                horizontalalignment = "right",
                verticalalignment = "bottom",
                transform = ax.transAxes)
    if include_x_label:
        ax.set_xlabel("True \\# of events ($k$)",
                # labelpad = 8.0,
                fontsize = xy_label_size)
    if include_y_label:
        ax.set_ylabel("Estimated \\# of events ($\\hat{{k}}$)",
                labelpad = 8.0,
                fontsize = xy_label_size)
    if plot_title:
        ax.set_title(plot_title,
                fontsize = title_size)

    # Make sure ticks correspond only with number of events
    ax.xaxis.set_ticks(range(number_of_comparisons))
    ax.yaxis.set_ticks(range(number_of_comparisons))
    xtick_labels = [item for item in ax.get_xticklabels()]
    for i in range(len(xtick_labels)):
        xtick_labels[i].set_text(str(i + 1))
    ytick_labels = [item for item in ax.get_yticklabels()]
    for i in range(len(ytick_labels)):
        ytick_labels[i].set_text(str(i + 1))
    ax.set_xticklabels(xtick_labels)
    ax.set_yticklabels(ytick_labels)

    gs.update(
            left = pad_left,
            right = pad_right,
            bottom = pad_bottom,
            top = pad_top)

    plot_dir = os.path.join(project_util.ECOEVOLITY_SIM_DIR, "plots")
    if not os.path.exists(plot_dir):
        os.mkdir(plot_dir)
    plot_path = os.path.join(plot_dir,
            "{0}-nevents.pdf".format(plot_file_prefix))
    plt.savefig(plot_path)
    _LOG.info("Plots written to {0!r}\n".format(plot_path))


def parse_results(paths):
    return pycoevolity.parsing.get_dict_from_spreadsheets(
            paths,
            sep = "\t",
            offset = 0)


def main_cli(argv = sys.argv):

    cyrt_results = parse_results(glob.glob(
            os.path.join(project_util.ECOEVOLITY_SIM_DIR,
                    "cyrtodactylus-rate200",
                    "batch*",
                    "results.csv.gz")))
    cyrt_snp_results = parse_results(glob.glob(
            os.path.join(project_util.ECOEVOLITY_SIM_DIR,
                    "cyrtodactylus-rate200-unlinked-snps",
                    "batch*",
                    "results.csv.gz")))
    gekko_results = parse_results(glob.glob(
            os.path.join(project_util.ECOEVOLITY_SIM_DIR,
                    "gekko-rate2000",
                    "batch*",
                    "results.csv.gz")))
    gekko_snp_results = parse_results(glob.glob(
            os.path.join(project_util.ECOEVOLITY_SIM_DIR,
                    "gekko-rate2000-unlinked-snps",
                    "batch*",
                    "results.csv.gz")))

    row_labels = [
            "All sites",
            "Unlinked SNPs",
            ]
    column_labels = [
            "\\textit{{Cyrtodactylus}}",
            "\\textit{{Gekko}}",
            ]
    cyrt_comparison_labels = [
            ("Bohol0", "CamiguinSur0"),
            ("Palawan1", "Kinabalu1"),
            ("Samar2", "Leyte2"),
            ("Luzon3", "BabuyanClaro3"),
            ("Luzon4", "CamiguinNorte4"),
            ("Polillo5", "Luzon5"),
            ("Panay6", "Negros6"),
            ("Sibuyan7", "Tablas7"),
            ]
    gekko_comparison_labels = [
            ("BabuyanClaro8", "Calayan8"),
            ("SouthGigante9", "NorthGigante9"),
            ("Lubang11", "Luzon11"),
            ("Panay13", "Masbate13"),
            ("Negros14", "Panay14"),
            ("Sabtang15", "Batan15"),
            ("Romblon16", "Tablas16"),
            ("CamiguinNorte17", "Dalupiri17"),
            ]


    cyrt_height_parameters = []
    cyrt_root_size_parameters = []
    cyrt_leaf_size_parameters = []
    cyrt_height_ess_parameters = []
    cyrt_height_psrf_parameters = []
    for l1, l2 in cyrt_comparison_labels:
            cyrt_height_parameters.append("root_height_{0}".format(l1))
            cyrt_root_size_parameters.append("pop_size_root_{0}".format(l1))
            cyrt_leaf_size_parameters.append("pop_size_{0}".format(l1))
            cyrt_leaf_size_parameters.append("pop_size_{0}".format(l2))
            cyrt_height_ess_parameters.append("ess_sum_root_height_{0}".format(l1))
            cyrt_height_psrf_parameters.append("psrf_root_height_{0}".format(l1))

    gekko_height_parameters = []
    gekko_root_size_parameters = []
    gekko_leaf_size_parameters = []
    gekko_height_ess_parameters = []
    gekko_height_psrf_parameters = []
    for l1, l2 in gekko_comparison_labels:
            gekko_height_parameters.append("root_height_{0}".format(l1))
            gekko_root_size_parameters.append("pop_size_root_{0}".format(l1))
            gekko_leaf_size_parameters.append("pop_size_{0}".format(l1))
            gekko_leaf_size_parameters.append("pop_size_{0}".format(l2))
            gekko_height_ess_parameters.append("ess_sum_root_height_{0}".format(l1))
            gekko_height_psrf_parameters.append("psrf_root_height_{0}".format(l1))


    parameters_to_plot = {
            "event-time": {
                    "cyrt-headers": cyrt_height_parameters,
                    "gekko-headers": gekko_height_parameters,
                    "label": "event time",
                    "short_label": "time",
                    "symbol": "t",
                    "shared_axes": False,
            },
            "ancestor-size": {
                    "cyrt-headers": cyrt_root_size_parameters,
                    "gekko-headers": gekko_root_size_parameters,
                    "label": "ancestral population size",
                    "short_label": "size",
                    "symbol": "N_e\\mu",
                    "shared_axes": True,
            },
            "descendant-size": {
                    "cyrt-headers": cyrt_leaf_size_parameters,
                    "gekko-headers": gekko_leaf_size_parameters,
                    "label": "descendant population size",
                    "short_label": "size",
                    "symbol": "N_e\\mu",
                    "shared_axes": True,
            },
    }

    for parameter, p_info in parameters_to_plot.items():
        cyrt_data = ScatterData.init(cyrt_results,
                p_info["cyrt-headers"],
                highlight_parameter_prefix = "psrf",
                highlight_threshold = 1.1)
        cyrt_snp_data = ScatterData.init(cyrt_snp_results,
                p_info["cyrt-headers"],
                highlight_parameter_prefix = "psrf",
                highlight_threshold = 1.1)
        gekko_data = ScatterData.init(gekko_results,
                p_info["gekko-headers"],
                highlight_parameter_prefix = "psrf",
                highlight_threshold = 1.1)
        gekko_snp_data = ScatterData.init(gekko_snp_results,
                p_info["gekko-headers"],
                highlight_parameter_prefix = "psrf",
                highlight_threshold = 1.1)
        
        x_label = "True {0} (${1}$)".format(
                p_info["label"],
                p_info["symbol"])
        y_label = "Estimated {0} ($\\hat{{{1}}}$)".format(
                p_info["short_label"],
                p_info["symbol"])

        data_grid = [
                [cyrt_data, gekko_data],
                [cyrt_snp_data, gekko_snp_data],
                ]

        generate_scatter_plots(
                data_grid = data_grid,
                plot_file_prefix = parameter,
                parameter_symbol = p_info["symbol"],
                column_labels = column_labels,
                row_labels = row_labels,
                plot_width = 2.2,
                plot_height = 1.8,
                pad_left = 0.175,
                pad_right = 0.95,
                pad_bottom = 0.14,
                pad_top = 0.95,
                x_label = x_label,
                x_label_size = 18.0,
                y_label = y_label,
                y_label_size = 18.0,
                force_shared_x_range = p_info["shared_axes"],
                force_shared_y_range = p_info["shared_axes"],
                force_shared_xy_ranges = True,
                force_shared_spines = p_info["shared_axes"],
                include_coverage = True,
                include_rmse = True,
                include_identity_line = True,
                include_error_bars = True)


    results_grid = [
            [cyrt_results, gekko_results],
            [cyrt_snp_results, gekko_snp_results],
            ]
    generate_model_plots(
            results_grid = results_grid,
            column_labels = column_labels,
            row_labels = row_labels,
            number_of_comparisons = 8,
            plot_width = 2.0,
            plot_height = 1.8,
            pad_left = 0.14,
            pad_right = 0.95,
            pad_bottom = 0.14,
            pad_top = 0.94,
            y_label_size = 18.0,
            y_label = None,
            number_font_size = 8.0,
            include_median = False,
            include_cs = False,
            include_prop_correct = False,
            # filter_parameter_prefix = "psrf_pop_size",
            # filter_threshold = 1.02,
            plot_file_prefix = "")

    # generate_specific_model_plots(
    #         results = cyrt_results,
    #         number_of_comparisons = 8,
    #         plot_title = None,
    #         include_x_label = False,
    #         include_y_label = False,
    #         include_median = True,
    #         include_cs = True,
    #         include_prop_correct = True,
    #         plot_width = 3.5,
    #         plot_height = 3.3,
    #         xy_label_size = 16.0,
    #         title_size = 16.0,
    #         pad_left = 0.16,
    #         pad_right = 0.99,
    #         pad_bottom = 0.165,
    #         pad_top = 0.915,
    #         lower_annotation_y = 0.01,
    #         upper_annotation_y = 0.915,
    #         plot_file_prefix = "nevents-cyrt")

    # Generate histograms for the number of variable sites
    parameters = [
            "n_var_sites_c1",
            "n_var_sites_c2",
            "n_var_sites_c3",
            "n_var_sites_c4",
            "n_var_sites_c5",
            "n_var_sites_c6",
            "n_var_sites_c7",
            "n_var_sites_c8",
            ]
    cyrt_data = HistogramData.init(cyrt_results, parameters, True)
    gekko_data = HistogramData.init(gekko_results, parameters, True)
    
    data_grid = [
            [cyrt_data, gekko_data],
            ]

    generate_histograms(
            data_grid = data_grid,
            plot_file_prefix = "number-of-variable-sites",
            column_labels = column_labels,
            row_labels = None,
            parameter_label = "Number of variable sites",
            range_key = "range",
            number_of_digits = 0,
            plot_width = 1.9,
            plot_height = 2.0,
            pad_left = 0.08,
            pad_right = 0.99,
            pad_bottom = 0.2,
            pad_top = 0.90,
            force_shared_x_range = True,
            force_shared_bins = True,
            force_shared_y_range = True,
            force_shared_spines = True,
            )

    histograms_to_plot = {
            "number-of-variable-sites": {
                    "cyrt-headers": [
                            "n_var_sites_c1",
                            "n_var_sites_c2",
                            "n_var_sites_c3",
                            "n_var_sites_c4",
                            "n_var_sites_c5",
                            "n_var_sites_c6",
                            "n_var_sites_c7",
                            "n_var_sites_c8",
                    ],
                    "gekko-headers": [
                            "n_var_sites_c1",
                            "n_var_sites_c2",
                            "n_var_sites_c3",
                            "n_var_sites_c4",
                            "n_var_sites_c5",
                            "n_var_sites_c6",
                            "n_var_sites_c7",
                            "n_var_sites_c8",
                    ],
                    "label": "Number of variable sites",
                    "short_label": "No. variable sites",
                    "shared_axes": False,
                    "ndigits": 0,

            },
            "ess-ln-likelihood": {
                    "cyrt-headers": [
                            "ess_sum_ln_likelihood",
                    ],
                    "gekko-headers": [
                            "ess_sum_ln_likelihood",
                    ],
                    "label": "Effective sample size of log likelihood",
                    "short_label": "ESS of lnL",
                    "shared_axes": True,
                    "ndigits": 0,
            },
            "ess-event-time": {
                    "cyrt-headers": cyrt_height_ess_parameters,
                    "gekko-headers": gekko_height_ess_parameters,
                    "label": "Effective sample size of event time",
                    "short_label": "ESS of time",
                    "shared_axes": True,
                    "ndigits": 0,
            },
            "psrf-ln-likelihood": {
                    "cyrt-headers": [
                            "psrf_ln_likelihood",
                    ],
                    "gekko-headers": [
                            "psrf_ln_likelihood",
                    ],
                    "label": "PSRF of log likelihood",
                    "short_label": "PSRF of lnL",
                    "shared_axes": False,
                    "ndigits": 3,
            },
            "psrf-event-time": {
                    "cyrt-headers": cyrt_height_psrf_parameters,
                    "gekko-headers": gekko_height_psrf_parameters,
                    "label": "PSRF of event time",
                    "short_label": "PSRF of time",
                    "shared_axes": False,
                    "ndigits": 3,
            },
    }

    for parameter, p_info in histograms_to_plot.items():
        cyrt_data = HistogramData.init(cyrt_results, p_info["cyrt-headers"], False)
        cyrt_snp_data = HistogramData.init(cyrt_snp_results, p_info["cyrt-headers"], False)
        gekko_data = HistogramData.init(gekko_results, p_info["gekko-headers"], False)
        gekko_snp_data = HistogramData.init(gekko_snp_results, p_info["gekko-headers"], False)

        data_grid = [
                [cyrt_data, gekko_data],
                [cyrt_snp_data, gekko_snp_data],
                ]

        generate_histograms(
                data_grid = data_grid,
                plot_file_prefix = parameter,
                column_labels = column_labels,
                row_labels = row_labels,
                parameter_label = p_info["label"],
                range_key = "range",
                number_of_digits = p_info["ndigits"],
                plot_width = 2.2,
                plot_height = 1.9,
                pad_left = 0.15,
                pad_right = 0.95,
                pad_bottom = 0.14,
                pad_top = 0.94,
                force_shared_x_range = p_info["shared_axes"],
                force_shared_bins = False,
                force_shared_y_range = True,
                force_shared_spines = p_info["shared_axes"],
                )


if __name__ == "__main__":
    main_cli()
