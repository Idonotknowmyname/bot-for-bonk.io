import time
from collections import defaultdict, deque
import threading
import multiprocessing as mp
import atexit
import matplotlib.pyplot as plt


def mean(_list):
    return sum(_list) * 1. / len(_list)


def live_plotter(x_vec, y1_data, line1, identifier='', pause_time=0.1):
    if line1 == []:
        # this is the call to matplotlib that allows dynamic plotting
        plt.ion()
        fig = plt.figure(figsize=(13, 6))
        ax = fig.add_subplot(111)
        # create a variable for the line so we can later update it
        line1, = ax.plot(x_vec, y1_data, '-o', alpha=0.8)
        # update plot label/title
        plt.ylabel('Y Label')
        plt.title('Title: {}'.format(identifier))
        plt.show()

    # after the figure, axis, and line are created, we only need to update the y-data
    line1.set_ydata(y1_data)
    # adjust limits if new data goes beyond bounds
    if np.min(y1_data) <= line1.axes.get_ylim()[0] or np.max(y1_data) >= line1.axes.get_ylim()[1]:
        plt.ylim([np.min(y1_data)-np.std(y1_data), np.max(y1_data)+np.std(y1_data)])
    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)

    # return line so we can update it again in the next iteration
    return line1


def plot_function(queue, plt_every, ticker, window_size=100, rolling=30):
    plt.ion()
    f = plt.figure(figsize=(13, 6))
    ax_index = 111
    avg_periods = defaultdict(lambda: [None] * window_size)
    x = range(window_size)
    axes = {}
    lines = {}
    plt.show(block=False)

    last_time = time.time()
    while not ticker._thread_should_close:
        t = time.time()
        if t - last_time >= plt_every:
            # Get the average period for all values
            avg_period = ticker.average_period(rolling=rolling)
            print("Sampled avg period of ticks:", avg_period)
            # Add all new observations and change the data
            for key, val in avg_period.items():
                avg_periods[key] = avg_periods[key][1:] + [avg_period[key]]

                if key not in lines.keys():
                    axes[key] = ax = f.add_subplot(ax_index)
                    ax_index += 1
                    lines[key], = ax.plot(x, avg_periods[key], key)
                    plt.legend()

                avg_periods[key] = avg_periods[key][1:] + [avg_period[key]]

                lines[key].set_ydata(avg_periods[key])

            plt.draw()
            last_time = t
        else:
            time.sleep(0.1)


class Ticker:
    """ A ticker is like a chronometer on steroids, it ticks every lap, calculating average value, running std and other statistics.

    Usage:
        # Measure one component
        tk = Ticker()

        for i in range(1000):
            tk.tick("cv_pipeline")
            _ = cv_pipeline.run(last_frame)


        print(f"Average time taken to run the CV pipeline: {tk.average_period()}")

        # Measure multiple components independently

        tk = Ticker()

        for i in range(1000):
            tk["collect"].tick()
            event_coll._collect()
            tk["collect"].tock()

            tk["cv_pipeline"].tick()
            cv_pipeline.run(frame)
            tk["cv_pipeline"].tock()

        print(f"Average times: {tk.average_period()}")
    """

    def __init__(self, tick_tock=False, buffer_size=10000):

        self.last_ticked = None

        self.tick_tock = tick_tock

        if tick_tock:
            self.tick_tock_times = defaultdict(list)
        else:
            self.tick_times = defaultdict(list)

        self._thread = None
        self._thread_should_close = False
        self._thread_queue = None

    def tick(self, name="default"):
        if not self.tick_tock and self.last_ticked is not None:
            self.tick_times[name].append(time.time() - self.last_ticked)
            # print(f"Done the tick -> {name}:", self.tick_times[name])

        self.last_ticked = time.time()

    def tock(self, name="default"):
        assert self.tick_tock, "Should have creted the Ticker with tick_tock=True"
        t = time.time()
        self.tick_tock_times[name].append(t - self.last_ticked)

    def average_period(self, rolling=False):

        if self.tick_tock:
            arrs = self.tick_tock_times
        else:
            arrs = self.tick_times

        # If there is no data available yet, wait until it is
        # print(f"len(self.tick_tock_times) = {len(self.tick_tock_times)}, self.tick_tock_times = {self.tick_tock_times} ")
        print(f"len(self.tick_times) = {len(self.tick_times)}, self.tick_times = {self.tick_times} ")
        while len(arrs.keys()) > 0 and min([len(vals) for _, vals in arrs.items()]) < rolling:
            time.sleep(0.1)
            print("Waiting...")

        if rolling and type(rolling) is int and rolling > 0:

            return {name: mean(arrs[name][-rolling:]) for name in arrs.keys()}
        elif rolling == False:
            return {name: mean(arrs[name]) for name in arrs.keys()}

    def enable_statistics_plots(self, update_every_n_seconds=1., window_size=100, rolling_avg=30):

        self._thread_queue = q = mp.Queue()

        t = mp.Process(target=plot_function, args=(q, update_every_n_seconds, self, window_size, rolling_avg))
        # t.daemon = True
        t.start()

        self._thread = t
        atexit.register(t.terminate)

    def __del__(self):
        self._thread_should_close = True
        self._thread.terminate()


if __name__ == "__main__":
    import random

    t = Ticker()

    t.enable_statistics_plots()

    print("Starting...")
    for i in range(10000):
        if i % 100 == 0:
            print(i)
        t.tick()
        dt = (random.random() - 0.5) / 10.
        time.sleep(0.1 + dt)
