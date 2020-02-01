import argparse
import os

import matplotlib.pyplot as plt
import numpy as np

def plot_transfer_scores(output_path, exp_name, exp_path, show_plots):

    if not output_path:
        output_path = exp_path


    results = []
    titles = []
    plt.figure(figsize=(10, 5))

    for (dirpath, dirnames, filenames) in os.walk(exp_path):
        for run in filenames:
            if "domain_rand_rew" in run:
                titles.append(dirpath.split("/")[-1][0:5])
                results.append(np.mean(np.load(os.path.join(dirpath, run))))

    xrange = np.arange(len(results))
    plt.bar(xrange, results)
    plt.xticks(range(len(titles)), titles)
    if show_plots:
        plt.show()
    with open('{}/{}_{}.png'.format(output_path, exp_name, "domain_rand_transfer"),'wb') as result_plot:
        plt.savefig(result_plot)


    results = []
    titles = []
    plt.figure(figsize=(10, 5))
    for (dirpath, dirnames, filenames) in os.walk(exp_path):
        for run in filenames:
            if "base_sweep_rew" in run:
                titles.append(dirpath.split("/")[-1][0:5])
                results.append(np.mean(np.load(os.path.join(dirpath, run))))

    xrange = np.arange(len(results))
    plt.bar(xrange, results)
    plt.xticks(range(len(titles)), titles)
    if show_plots:
        plt.show()
    with open('{}/{}_{}.png'.format(output_path, exp_name, "base_score"),'wb') as result_plot:
        plt.savefig(result_plot)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('experiment_path', type=str, help='Pass the path to the folder containing all your results files')
    parser.add_argument('--output_path', type=str, help='Output file location.')
    parser.add_argument('--base_experiment', required=False, type=str, help='subtract this experiment\'s heatmap from the others before taking the mean\
                                                                            if folder, find best base')
    parser.add_argument('--show_plots', action="store_true", help='Show plots as they are created.')
    args = parser.parse_args()

    plot_transfer_scores(args.output_path, os.path.basename(args.experiment_path), args.experiment_path, args.show_plots)