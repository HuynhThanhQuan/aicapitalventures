import os
from pathlib import Path
import matplotlib.pyplot as plt


def plot_xy(x,y):
    fig, ax = plt.subplots()
    ax.plot(x, y, linewidth=2.0)
    plt.grid()
    plt.show()
