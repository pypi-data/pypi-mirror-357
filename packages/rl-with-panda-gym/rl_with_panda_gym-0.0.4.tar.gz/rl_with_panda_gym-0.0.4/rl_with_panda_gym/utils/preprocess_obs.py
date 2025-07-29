import numpy as np
import tensorflow as tf

def preprocess_obs(obs):
    """Preprocessa le osservazioni come nell'ambiente di training
    
    """
    ag = obs["achieved_goal"]     # 3 dimensioni
    tg = obs["desired_goal"]      # 3 dimensioni
    ob = obs["observation"][:6]   # primi 6 elementi (posizione + velocità del gripper)
    
    return np.concatenate([ag, tg, ob])
