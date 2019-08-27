import matplotlib.pyplot as plt
import pandas as pd
from itertools import combinations
import numpy as np


def plots_dict(input_dict):
    """Create a dictionary of combinations of readers to create bar graphs"""
    # Getting the combinations of the formats
    # import pdb;pdb.set_trace()
    comb = combinations(input_dict.keys(), 2)
    x = list(comb)
    comp_values = {}
    for each in x:
        name = each[0].split("_")[0] + " vs " + each[1].split("_")[0]
        comp_values[name] = {}
        comp_values[name]["R0"] = []
        comp_values[name]["X0"] = []
        comp_values[name]["R1"] = []
        comp_values[name]["X1"] = []
        for (k, v), (k1, v1) in zip(
            input_dict[each[0]].items(), input_dict[each[1]].items()
        ):
            comp_values[name]["R0"].append(abs(v[0] - v1[0]))
            comp_values[name]["X0"].append(abs(v[1] - v1[1]))
            comp_values[name]["R1"].append(abs(v[2] - v1[2]))
            comp_values[name]["X1"].append(abs(v[3] - v1[3]))
    return comp_values


def plots(input_dict):
    """Create bar graphs"""
    comp_values = plots_dict(input_dict)
    fig, axes = plt.subplots(6, 4, figsize=(10, 7), sharex=True, sharey=True)
    plt.subplots_adjust(left=0, right=0.9, top=0.9, bottom=0.1)
    colors = ["tab:red", "tab:blue", "tab:green", "tab:pink"]
    y_pos = [0, 1, 2, 3]
    width = 0.2
    for row, comp_key in zip(axes, comp_values.keys()):
        for col, each_plot in zip(row, comp_values[comp_key].keys()):
            if col.is_first_col():
                col.set_ylabel(comp_key, rotation="horizontal", ha="right")
            if col.is_first_row():
                col.set_title(each_plot)
            v = comp_values[comp_key][each_plot]
            col.bar(y_pos, v, width, color="tab:blue")
            col.set_ylim(0, 15)
            # col.set_xticks(np.add(y_pos,(width/2))) # set the position of the x ticks
            # col.set_xticklabels(input_dict[x[0]].keys())

    # plt.suptitle('Differences of sequence impedances', size=14)
    fig.tight_layout()
    plt.show()
