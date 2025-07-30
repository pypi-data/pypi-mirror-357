#!/usr/bin/env python3

__all__ = ["ProfileThis", "profilethis"]

from functools import wraps
from os import getpid
from threading import Thread
from time import sleep, time

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import mplcyberpunk
from psutil import Process
from seaborn import lineplot


class ProfileThis:
    """Logs runtime and memory allocation.

    Parameters
    ----------
    interval : float, optional
        How often to snapshot memory. Default is 0.1.
    """

    def __init__(self, interval: float | None = None):
        self.interval = 0.1 if interval is None else interval
        self.running = False
        self.timestamps = []
        self.memory_mb = []

    def __enter__(self) -> "ProfileThis":
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        self.clear()

    def _log(self):
        """Snapshots memory allocation and runtime according to some
        time interval.
        """

        process = Process(getpid())
        start_time = time()

        while self.running:
            now = time()
            rss = process.memory_info().rss / 1024**2
            self.timestamps.append(now - start_time)
            self.memory_mb.append(rss)
            sleep(self.interval)

    def start(self):
        """Starts memory profiling."""

        self.running = True
        self.thread = Thread(target=self._log, daemon=True)
        self.thread.start()

    def stop(self):
        """Stops memory profiling."""

        self.running = False
        self.thread.join()

    def clear(self):
        """Clears the timestamps and memory_mb attributes."""

        self.timestamps = []
        self.memory_mb = []
        self.running = False

    def plot(self, title: str, path: str):
        """Plots runtime and memory allocation.

        Parameters
        ----------
        title : str
            The title of the plot.
        path : str
            Where to save the plot.
        """

        color = "#FF0000FF"
        plt.style.use("cyberpunk")
        plt.rcParams.update(
            {
                "figure.facecolor": "none",
                "axes.facecolor": "none",
                "savefig.transparent": True,
                "text.color": color,
                "axes.labelcolor": color,
                "xtick.color": color,
                "ytick.color": color,
                "axes.edgecolor": color,
                "grid.color": "none",
            }
        )
        plt.figure(figsize=(10, 5), dpi=100)
        lineplot(x=self.timestamps, y=self.memory_mb, color=color)
        plt.title(title, weight="bold", fontsize=14).set_path_effects(
            [
                path_effects.Stroke(linewidth=1, foreground="red"),
                path_effects.Normal(),
            ]
        )
        plt.xlabel(
            "Time (seconds)", weight="bold", fontsize=10
        ).set_path_effects(
            [
                path_effects.Stroke(linewidth=1, foreground="red"),
                path_effects.Normal(),
            ]
        )
        plt.ylabel("Memory (MB)", weight="bold", fontsize=10).set_path_effects(
            [
                path_effects.Stroke(linewidth=1, foreground="red"),
                path_effects.Normal(),
            ]
        )
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.tight_layout()
        mplcyberpunk.add_glow_effects()
        plt.savefig(path)


def profilethis(title: str, path: str, interval: float | None = None):
    """Decorator that plots runtime and memory allocation.

    Parameters
    ----------
    title : str
        The title of the plot.
    path : str
        Where to save the plot.
    interval : float, optional
        How often to snapshot memory. Default is 0.1.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(
            *args,
            **kwargs,
        ):
            with ProfileThis(interval=interval) as profiler:
                result = func(*args, **kwargs)
                profiler.plot(title=title, path=path)
                return result

        return wrapper

    return decorator
