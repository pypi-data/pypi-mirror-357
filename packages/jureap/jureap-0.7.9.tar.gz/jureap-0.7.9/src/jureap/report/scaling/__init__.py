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
import jureap.manual


def prepare_plotting_data(experiment_array):
    complete_plotting_data = {}
    complete_plotting_data["experiment"] = []

    for experiment in experiment_array:
        plotting_data = {}
        plotting_data["system"] = experiment.json_data()["experiment"]["system"]
        plotting_data["pipeline"] = experiment.pipeline()
        plotting_data["workload_factor"] = float(experiment.workload_factor())
        plotting_data["runtime"] = {}
        plotting_data["runtime"]["nodes"] = []
        plotting_data["runtime"]["runtime"] = []
        for data in experiment.json_data()["data"]:
            plotting_data["runtime"]["nodes"].append(int(data["parameter"]["nodes"]))
            plotting_data["runtime"]["runtime"].append(float(data["runtime"]))

            plotting_data["runtime"]["runtime"] = [
                x
                for _, x in sorted(
                    zip(plotting_data["runtime"]["nodes"], plotting_data["runtime"]["runtime"])
                )
            ]

            plotting_data["runtime"]["nodes"] = sorted(plotting_data["runtime"]["nodes"])

        plotting_data["label"] = experiment.prefix()

        complete_plotting_data["experiment"].append(plotting_data)

    min_nodes = sys.maxsize
    max_nodes = 0
    min_runtime = sys.float_info.max
    max_runtime = 0

    max_workload_factor = sys.float_info.max

    for pipeline_data in complete_plotting_data["experiment"]:
        local_max = max(pipeline_data["runtime"]["nodes"])
        local_min = min(pipeline_data["runtime"]["nodes"])
        min_nodes = min(min_nodes, local_min)
        max_nodes = max(max_nodes, local_max)
        local_max = max(pipeline_data["runtime"]["runtime"])
        local_min = min(pipeline_data["runtime"]["runtime"])
        min_runtime = min(min_runtime, local_min)
        max_runtime = max(max_runtime, local_max)

    complete_plotting_data["node_range"] = [0.5 * min_nodes, 1.4 * max_nodes]
    complete_plotting_data["runtime_range"] = [0.5 * min_runtime, 1.4 * max_runtime]

    workload_factor_array = [
        data["workload_factor"] for data in complete_plotting_data["experiment"]
    ]
    min_workload_factor = min(workload_factor_array)
    normalized_wf = [p / min_workload_factor for p in workload_factor_array]

    base_runtime = 0
    for index, pipeline_data in enumerate(complete_plotting_data["experiment"]):
        if min(pipeline_data["runtime"]["nodes"]) == min_nodes:

            min_node_index = min(
                range(len(pipeline_data["runtime"]["nodes"])),
                key=pipeline_data["runtime"]["nodes"].__getitem__,
            )

            base_runtime = pipeline_data["runtime"]["runtime"][min_node_index]

    for index, pipeline_data in enumerate(complete_plotting_data["experiment"]):
        pipeline_data["expected_runtime"] = {}
        pipeline_data["expected_runtime"]["nodes"] = pipeline_data["runtime"]["nodes"]
        pipeline_data["expected_runtime"]["runtime"] = [
            normalized_wf[index] * base_runtime / p * min_nodes
            for p in pipeline_data["runtime"]["nodes"]
        ]

    complete_plotting_data["base_runtime"] = base_runtime

    return complete_plotting_data


def generate_plot_pdf_file(plotting_data, output_dir, skip_weak_scaling, legend_position):
    with tempfile.TemporaryDirectory(dir=output_dir, delete=False) as tmpdir:
        print("Generating plot in " + tmpdir)
        for pipeline_data in plotting_data["experiment"]:
            system_name = pipeline_data["system"]
            xaxis_data = pipeline_data["runtime"]["nodes"]
            yaxis_data = pipeline_data["runtime"]["runtime"]
            label = pipeline_data["label"]
            csv_filename = os.path.join(tmpdir, label + ".csv")
            workload_factor_filename = os.path.join(tmpdir, label + ".workload")

            with open(csv_filename, "w") as csv_file:
                csv_file.write("nodes,runtime\n")
                for i in range(len(xaxis_data)):
                    csv_file.write(str(xaxis_data[i]) + "," + str(yaxis_data[i]) + "\n")

            with open(workload_factor_filename, "w") as wf_file:
                wf_file.write(str(pipeline_data["workload_factor"]))

        jureap.manual.generate(system_name, tmpdir, output_dir,
                               skip_weak_scaling, legend_position)

    return "plot.pdf"


def generate_plot_tex_file(experiment_array, output_dir, skip_weak_scaling, legend_position):
    plotting_data = prepare_plotting_data(experiment_array)
    pdf_filename = generate_plot_pdf_file(
        plotting_data, output_dir, skip_weak_scaling, legend_position
    )

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
        authorfile.write("\\title{Scaling Evaluation Report}\n")


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


def sort_csv_file(input_file, output_file):
    with open(input_file, "r") as input_csv:
        lines = input_csv.read().splitlines()[:-1]
        header = lines[0] + "\n"
        node_index = header.split(",").index("nodes")
        data = [line.strip().split(",") for line in lines[1:]]
        data.sort(key=lambda x: int(x[node_index]))
        with open(output_file, "w") as output_csv:
            output_csv.write(header)
            for line in data:
                output_csv.write(",".join(line) + "\n")


def copy_raw_data(input_dir, experiment_array, output_dir):
    data_dir = os.path.join(output_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    for experiment in experiment_array:
        output_experiment_reldir = experiment.pipeline() + str(".") + experiment.prefix()
        output_experiment_dir = os.path.join(data_dir, output_experiment_reldir)
        input_experiment_dir = os.path.join(input_dir, experiment.pipeline_dir())
        csv_filepath = os.path.join(input_experiment_dir, experiment.prefix() + ".csv")
        json_filepath = os.path.join(input_experiment_dir, experiment.prefix() + ".json")
        os.makedirs(output_experiment_dir, exist_ok=True)
        output_csv_file = os.path.join(output_experiment_dir, experiment.prefix() + ".csv")
        sort_csv_file(csv_filepath, output_csv_file)
        shutil.copy(json_filepath, output_experiment_dir)


def generate(
    input_dir, experiment_array, output_dir, share_dir, tmp_dir, skip_weak_scaling, legend_position
):
    prepare_report_dir(output_dir, share_dir)
    copy_raw_data(input_dir, experiment_array, output_dir)
    generate_plot_tex_file(experiment_array, output_dir, skip_weak_scaling, legend_position)
    generate_csv_table_tex_file(experiment_array, output_dir)
    generate_json_tex_file(experiment_array, output_dir)
    write_json_data(experiment_array, output_dir)
    generate_author_tex_file(output_dir)
    compile_report_pdf(output_dir)
