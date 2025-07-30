from aesthetic.plot import set_style

import numpy as np, matplotlib.pyplot as plt, matplotlib as mpl
import matplotlib.colors as mcolors
from cycler import cycler

def set_colors(style):
    base = plt.rcParams['axes.prop_cycle'].by_key()['color']
    if '_wob' in style:
        inverse = [tuple(1 - v for v in mcolors.to_rgb(c)) for c in base]
        plt.rcParams['axes.prop_cycle'] = cycler('color', inverse)
    else:
        pass

def make_plot(style):
    x = np.linspace(0,10,1000)
    y = (x/100)**3 + 5*np.sin(x)
    _x, _y = np.arange(2, 8, 0.5), np.arange(2, 8, 0.5)

    set_colors(style)
    fig, ax = plt.subplots(figsize=(3,2.5))
    ax.plot(x, y, label=f'style: {style}')
    ax.plot(x, y+3)
    ax.plot(x, y+6)
    _yerr = np.abs(np.random.normal(2, 1, _x.size))
    c = 'k' if '_wob' not in style else 'w'
    ax.errorbar(_x, _y, yerr=_yerr, marker='o', elinewidth=0.5, lw=0, c=c, markersize=2)
    ax.update({
        'xlabel': r'x [units]',
        'ylabel': r'y [units]',
    })
    ax.legend(fontsize='small')
    return fig

if __name__ == '__main__':
    styles = ['clean', 'science', 'clean_wob', 'science_wob']
    for style in styles:
        set_style(style)
        fig = make_plot(style)
        fig.savefig(f'../results/plot_{style}.png', bbox_inches='tight', dpi=400)
        mpl.rc_file_defaults()