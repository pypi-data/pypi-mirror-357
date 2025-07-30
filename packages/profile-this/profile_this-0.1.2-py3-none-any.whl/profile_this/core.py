#!/usr/bin/env python3

__all__ = ["ProfileThis"]

from os import getpid
from threading import Thread
from time import sleep, time
from typing import Tuple

import matplotlib.pyplot as plt
from psutil import Process


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

    def _log(self):
        """Snapshots memory allocation and runtime according to some time interval."""

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

    def plot(
        self,
        title: str,
        path: str,
        color: str | None = None,
        figsize: Tuple[int, int] | None = None,
    ):
        """Plots runtime and memory allocation.

        Parameters
        ----------
        title : str
            The title of the plot.
        path : str
            Where to save the plot.
        color : str | None, optional
            The color of the line on the plot. Default is blue.
        figsize : Tuple[int, int] | None, optional
            The size of the ploat. Default is (10, 5).
        """

        color = "blue" if color is None else color
        figsize = (10, 5) if figsize is None else figsize
        plt.figure(figsize=figsize)
        plt.plot(self.timestamps, self.memory_mb, linewidth=2, color=color)
        plt.xlabel("Time (seconds)")
        plt.ylabel("Memory (MB)")
        plt.title(title)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(path)
