import time
import threading
import io
import cv2 as cv
from enum import Enum

from PIL import Image
import numpy as np

CV_PIPELINE = {"states": {
    "is_dead": None,
    "game_over": None,
    "game": None,
},
    "masks": {
}}

# This parameters dictates how long in seconds the event is_dead should be active for before deeming the player dead
IS_DEAD_N_SECONDS = 1.

# This parameters dictates how long in seconds the event game_over should be active for before deeming the player game over
IS_GAME_OVER_N_SECONDS = 1.


class Event(str, Enum):
    PLAYER_DIED = 'player_died'
    GAME_ENDED = 'game_ended'
    PLAYER_WON = 'player_won'
    GAME_STARTED = 'game_started'


class EventPublisher:
    """ This object takes a screenshot from the game at a specified interval (default 0.1s), and then it runs a Computer Vision pipeline generating boolean values about the state of the game.
        The aim of the class is to smoothen out the measured values from the pipeline and to generate events based on changes of the underlying bonk.io game."""

    def __init__(self, browser, collect_every=0.1, n_frames=5):
        self.browser = browser
        self.collect_every = collect_every
        self.n_frames = n_frames

        self.previous_frames = []
        self.collection_lock = threading.Lock()

        self.stop = False

        self.previous_events = []

        self.previous_cv_ = {}
        for event_name in CV_PIPELINE['states'].keys():
            self.previous_events[event_name] = []

        self.previous_masks = {}
        for mask_name in CV_PIPELINE['masks'].keys():
            self.previous_masks[mask_name] = []

    def run_thread(self):
        """ Method to be run as a tread continuously, at more or less fixed time intervals it collects the screenshot, runs the CV pipeline and it updates the internal list of events to report. """
        last_collected = -1e10

        while not self.stop:
            if time.time() - last_collected > self.collect_every:
                self._collect()
                last_collected = time.time()

                self._run_cv_pipeline()

                self._update_internal_event_list()

    def get_events(self):
        """ Main method to access the events produce by this collector"""

    def _collect(self):
        try:
            element = self.browser.find_element_by_id('gamerenderer')
        except Exception as e:
            print(f"WARNING: error when finding the game rendered element:", str(e))

        buff = io.BytesIO(element.screenshot_as_png)
        arr = np.array(Image.open(buff))
        with self.collection_lock:
            self.previous_frames.append((time.time(), arr))

    def _run_cv_pipeline(self):
        last_frame = self.previous_frames[-1]

        for event_name, event_fn in CV_PIPELINE['events'].items():
            event_flag = event_fn(last_frame)
            self.previous_events[event_name].append((time.time(), event_flag))

        for mask_name, mask_fn in CV_PIPELINE['masks'].items():
            mask = mask_fn(last_frame)
            self.previous_masks[mask].append(mask)

    def get_last_n_frames(self):
        """ Returns the last n frames (self.n_frames) collected and the last n masks generated for each mask function in CV_PIPELINE on the past frames """
        frames = None
        mask_frames = None
        with self.collection_lock:
            frames = self.previous_frames[-self.n_frames:]
            mask_frames = {mask_name: vals[-self.n_frames:] for mask_name, vals in self.previous_masks}

            self.previous_frames = [*frames]
            for mask_name in self.previous_masks.keys():
                self.previous_masks[mask_name] = self.previous_masks[mask_name][-self.n_frames:]

        return frames, mask_frames

    def _update_internal_event_list(self):

        events = []

        # Check if died (died if we have been getting "is_dead" for at least IS_DEAD_N_SECONDS second)
        counter = 1
        is_dead = False

        # Loop through the last measured events from the pipeline going back in time
        for i in range(len(self.previous_events['is_dead'])):
            t, was_dead = self.previous_events['is_dead'][-i-1]

            # If it was not dead, then break
            if not was_dead:
                break
            else:
                # If this has been dead for more than IS_DEAD_N_SECONDS, then add a dead event, game over is True then
                if time.time() - t > IS_DEAD_N_SECONDS:
                    is_dead = True
                    events.extend([Event.IS_DEAD, Event.GAME_OVER])
                    break

        # If it is not already game over because of death, check what the pipeline measurements said
        if not game_over:

            i = 0
            # Loop through the last measured events from the pipeline going back in time
            for i in range(len(self.previous_events['game_over'])):
                t, game_ended = self.previous_events['game_over'][-i-1]

                # If it was not game over, then break
                if not game_ended:
                    break
                else:
                    # If the game has been over continuosly for IS_GAME_OVER_N_SECONDS, then add a game over event
                    if time.time() - t > IS_GAME_OVER_N_SECONDS:
                        game_over = True
                        events.append([Event.GAME_OVER])

            # Already the first event back in time is non game_over, maybe it just flipped to a new game

        return events
