#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 22:26:40 2019

@author: fake_batman_
"""

import gym
import numpy as np
import os
import random
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from collections import deque

class Agent():
    def __init__(self, state_size, action_size):
        self.weight_backup = "cartpole_weight.h5"
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen = 2000) #double ended queue of 2000 length
        self.learning_rate = 0.001 # learning rate (alpha)
        self.gamma = 0.95 # future discount reward. 
        self.exploration_rate = 1.0 # high exploration rate at the start
        self.exploration_min = 0.01 # low exploration rate at the end ie high expoitation rate
        self.exploration_decay = 0.995 
        self.brain = self._build_model() # neural network
    
    # returns the neural network model and functions like .save(), .predict() are preformed
    def _build_model(self):
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
    
        if os.path.isfile(self.weight_backup):
            model.load_weights(self.weight_backup)
            self.exploration_rate = self.exploration_min
        return model
            
    def save_model(self):
        self.brain.save(self.weight_backup)
        
    def act(self, state):
        if np.random.rand() <= self.exploration_rate:
            return random.randrange(self.action_size) # choose random action
        act_values = self.brain.predict(state)
        return np.argmax(act_values[0]) # max of all the values predicted by the NN
    
    # remember() function will simply store states, actions 
    # and resulting rewards into the memory
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        
    # train our neural network on past experiences; but batch wise
    def replay(self, sample_batch_size):
        if len(self.memory) < sample_batch_size:
            return
        sample_batch = random.sample(self.memory, sample_batch_size)
        for state, action, reward, next_state, done in sample_batch:
            target = reward
            if not done:
                target = reward + self.gamma*np.amax(self.brain.predict(next_state)[0])
            target_f = self.brain.predict(state)
            # updating the target
            target_f[0][action] = target
            # .fit(), takes care of minimizing the loss ie subtracts the loss, squares it 
            self.brain.fit(state, target_f, epochs=1,verbose=0)
        if self.exploration_rate > self.exploration_min:
            self.exploration_rate *= self.exploration_decay
            
class CartPole:
    def __init__(self):
        self.sample_batch_size = 32
        self.episodes = 10000
        self.env = gym.make('CartPole-v1')
        self.state_size = self.env.observation_space.shape[0]
        self.action_size = self.env.action_space.n
        self.agent = Agent(self.state_size, self.action_size)
        
    def run(self):
        try:
            for index_episode in range(self.episodes):
                state = self.env.reset()
                state = np.reshape(state, [1, self.state_size])
                done = False
                index = 0
                
                while not done:
                    # Uncomment the below line to visualize the training
                    self.env.render()
                    action = self.agent.act(state)
                    next_state, reward, done, _ = self.env.step(action)
                    next_state = np.reshape(next_state, [1, self.state_size])
                    self.agent.remember(state, action, reward, next_state, done)
                    state = next_state
                    index += 1
                print("Episode: {}\tScore: {}".format(index_episode, index+1))
                self.agent.replay(self.sample_batch_size)
        finally:
            self.agent.save_model()
            
if __name__ == "__main__":
    cartpole = CartPole()
    cartpole.run()
                    