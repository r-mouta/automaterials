import math
import numpy as np
import palettable


def pretty_plot(
    width=8,
    height=None,
    plt=None,
    dpi=None,
    color_cycle=('qualitative', 'Set1_9'),
):
    """
    Provides a publication quality plot, with nice defaults for font sizes etc.

    Args:
        width (float): Width of plot in inches. Defaults to 8in.
        height (float): Height of plot in inches. Defaults to width * golden
            ratio.
        plt (matplotlib.pyplot): If plt is supplied, changes will be made to an
            existing plot. Otherwise, a new plot will be created.
        dpi (int): Sets dot per inch for figure. Defaults to 300.
        color_cycle (tuple): Set the color cycle for new plots to one of the
            color sets in palettable. Defaults to a qualitative Set1_9.

    Returns:
        Matplotlib plot object with properly sized fonts.
    """
    ticksize = int(width * 2.5)

    golden_ratio = (math.sqrt(5) - 1) / 2

    if not height:
        height = int(width * golden_ratio)

    if plt is None:
        import importlib

        import matplotlib.pyplot as plt

        mod = importlib.import_module(
            'palettable.colorbrewer.%s' % color_cycle[0]
        )
        colors = getattr(mod, color_cycle[1]).mpl_colors
        from cycler import cycler

        plt.figure(figsize=(width, height), facecolor='w', dpi=dpi)
        ax = plt.gca()
        ax.set_prop_cycle(cycler('color', colors))
    else:
        fig = plt.gcf()
        fig.set_size_inches(width, height)
    plt.xticks(fontsize=ticksize)
    plt.yticks(fontsize=ticksize)

    ax = plt.gca()
    ax.set_title(ax.get_title(), size=width * 4)

    labelsize = int(width * 3)

    ax.set_xlabel(ax.get_xlabel(), size=labelsize)
    ax.set_ylabel(ax.get_ylabel(), size=labelsize)

    return plt
