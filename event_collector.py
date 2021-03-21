import time
import threading
import io
import cv2 as cv
from collections import defaultdict
from enum import Enum

from PIL import Image
import numpy as np

CV_PIPELINE = {"states": {
    "is_dead": None,
    "game_over": None,
    "player_wins": None,
    "player_loses": None,
},
    "masks": {
}}

# This parameters dictates how long in seconds the event is_dead should be active for before deeming the player dead
IS_DEAD_N_SECONDS = 1.

# This parameters dictates how long in seconds the event game_over should be active for before deeming the player game over
IS_GAME_OVER_N_SECONDS = 1.

# This parameter represents the number across which to average the past values of a status to get the truth value and detect value switches robustly
N_SECONDS_STATUS_AVERAGE = 1.

# How long in second, after a confirmed robust (smoothed) state change, another one can occur (to avoid states switching too fast and there being bullshit events)
STATES_UPDATE_COOLDOWN = 0.3


def get_timed_element_from_last_n_seconds(n_seconds, timed_elements):
    now = time.time()
    i = 0
    t = None
    for i in range(len(timed_elements)):
        t, _ = timed_elements[-i-1]
        if now - t > n_seconds:
            break

    if i == 0:
        # The first element is already very old
        print(
            f"(get_timed_element_from_last_n_seconds) -> WARNING: the last element of the list is already more than n seconds in the past, data is stale:\n\tage: {now - t:.3f}sec\n\tn_seconds: {n_seconds}")
        # Return the last element only to not break
        return timed_elements[-1:]
    else:
        return timed_elements[-i:]


def get_mode(elem_list):
    assert len(elem_list) > 0, "Elem list is empty"

    # Assumes each element is hashable
    highest_elem = None
    highest_count = -1e9
    counts = defaultdict(lambda: 0)

    for elem in elem_list:
        counts[elem] += 1
        if counts[elem] > highest_count:
            highest_count = counts[elem]
            highest_elem = elem

    return highest_elem


class Event(str, Enum):
    PLAYER_DIED = 'player_died'
    GAME_ENDED = 'game_ended'
    PLAYER_WON = 'player_won'
    PLAYER_LOST = 'player_won'
    GAME_STARTED = 'game_started'


class EventCollector:
    """ This object takes a screenshot from the game at a specified interval (default 0.1s), and then it runs a Computer Vision pipeline generating boolean values about the state of the game.
        The aim of the class is to smoothen out the measured values from the pipeline and to generate events based on changes of the underlying bonk.io game."""

    def __init__(self, browser, collect_every=0.1, n_frames=5):
        self.browser = browser
        self.collect_every = collect_every
        self.n_frames = n_frames

        self.previous_frames = []
        self.frames_lock = threading.Lock()

        self.previous_masks = {}
        for mask_name in CV_PIPELINE['masks'].keys():
            self.previous_masks[mask_name] = []

        self.previous_states = {}
        self.last_smoothed_state = {}
        self.last_state_updated = {}
        self.states_lock = threading.Lock()
        for status_name in CV_PIPELINE['states'].keys():
            self.previous_states[status_name] = []
            self.last_smoothed_state[status_name] = None
            self.last_state_updated[status_name] = -1e9

        self.stop = False

        self.accumulated_events = []

    def run_thread(self):
        """ Method to be run as a tread continuously, at more or less fixed time intervals it collects the screenshot, runs the CV pipeline and it updates the internal list of events to report. """
        last_collected = -1e9

        while not self.stop:
            if time.time() - last_collected > self.collect_every:
                self._collect()
                last_collected = time.time()

                self._run_cv_pipeline()

                self._update_internal_event_list()

    def get_events(self):
        """ Main method to access the events produce by this collector"""
        raise NotImplementedError()

    def _collect(self):
        try:
            element = self.browser.find_element_by_id('gamerenderer')
        except Exception as e:
            print(f"WARNING: error when finding the game rendered element:", str(e))

        buff = io.BytesIO(element.screenshot_as_png)
        arr = np.array(Image.open(buff))
        with self.frames_lock:
            self.previous_frames.append((time.time(), arr))

    def _run_cv_pipeline(self):
        t, last_frame = self.previous_frames[-1]

        for status_name, status_fn in CV_PIPELINE['states'].items():
            status_flag = status_fn(last_frame)
            self.previous_states[event_name].append((t, status_flag))

        with self.frames_lock:
            for mask_name, mask_fn in CV_PIPELINE['masks'].items():
                mask = mask_fn(last_frame)
                self.previous_masks[mask].append((t, mask))

    def get_last_n_frames(self):
        """ Returns the last self.n_frames (contains the time when it was retrieved in seconds) collected and the last n masks generated for each mask function in CV_PIPELINE on the past frames """
        frames = None
        mask_frames = None
        with self.frames_lock:
            frames = self.previous_frames[-self.n_frames:]
            mask_frames = {mask_name: vals[-self.n_frames:] for mask_name, vals in self.previous_masks}

            self.previous_frames = [*frames]

            for mask_name in self.previous_masks.keys():
                self.previous_masks[mask_name] = self.previous_masks[mask_name][-self.n_frames:]

        return frames, mask_frames

    def get_accumulated_events(self):
        """ Return the accumulated events from last time this method was called"""
        events = self.accumulated_events

        self.accumulated_events = []

        return events

    def _update_internal_event_list(self):

        events = []
        state_switch = {}
        now = time.time()

        # For each of the states (boolean) detected by the CV pipeline, do an average over the last N_SECONDS_STATUS_AVERAGE seconds and potentially register a state switch
        for status_name in CV_PIPELINE['states'].keys():
            # Get the averaging result over the values in the last N_SECONDS_STATUS_AVERAGE
            states_to_avg = get_timed_element_from_last_n_seconds(N_SECONDS_STATUS_AVERAGE, self.previous_states[status_name])

            avg_state = get_mode([val for _, val in states_to_avg])

            if avg_state != self.last_smoothed_state[status_name] and now - self.last_state_updated[status_name] > STATES_UPDATE_COOLDOWN:
                # Only if the previous smoothed value was not None then a status switch happened
                if self.last_smoothed_state[status_name] is not None:
                    # State is switched!
                    state_switch[status_name] = avg_state

                self.last_smoothed_state[status_name] = avg_state
                self.last_state_updated[status_name] = now

        # Produces new events by looking at the states_switch object
        with self.states_lock:
            # Check if the player died
            if state_switch.get('is_dead', default=False):
                events.append(Event.PLAYER_DIED)

            # Check if bonk.io game ended for everyone
            if state_switch.get('game_over', default=False):
                events.append(Event.GAME_OVER)

            # Check if bonk.io game just started for everyone
            if not state_switch.get('game_over', default=True):
                events.append(Event.GAME_STARTED)

            # Check if the screen with the player winning just showed up
            if state_switch.get('player_wins', default=False):
                events.append(Event.PLAYER_WON)

            # Check if the screen with the opponent winning just showed up
            if state_switch.get('player_loses', default=False):
                events.append(Event.PLAYER_LOST)

        self.accumulated_events.extend(events)
