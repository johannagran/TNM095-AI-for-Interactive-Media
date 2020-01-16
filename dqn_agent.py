# =============================================================================#
# Name        : dqn_agent.py                                                   #
# Description : DQN agent for playing Tetris game                              #
# Authors     : Ronja Faltin, Johanna Granström, Emilie Ho                     #
# Date        : 21.10.2019                                                     #
# ---------------------------------------------------------------------------- #

from keras.models import Sequential, load_model
from keras.layers import Dense
from collections import deque
import numpy as np
import random


class DQNAgent:

    # If no string is given then no model is loaded
    def __init__(self, string=0):

        # Initialize attributes
        self.start_size = 1000
        self.memory_size = 2000
        self.experience_replay = deque(maxlen=self.memory_size)
        self.discount = 0.95
        self.neurons = [32, 32]
        self.loss = 'mse'
        self.optimizer = 'adam'
        self.actions = [0, 1, 2, 3, 4]

        # Initialize discount exploration rate
        self.epsilon = 0.2
        self.gamma = 0.6

        # If you want to load a saved model
        if not string == 0:
            # Load the model from string
            self.q_network = load_model(string)
            print("Loaded model with name: ", string)

            # Build networks
            self.target_network = self.build_model()
            self.align_target_model()
        else:
            # Build networks
            self.q_network = self.build_model()
            self.target_network = self.build_model()
            self.align_target_model()

    def store(self, state, action, reward, next_state, terminated, bumpiness, total_height, total_holes):
        self.experience_replay.append((state, action, reward, next_state, terminated, bumpiness, total_height,
                                       total_holes))

    def build_model(self):

        model = Sequential()
        model.add(Dense(self.neurons[0], activation='relu'))
        model.add(Dense(self.neurons[0], activation='relu'))
        model.add(Dense(self.neurons[0], activation='linear'))

        model.compile(loss=self.loss, optimizer=self.optimizer)

        return model

    def align_target_model(self):
        self.target_network.set_weights(self.q_network.get_weights())

    # Exploration function
    def act(self, state):
        """Returns the best state of a given collection of states after exploring"""
        if np.random.rand() <= self.epsilon:
            return random.choice(self.actions)
        else:
            q_values = self.q_network.predict(state)
            return np.argmax(q_values[0][self.actions])

    def retrain(self, batch_size):
        """Training the agent"""
        mini_batch = random.sample(self.experience_replay, batch_size)

        for state, action, reward, next_state, terminated, bumpiness, total_height, total_holes in mini_batch:
            target = self.q_network.predict(state)

            if terminated:
                target[0][action] = reward
            else:
                t = self.target_network.predict(next_state)
                target[0][action] = reward + self.gamma * np.amax(t)

            self.q_network.fit(state, target, epochs=1, verbose=0)

    def save_model(self, name):
        # save model and architecture to single file
        self.q_network.save(name)
        print("Saved model to disk as: ", name)
