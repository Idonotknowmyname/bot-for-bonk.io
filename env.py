import gym
from game_engine import GameEngine


class BonkIoGame(gym.Environment):
    def __init__(self):
        self._engine = None

    def reset(self):
        if self._engine is None:
            self._engine = GameEngine()

        obs, info = self._engine.get_obs()
