# =============================================================================#
# Name        : run_model.py                                                   #
# Description : Running script for training a DQN agent for playing Tetris     #
# Authors     : Ronja Faltin, Johanna Granström, Emilie Ho                     #
# Date        : 21.10.2019                                                     #
# ---------------------------------------------------------------------------- #

from builtins import range
import numpy as np
from dqn_agent import DQNAgent
from tetris_game import TetrisApp
import time

# Configuration
environment = TetrisApp()
# If you want to load a saved model: give a model name. Example:
# agent = DQNAgent('model2_q_network.h5')

agent = DQNAgent('q_network.h5')
save_model_as = 'new_q_network.h5'

batch_size = 32
num_of_episodes = 3000
time_steps_per_episode = 20000  # Amount of allowed actions for each game
best_episode = [-100, 0, 0.0, 0]  # Reward, Episode, Time, Number of cleared lines


# Function to train a model and save it
def run_dqn_train():

    for e in range(0, num_of_episodes):
        # Initialize variables
        terminated = False
        episodes_reward = 0

        environment.start_game(terminated)
        state = environment.get_state()
        state = np.reshape(state, [-1, 1])

        start_timer = time.time()

        for time_step in range(time_steps_per_episode):
            # Run Action
            environment.reset_reward()
            action = agent.act(state)

            # Take action
            next_state, reward, terminated, bumpiness, total_height, total_holes = environment.play(action)
            next_state = np.reshape(next_state, [-1, 1])
            agent.store(state, action, reward, next_state, terminated, bumpiness, total_height, total_holes)
            state = next_state
            episodes_reward += reward

            if terminated:
                agent.align_target_model()
                break

            #  If we want to quit the ai
            if environment.quit():
                break

            if len(agent.experience_replay) > batch_size:
                agent.retrain(batch_size)

        end_timer = time.time()
        total_time = end_timer - start_timer

        # Get the highest reward
        if episodes_reward > best_episode[0]:
            best_episode[0] = episodes_reward
            best_episode[1] = e
            best_episode[2] = total_time
            best_episode[3] = environment.get_number_of_lines()

        print("**********************************")
        print("Episode/Game: ", e)
        print("Total time: ", total_time, "Seconds")
        print("Episodes total reward: ", episodes_reward)
        print("Total cleared lines: ", environment.get_number_of_lines())
        print("**********************************")

        # Check if we didn't quit the ai with QUIT
        if environment.quit():
            break

    print("______________________________________")
    print("The highest reward was: ", best_episode[0], "in game: ", best_episode[1])
    print("With the time: ", best_episode[2], "Seconds")
    print("Total lines cleared: ", best_episode[3])
    print("______________________________________")
    agent.q_network.summary()
    agent.save_model(save_model_as)


# Function to play the game with a loaded model
"""def run_dqn():
    # Load the model you want to play with
    # loaded_agent = load_model()"""


if __name__ == '__main__':
    run_dqn_train()
