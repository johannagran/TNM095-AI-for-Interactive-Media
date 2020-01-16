# TNM095-AI-for-Interactive-Media
The reinforcement learning method that have been used for this project is Deep Q Networks, where the agent is
trained by interacting with the environment. The first thing that will happen in the process of training the agent, is
that the agent will be given a state from the environment. Depending on the state, the agent chooses an action
to send back to the environment. Actions in return give rewards which can be positive, negative or zero. For this
specific project the actions are to move a brick left, right, rotate a brick or instant drop a brick. The goal is to train
the agent to maximize the total reward it collects over an episode. An episode is one game from beginning to
game over. For each episode the agent learns which actions provides positive rewards and which actions to avoid.
