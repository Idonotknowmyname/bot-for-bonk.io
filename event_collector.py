import time
import threading
import io
import cv2 as cv

from PIL import Image
import numpy as np

CV_PIPELINE = {"events": {
    "is_dead": None,
    "game_over": None,
    "start_game": None,
},
    "masks": {
}}


class EventCollector:
    def __init__(self, browser, collect_every=0.1, n_frames=5):
        self.browser = browser
        self.collect_every = collect_every
        self.n_frames = n_frames

        self.previous_frames = []
        self.collection_lock = threading.Lock()

        self.stop = False

        self.previous_events = {}
        for event_name in CV_PIPELINE['events'].keys():
            self.previous_events[event_name] = []

        self.previous_masks = {}
        for mask_name in CV_PIPELINE['masks'].keys():
            self.previous_masks[mask_name] = []

    def run(self):
        last_collected = -1e10

        while not self.stop:
            if time.time() - last_collected > self.collect_every:
                self.collect()
                last_collected = time.time()

                self.run_cv_pipeline()

                self.update_internal_state()

    def collect(self):
        try:
            element = self.browser.find_element_by_id('gamerenderer')
        except Exception as e:
            print(f"WARNING: error when finding the game rendered element")

        buff = io.BytesIO(element.screenshot_as_png)
        arr = np.array(Image.open(buff))
        with self.collection_lock:
            self.previous_frames.append((time.time(), arr))

    def run_cv_pipeline(self):
        last_frame = self.previous_frames[-1]

        for event_name, event_fn in CV_PIPELINE['events'].items():
            event_flag = event_fn(last_frame)
            self.previous_events[event_name].append(event_flag)

        for mask_name, mask_fn in CV_PIPELINE['masks'].items():
            mask = mask_fn(last_frame)
            self.previous_masks[mask].append(mask)

    def get_last_n_frames(self):
        frames = None
        mask_frames = None
        with self.collection_lock:
            frames = self.previous_frames[-self.n_frames:]
            mask_frames = {mask_name: vals[-self.n_frames:] for mask_name}

            self.previous_frames = [*frames]

        return frames, mask_frames
