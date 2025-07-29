# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2024 Jayesh Badwaik <j.badwaik@fz-juelich.de>
# --------------------------------------------------------------------------------------------------

import itertools
import os
import tempfile
import shutil
import subprocess
import json
import sys
import matplotlib.pyplot
import math
import numpy
import jureap.detail
import glob


class MachineData:
    def __init__(self, name):
        self.name = name
        self._node_array = []
        self._runtime_array = []
        self.is_empty = True

    def add_data(self, nodes, runtime):
        if len(nodes) != 0:
            self.is_empty = False
        self._node_array = self._node_array + nodes
        self._runtime_array = self._runtime_array + runtime
        self._runtime_array = [x for _, x in sorted(zip(self._node_array, self._runtime_array))]
        self._node_array = sorted(self._node_array)

    def is_empty(self):
        return self.is_empty

    def name(self):
        return self.name

    def node_array(self):
        return self._node_array

    def runtime_array(self):
        return self._runtime_array


class ProcessedData:
    def __init__(self, machine_data):
        self.machine_data = machine_data
        self._name = machine_data.name
        if self._name == "jurecadc":
            node_scale_factor = 0.5
        elif self._name == "jedi":
            node_scale_factor = 1
        elif self._name == "juwelsbooster":
            node_scale_factor = 0.5
        else:
            raise ValueError("Unknown machine name")

        self._node_array = [p * node_scale_factor for p in machine_data.node_array()]
        self._runtime_array = machine_data.runtime_array()

    def name(self):
        return self._name

    def node_array(self):
        return self._node_array

    def runtime_array(self):
        return self._runtime_array

    def ideal_scaling(self):
        return [self._runtime_array[0] / p * self._node_array[0] for p in self._node_array]

    def low_scaling(self):
        return [p * 1.25 for p in self.ideal_scaling()]


def experiment_to_data(experiment):
    nodes = [int(p["parameter"]["nodes"]) for p in experiment.json_data()["data"]]
    runtime = [float(p["runtime"]) for p in experiment.json_data()["data"]]
    return {"nodes": nodes, "runtime": runtime}


def aggregate_data(experiment_array):
    aggregate = {}
    aggregate["jurecadc"] = MachineData("jurecadc")
    aggregate["jedi"] = MachineData("jedi")
    aggregate["juwelsbooster"] = MachineData("juwelsbooster")

    for experiment in experiment_array:
        data = experiment_to_data(experiment)
        if experiment.json_data()["experiment"]["system"] == "jurecadc":
            aggregate["jurecadc"].add_data(data["nodes"], data["runtime"])
        elif experiment.json_data()["experiment"]["system"] == "jedi":
            aggregate["jedi"].add_data(data["nodes"], data["runtime"])
        elif experiment.json_data()["experiment"]["system"] == "juwelsbooster":
            aggregate["juwelsbooster"].add_data(data["nodes"], data["runtime"])

    return aggregate


def aggregate_to_processed_data(aggregate):
    processed_data = []
    for name, machine_data in aggregate.items():
        if not machine_data.is_empty:
            processed_data.append(ProcessedData(machine_data))

    return processed_data


def compute_plot_range_limits(processed_data):
    range_limits = {}
    range_limits["xlim"] = [sys.maxsize, 0]
    range_limits["ylim"] = [sys.maxsize, 0]
    range_limits["xticks"] = []
    for data in processed_data:
        range_limits["xlim"][0] = min(range_limits["xlim"][0], min(data.node_array()))
        range_limits["xlim"][1] = max(range_limits["xlim"][1], max(data.node_array()))
        range_limits["ylim"][0] = min(range_limits["ylim"][0], min(data.runtime_array()))
        range_limits["ylim"][1] = max(range_limits["ylim"][1], max(data.runtime_array()))
        range_limits["ylim"][0] = min(range_limits["ylim"][0], min(data.ideal_scaling()))
        range_limits["ylim"][1] = max(range_limits["ylim"][1], max(data.low_scaling()))
        range_limits["xticks"] = range_limits["xticks"] + data.node_array()

    range_limits["xlim"] = [0.75 * range_limits["xlim"][0], 1.25 * range_limits["xlim"][1]]
    range_limits["ylim"] = [0.9 * range_limits["ylim"][0], 1.1 * range_limits["ylim"][1]]
    range_limits["xticks"] = sorted(list(set(range_limits["xticks"])))

    # last_position = 0
    # reduced_node_array = [range_limits["xticks"][0]]
    # for i in range(len(range_limits["xticks"]) - 1):
    #    if range_limits["xticks"][i + 1] / range_limits["xticks"][i] > 1.1:
    #        reduced_node_array.append(range_limits["xticks"][i])

    # if max(range_limits["xticks"]) not in reduced_node_array:
    #    reduced_node_array.append(max(range_limits["xticks"]))

    # if reduced_node_array[-2] / reduced_node_array[-1] < 1.5:
    #    reduced_node_array.pop(-2)

    # range_limits["xticks"] = reduced_node_array

    range_limits["xticks"] = [0.5 if p == 0.5 else int(p) for p in range_limits["xticks"]]

    if math.log(range_limits["ylim"][0]) < 0 or math.log(range_limits["ylim"][1]) < 0:
        range_limits["yticks"] = numpy.linspace(
            range_limits["ylim"][0], range_limits["ylim"][1], num=8
        )
    else:
        range_limits["yticks"] = numpy.logspace(
            math.log(range_limits["ylim"][0], 2),
            math.log(range_limits["ylim"][1], 2),
            num=8,
            base=2,
        )
        range_limits["yticks"] = [int(p) for p in range_limits["yticks"]]

    return range_limits


def prepare_plotting_data(experiment_array):
    aggregate = aggregate_data(experiment_array)
    processed_data = aggregate_to_processed_data(aggregate)

    plotting_data = {}
    plotting_data["data"] = []
    plotting_data["plot_param"] = {}
    plotting_data["plot_param"]["range_limits"] = compute_plot_range_limits(processed_data)

    for data in processed_data:
        plotting_data["data"].append(
            {
                "name": data.name(),
                "nodes": data.node_array(),
                "runtime": data.runtime_array(),
                "ideal_scaling": data.ideal_scaling(),
                "low_scaling": data.low_scaling(),
            }
        )

    return plotting_data


def map_machine_name_to_plot_label(machine_name):
    if machine_name == "jurecadc":
        return "JURECA-DC"
    elif machine_name == "jedi":
        return "JEDI"
    elif machine_name == "juwelsbooster":
        return "JUWELS Booster"
    else:
        raise ValueError("Unknown machine name")


def generate_plot_pdf_file(plotting_data, output_dir):
    plot = matplotlib.pyplot.figure()
    marker_array = itertools.cycle(("o", "^", "s", "X"))
    cmap = matplotlib.colormaps["tab10"]
    colorgen = iter([cmap(i) for i in range(len(plotting_data["data"]))])

    ax = plot.subplots()
    ax.set_xlabel("Number of JEDI Nodes  (log-scale)")
    ax.set_ylabel("Runtime / s   (log-scale)")
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.margins(2)
    ax.set_xlim(plotting_data["plot_param"]["range_limits"]["xlim"])
    ax.set_ylim(plotting_data["plot_param"]["range_limits"]["ylim"])
    ax.grid(visible=True, which="major", axis="x", linestyle="-", linewidth=0.5, alpha=0.5)
    ax.tick_params(
        axis="both", which="minor", labelbottom=False, labelleft=False, bottom=False, left=False
    )

    ax_t = ax.secondary_xaxis("top")
    ax_t.minorticks_off()
    ax_t.set_xticks(plotting_data["plot_param"]["range_limits"]["xticks"])
    ax_t.set_xticklabels([2 * i for i in plotting_data["plot_param"]["range_limits"]["xticks"]])

    if "juwelsbooster" in [data["name"] for data in plotting_data["data"]] and "jurecadc" in [
        data["name"] for data in plotting_data["data"]
    ]:
        ax_t.set_xlabel("Number of JURECA/JUWELS Booster Nodes  (log-scale)")
    elif "juwelsbooster" in [data["name"] for data in plotting_data["data"]] and "jurecadc" not in [
        data["name"] for data in plotting_data["data"]
    ]:
        ax_t.set_xlabel("Number of JUWELS Booster Nodes  (log-scale)")
    else:
        ax_t.set_xlabel("Number of JURECA-DC Nodes  (log-scale)")

    ax.set_xlim(plotting_data["plot_param"]["range_limits"]["xlim"])
    ax.set_ylim(plotting_data["plot_param"]["range_limits"]["ylim"])
    ax.set_xticks(plotting_data["plot_param"]["range_limits"]["xticks"])
    ax.set_yticks(plotting_data["plot_param"]["range_limits"]["yticks"])
    ax.set_xticklabels(plotting_data["plot_param"]["range_limits"]["xticks"])
    ax.set_yticklabels(plotting_data["plot_param"]["range_limits"]["yticks"])
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:.1f}"))

    for data in plotting_data["data"]:
        color = next(colorgen)
        marker = next(marker_array)
        ax.plot(
            data["nodes"],
            data["runtime"],
            color=color,
            label=map_machine_name_to_plot_label(data["name"]),
            marker=marker,
            markersize=8,
        )

        ax.plot(
            data["nodes"],
            data["ideal_scaling"],
            color=color,
            linestyle="--",
            linewidth=0.6,
            alpha=1,
        )

        ax.plot(
            data["nodes"], data["low_scaling"], color=color, linestyle="--", linewidth=0.6, alpha=1
        )

    ax.plot(
        [0],
        [0],
        label="80% parallel efficiency intervals",
        alpha=1,
        ls="--",
        color="grey",
    )

    plot.legend(bbox_to_anchor=(0.58, 0.32))

    pdf_file = os.path.join(output_dir, "plot.pdf")
    png_file = os.path.join(output_dir, "plot.png")

    plot.savefig(pdf_file, bbox_inches="tight")
    plot.savefig(png_file, bbox_inches="tight")
    return "plot.pdf"


def generate_plot_tex_file(experiment_array, output_dir):
    plotting_data = prepare_plotting_data(experiment_array)
    pdf_filename = generate_plot_pdf_file(plotting_data, output_dir)

    plotfilename = os.path.join(output_dir, "plot.tex")

    with open(plotfilename, "w") as plotfile:
        plotfile.write("% This file was generated by jureap.\n")
        plotfile.write("\\exacbplot{" + pdf_filename + "}{Caption}\n")


def generate_csv_table_tex_file(experiment_array, output_dir):
    tablefilename = os.path.join(output_dir, "table.tex")
    with open(tablefilename, "w") as tablefile:
        tablefile.write("% This file was generated by jureap.\n")

        for experiment in experiment_array:
            csv_file = os.path.join(
                "data", experiment.output_pipeline_dir(), experiment.prefix() + ".csv"
            )
            tablefile.write("\\exacbtable{" + csv_file + "}{Caption}\n")


def generate_json_tex_file(experiment_array, output_dir):
    jsonfilename = os.path.join(output_dir, "json.tex")
    with open(jsonfilename, "w") as jsonfile:
        jsonfile.write("% This file was generated by jureap.\n")

        for experiment in experiment_array:
            json_file = os.path.join(
                "data", experiment.output_pipeline_dir(), experiment.prefix() + ".json"
            )
            jsonfile.write("\\lstinputlisting[caption=Caption]{" + json_file + "}\n")


def generate_author_tex_file(output_dir):
    authorfilename = os.path.join(output_dir, "author.tex")
    with open(authorfilename, "w") as authorfile:
        authorfile.write("% This file was generated by jureap.\n")
        authorfile.write("\\title{JEDI Evaluation Report}\n")


def compile_report_pdf(output_dir):
    subprocess.run(["make", "debug"], cwd=output_dir, env=os.environ)


def prepare_report_dir(output_dir, share_dir):
    texdir = os.path.join(share_dir, "jureap/tex/jedi")
    shutil.copytree(texdir, output_dir)


def write_json_data(experiment_array, output_dir):
    json_dir = os.path.join(output_dir, "json")
    os.makedirs(json_dir, exist_ok=True)
    for experiment in experiment_array:
        json_filepath = os.path.join(
            json_dir, experiment.pipeline() + "." + experiment.prefix() + ".json"
        )
        with open(json_filepath, "w") as jsonfile:
            json.dump(experiment.json_repr(), jsonfile, indent=4)


def copy_raw_data(input_dir, experiment_array, output_dir):
    data_dir = os.path.join(output_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    for experiment in experiment_array:
        output_experiment_reldir = experiment.pipeline() + str(".") + experiment.prefix()
        output_experiment_dir = os.path.join(data_dir, output_experiment_reldir)
        input_experiment_dir = os.path.join(input_dir, experiment.pipeline_dir())
        csv_filepath = os.path.join(input_experiment_dir, experiment.prefix() + ".csv")
        json_filepath = os.path.join(input_experiment_dir, experiment.prefix() + ".json")
        energy_dirpath = os.path.join(input_experiment_dir, experiment.prefix() + ".energy")
        os.makedirs(output_experiment_dir, exist_ok=True)
        if os.path.exists(energy_dirpath):
            shutil.copytree(energy_dirpath, os.path.join(output_experiment_dir, "energy"))
        shutil.copy(csv_filepath, output_experiment_dir)
        shutil.copy(json_filepath, output_experiment_dir)


def compute_node_energy(energy_dir):
    file_list = glob.glob(os.path.join(energy_dir, "energy.*.csv"))
    same_node_file_list = {}

    for file in file_list:
        split_file_string = os.path.basename(file).split(".")
        name = ".".join(split_file_string[0:1])
        pid = split_file_string[-2]
        node = ".".join(split_file_string[2:-2])
        if node not in same_node_file_list:
            same_node_file_list[node] = [file]
        else:
            same_node_file_list[node].append(file)

    total_energy = 0

    for node in same_node_file_list:
        file_data = jureap.detail.csv_file_to_array(same_node_file_list[node][0])
        sanitized_file_data = []
        for index, data in enumerate(file_data):
            data["sensor"] = data[""]
            del data[""]
            sanitized_file_data.append(data)

        for data in sanitized_file_data:
            if "pynvml" in data["sensor"]:
                total_energy = total_energy + float(data["0"])

    return total_energy


def extract_experiment_energy_info(energy_dir):
    experiment_energy_info = {}
    experiment_energy_info["node"] = []
    experiment_energy_info["energy"] = []
    for directory in os.listdir(energy_dir):
        node = int(directory)
        energy = compute_node_energy(os.path.join(energy_dir, directory))
        experiment_energy_info["node"].append(node)
        experiment_energy_info["energy"].append(energy)

    return experiment_energy_info


def generate_energy_plot(experiment_array, output_dir):
    experiment_energy_info_array = []
    for experiment in experiment_array:
        energy_dir = os.path.join(
            output_dir, "data", experiment.pipeline() + str(".") + experiment.prefix(), "energy"
        )
        experiment_energy_info = extract_experiment_energy_info(energy_dir)
        experiment_energy_info["system"] = experiment.json_data()["reporter"]["info"]["system"]
        experiment_energy_info_array.append(experiment_energy_info)

    generate_energy_plot_file(experiment_energy_info_array, output_dir)


def generate_energy_plot_file(experiment_energy_info_array, output_dir):
    plot = matplotlib.pyplot.figure()
    marker_array = itertools.cycle(("o", "^", "s", "X"))
    cmap = matplotlib.colormaps["tab10"]

    ax = plot.subplots()
    ax.set_xlabel("Number of JEDI Nodes  (log-scale)")
    ax.set_ylabel("Runtime / s   (log-scale)")
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.margins(2)
    ax.grid(visible=True, which="major", axis="x", linestyle="-", linewidth=0.5, alpha=0.5)
    ax.tick_params(
        axis="both", which="minor", labelbottom=False, labelleft=False, bottom=False, left=False
    )

    ax_t = ax.secondary_xaxis("top")
    ax_t.minorticks_off()
    ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.2f'))

    min_val = 10**9
    max_val = 0
    for experiment in experiment_energy_info_array:
        if experiment["system"] == "jedi":
            ax.set_xticks(experiment["node"])
            ax.set_xticklabels(experiment["node"])
            ax_t.set_xticks(experiment["node"])
            ax_t.set_xticklabels([2 * i for i in experiment["node"]])

            ax.set_xlim([0.8 * min(experiment["node"]), 1.2 * max(experiment["node"])])

        min_val = min(min_val, min(experiment["energy"]))
        max_val = max(max_val, max(experiment["energy"]))

        sorted_energy = [x for _, x in sorted(zip(experiment["node"], experiment["energy"]))]
        sorted_node = sorted(experiment["node"])

        marker = next(marker_array)
        data = experiment
        ax.plot(sorted_node, sorted_energy, label=data["system"], marker=marker, markersize=8)

    ax.set_ylim([0.8 * min_val, 1.2 * max_val])
    yticks = numpy.logspace(
        math.log(min_val, 2),
        math.log(max_val, 2),
        num=8,
        base=2,
    )
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks)

    plot.legend(bbox_to_anchor=(0.58, 0.32))

    pdf_file = os.path.join(output_dir, "energy.pdf")
    png_file = os.path.join(output_dir, "energy.png")

    plot.savefig(pdf_file, bbox_inches="tight")
    plot.savefig(png_file, bbox_inches="tight")
    return "energy.pdf"


def generate(input_dir, experiment_array, output_dir, share_dir, tmp_dir):
    prepare_report_dir(output_dir, share_dir)
    copy_raw_data(input_dir, experiment_array, output_dir)
    # generate_energy_plot(experiment_array, output_dir)
    generate_plot_tex_file(experiment_array, output_dir)
    generate_csv_table_tex_file(experiment_array, output_dir)
    generate_json_tex_file(experiment_array, output_dir)
    write_json_data(experiment_array, output_dir)
    generate_author_tex_file(output_dir)
    compile_report_pdf(output_dir)
