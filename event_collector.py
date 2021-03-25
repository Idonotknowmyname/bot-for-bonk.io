import time
import threading
import io
import cv2 as cv
from collections import defaultdict
from enum import Enum

from PIL import Image
import numpy as np
from cv_pipeline import cvPipeline


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
    PLAYER_LOST = 'player_lost'
    GAME_STARTED = 'game_started'


CV_PIPELINE = {"states": {
    "is_dead": lambda x: False,
    # "game_over": lambda x: False,
    # "player_wins": lambda x: False,
    # "player_loses": lambda x: False,
},
    "masks": {
        "position_rect": None
}}

# This parameters dictates how long in seconds the event is_dead should be active for before deeming the player dead
IS_DEAD_N_SECONDS = 1.

# This parameters dictates how long in seconds the event game_over should be active for before deeming the player game over
IS_GAME_OVER_N_SECONDS = 1.

# This parameter represents the number across which to average the past values of a status to get the truth value and detect value switches robustly
N_SECONDS_STATUS_AVERAGE = 1.

# How long in second, after a confirmed robust (smoothed) state change, another one can occur (to avoid states switching too fast and there being bullshit events)
STATES_UPDATE_COOLDOWN = 0.3


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

        self.last_collected = None
        self.last_collected_frame = None

        self.cv_pipeline = cvPipeline()

    def run_thread(self):
        """ Method to be run as a tread continuously, at more or less fixed time intervals it collects the screenshot, runs the CV pipeline and it updates the internal list of events to report. """
        self.last_collected = -1e9

        while not self.stop:
            if time.time() - self.last_collected > self.collect_every:
                t, frame = self._collect()
                self.last_collected = time.time()
                ttt = time.time()
                states, masks = self._run_cv_pipeline(t, frame)
                # print(f'VISION: {time.time()-ttt:.5f}')
                # Update all image observations
                with self.frames_lock:
                    self.previous_frames.append(frame)
                    for key in masks.keys():
                        self.previous_masks[key].append(masks[key])

                self._update_internal_event_list(states)

    def _collect(self):
        try:
            element = self.browser.find_element_by_id('gamerenderer')
        except Exception as e:
            print(f"WARNING: error when finding the game rendered element:", str(e))

        try:
            start_time = time.time()
            png_bytes = element.screenshot_as_png
            time_captured = time.time()
            # print(f"Screenshot {time.time() - start_time:.5f}",end=' | ')
            # print()
        except AttributeError as e:
            if 'NoneType' in str(e):
                print(f"WARNING: got error when trying to take screenshot: {str(e)}")
            else:
                raise e

        # start_time = time.time()
        arr = np.array(Image.open(io.BytesIO(png_bytes)))[:, :, :3]
        # print(f"Captured a numpy array of shape: {arr.shape}")
        # print(f"Loading the image in a numpy array took {time.time() - start_time:.3f}s")

        return time_captured, arr

    def _run_cv_pipeline(self, t, last_frame):

        pipeline_result = self.cv_pipeline.run(last_frame)

        # is_dead = pipeline_result['states']['is_dead']
        # self.previous_states['is_dead'].append((t, is_dead))

        # pos_rect = pipeline_result['masks']['position_rect']
        states = {}
        for status_name, _ in CV_PIPELINE['states'].items():
            status_flag = pipeline_result['states'][status_name]
            states[status_name] = (t, status_flag)

        masks = {}
        for mask_name, _ in CV_PIPELINE['masks'].items():
            mask = pipeline_result['masks'][mask_name]
            masks[mask_name] = (t, mask)

        return states, masks

    def get_last_n_frames(self):
        """ Returns the last self.n_frames (contains the time when it was retrieved in seconds) collected and the last n masks generated for each mask function in CV_PIPELINE on the past frames """
        frames = None
        mask_frames = None

        while len(self.previous_frames) == 0 or len(self.previous_masks[list(self.previous_masks.keys())[0]]) == 0:
            print("Frames buffer still empty, waiting...")
            time.sleep(0.1)

        with self.frames_lock:
            frames = self.previous_frames[-self.n_frames:]
            mask_frames = {mask_name: vals[-self.n_frames:] for mask_name, vals in self.previous_masks.items()}

            self.previous_frames = [*frames]

            for mask_name in self.previous_masks.keys():
                self.previous_masks[mask_name] = self.previous_masks[mask_name][-self.n_frames:]

        return frames, mask_frames

    def get_accumulated_events(self):
        """ Return the accumulated events from last time this method was called"""
        events = self.accumulated_events

        self.accumulated_events = []

        return events

    def _update_internal_event_list(self, states):

        events = []
        state_switch = {}
        now = time.time()

        for status_name in states.keys():
            self.previous_states[status_name].append(states[status_name])

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
            if state_switch.get('is_dead', False):
                events.append(Event.PLAYER_DIED)

            # Check if bonk.io game ended for everyone
            if state_switch.get('game_over', False):
                events.append(Event.GAME_OVER)

            # Check if bonk.io game just started for everyone
            if not state_switch.get('game_over', True):
                events.append(Event.GAME_STARTED)

            # Check if the screen with the player winning just showed up
            if state_switch.get('player_wins', False):
                events.append(Event.PLAYER_WON)

            # Check if the screen with the opponent winning just showed up
            if state_switch.get('player_loses', False):
                events.append(Event.PLAYER_LOST)

        self.accumulated_events.extend(events)


if __name__ == "__main__":
    import browser_automation as ba
    import cv2 as cv

    browser = ba.from_main_menu_to_game(driver_type="firefox", headless=False)

    ec = EventCollector(browser, collect_every=.01, n_frames=3)

    t = threading.Thread(target=ec.run_thread)

    t.start()

    try:
        while True:
            timing = time.time()
            frames, masks = ec.get_last_n_frames()
            last_frame = frames[-1]
            pos_rect_mask = masks['position_rect'][-1][1]
            # print(frames[-1][0])

            superposed_frame = np.expand_dims(np.where(pos_rect_mask == 255, 0, 1), axis=-1) * last_frame
            # print(f"pos_rect_mask: min = {pos_rect_mask.min()}, max = {pos_rect_mask.max()}, mean = {pos_rect_mask.mean()}")

            # print(f"last_frame.shape = {last_frame.shape}")
            cv.imshow("screen", superposed_frame.astype(np.uint8))
            # cv.imwrite('./Images/screen.png',superposed_frame.astype(np.uint8))
            cv.waitKey(1)
            print(f'TOTAL TIME {time.time()-timing}, FPS: {1/(time.time()-timing)}')

    except KeyboardInterrupt:
        browser.close()
        raise e
        ec.stop = True
        try:
            t.join(timeout=3)
        except:
            raise
