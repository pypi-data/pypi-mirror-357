import tensorflow as tf
import tensorflow_probability as tfp
from collections import deque
import panda_gym
import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd


from rl_with_panda_gym.utils.compute_moving_average import compute_moving_average


class Policy(tf.keras.Model):
    """

     Policy network dell'agente, Predice la probabilità di ogni azione discreta in PandaGym.


    Esempio:
        1. Gli passiamo un osservazione,
        2. ottenere le probabilità di ogni azione discreta,

    Attributes:
        action_dim (int): Dimensione dello spazio delle azioni, di default 3 per PandaGym

    """

    def __init__(self, num_action, action_dim=3, discrete=False):
        super().__init__()
        self.discrete = discrete
        self.dense1 = tf.keras.layers.Dense(128, activation="relu")
        self.dense2 = tf.keras.layers.Dense(64, activation="relu")
        self.dense3 = tf.keras.layers.Dense(32, activation="relu")
        if discrete:
            self.dense4 = tf.keras.layers.Dense(num_action, activation="softmax")
        else:
            self.mu = tf.keras.layers.Dense(action_dim, activation="tanh")
            self.var = tf.keras.layers.Dense(
                action_dim, activation=lambda x: tf.nn.softplus(x)
            )

    def call(self, inputs):
        """
        Esegue il forward pass della rete neurale.

        Args:
            inputs (tf.Tensor): Input della rete neurale, l'osservazione dell'ambiente
        Returns:
            tf.Tensor: Output della rete neurale, le probabilità di ogni azione discreta

        """

        x = self.dense1(inputs)
        x = self.dense2(x)
        x = self.dense3(x)
        if self.discrete:
            return self.dense4(x)
        return self.mu(x)[0], self.var(x)[0]


class Reinforce:
    """
    Class per l'agente Reinforce per PandaGym

    Attributes:
        env (gym.Env): Ambiente PandaGym
        gamma (float): Fattore di sconto per i ritorni, di default 0.99
        learning_rate (float): Tasso di apprendimento per l'ottimizzatore, di default 0.001
        num_episodes (int): Numero di episodi da eseguire, di default 10000
        print_every (int): Frequenza con cui stampare i risultati, di default 100
        division (int): Numero di divisioni dello spazio delle azioni, di default 4

    """

    def __init__(
        self,
        env,
        result_path="./",
        model_path="./",
        plot_path="./",
        gamma=0.99,
        learning_rate=0.001,
        num_episodes=10000,
        print_every=100,
        division=4,
        discrete=False,
    ):
        """
        Inizializza l'agente Reinforce per PandaGym
        """

        self.env = env
        self.gamma = gamma
        self.num_episodes = num_episodes
        self.learning_rate = learning_rate
        self.print_every = print_every

        self.discrete = discrete
        print(f"Discretizzazione dello spazio delle azioni: {self.discrete}")

        # Imposto la dimensione dello spazio delle azioni
        self.action_dim = self.env.action_space.shape[0]

        # DISCRETIZATION
        self.division = division
        self.num_action = self.division**self.action_dim
        # Divido lo spazio delle azioni in division parti
        self.action_bins = np.linspace(
            self.env.action_space.low[0], self.env.action_space.high[0], self.division
        )
        # Ora bisogna salvarsi tutte le combinazioni possibili di azioni
        self.all_action_combination = np.array(
            np.meshgrid(self.action_bins, self.action_bins, self.action_bins)
        ).T.reshape(-1, 3)
        # CREO LA POLICY
        if self.discrete:
            self.policy = Policy(
                num_action=self.num_action, action_dim=self.action_dim, discrete=True
            )
        else:
            self.policy = Policy(
                num_action=None, action_dim=self.action_dim, discrete=False
            )
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate)

        self.success_track = []
        self.reward_track = []
        
        #PERCORSI PER I RISULTATI
        self.result_path = result_path
        self.model_path = model_path
        self.plot_path = plot_path

    def generate_episode(self, policy):
        """
        Genera un episodio eseguendo la policy nell'ambiente

        Args:
            policy (ContinousPolicy): Policy da eseguire nell'ambiente
        Returns:
            states (list): Lista degli stati osservati durante l'episodio
            actions (list): Lista delle azioni eseguite durante l'episodio
            rewards (list): Lista dei reward ottenuti durante l'episodio

        """

        obs, _ = self.env.reset()
        obs = self.preprocess_obs(obs)
        done = False
        states, action_indices, actions, rewards = [], [], [], []

        while not done:

            states.append(obs)
            action, action_idx = self.sample_action(policy, obs)

            obs, reward, terminated, truncated, info = self.env.step(action)
            obs = self.preprocess_obs(obs)
            done = terminated or truncated

            action_indices.append(action_idx)
            actions.append(action)
            rewards.append(reward)

        self.success_track.append(info["is_success"])

        if self.discrete:
            return states, action_indices, rewards
        return states, actions, rewards

    def sample_action(self, policy, obs):
        """
        Campiona un'azione dalla policy data l'osservazione

        dopo aver predetto la probabilità di ogni azione discreta creiamo una distribuzione categorica e campioniamo un'azione
        per poi ritornare l'azione e il suo indice
        Args:
            policy (ContinuousPolicy): Policy da cui campionare l'azione
            obs (tf.Tensor): Osservazione dell'ambiente
        Returns:
            action (np.ndarray): Azione campionata dalla policy
            action_idx (int): Indice dell'azione campionata ( indice della combinazione di azioni discrete )


        """
        if self.discrete:
            x = policy(obs)

            dist = tfp.distributions.Categorical(probs=x)
            action_idx = dist.sample()[0]
            if not 0 <= action_idx < self.num_action:
                print(f"Action index {action_idx} stranamente fuori range!")
            return self.all_action_combination[action_idx], action_idx
        else:
            mu, var = policy(obs)
            dist = tfp.distributions.Normal(mu, var)
            action = dist.sample()
            action = tf.clip_by_value(
                action, self.env.action_space.low, self.env.action_space.high
            )
            return action.numpy(), None

    def preprocess_obs(self, obs):
        """
           Concatena "achieved_goal", "desired_goal" e "observation" dell'osservazione in un unico array.

        Args:
            observation (Dict): Osservazione dell'ambiente PandaGym contenente "achieved_goal", "desired_goal" e "observation".
        Returns:
            np.ndarray: un numpy array concatenato contenente achieved_goal, desired_goal e observation.

        """

        ag = obs["achieved_goal"]
        tg = obs["desired_goal"]
        ob = obs["observation"]
        return np.concatenate([ag, tg, ob])[np.newaxis, :]

    @tf.function
    def train_plicy(self, states, returns, action_indices=None, actions=None):
        if self.discrete:

            with tf.GradientTape() as tape:
                policy_loss = 0

                # Calcolo la log_probabilità delle azioni e la loss della policy
                for state, action_idx, G in zip(states, action_indices, returns):

                    # predico nuovamente la media e sigma
                    x = self.policy(state)

                    # creo la distribuzione normale
                    dist = tfp.distributions.Categorical(probs=x)

                    # ESATTAMENTE LA RIGA 7 PSEUDOCODICE
                    # calcolo la log_probabilità dell'azione nella distribuzione
                    action_idx = tf.convert_to_tensor([action_idx], dtype=tf.float32)
                    log_prob = tf.reduce_sum(
                        dist.log_prob(action_idx)
                    )  # sommo le log_probabilità per ogni dimensione dell'azione per avere un singolo valore
                    policy_loss += -log_prob * G

                    if tf.math.is_nan(policy_loss):
                        print("NaN detected in policy_loss!")
                        break

                policy_loss /= len(states)

            # LINEA 8 PSEUDOCODICE
            gradients = tape.gradient(policy_loss, self.policy.trainable_variables)

            self.optimizer.apply_gradients(
                zip(gradients, self.policy.trainable_variables)
            )

        else:
            with tf.GradientTape() as tape:
                policy_loss = 0

                # Calcolo la log_probabilità delle azioni e la loss della policy
                for state, action, G in zip(states, actions, returns):

                    # predico nuovamente la media e var
                    mu, var = self.policy(state)

                    # creo la distribuzione normale
                    dist = tfp.distributions.Normal(mu, var)

                    # ESATTAMENTE LA RIGA 7 PSEUDOCODICE
                    # calcolo la log_probabilità dell'azione nella distribuzione
                    action = tf.convert_to_tensor(action, dtype=tf.float32)
                    log_prob = tf.reduce_sum(
                        dist.log_prob(action)
                    )  # sommo le log_probabilità per ogni dimensione dell'azione per avere un singolo valore
                    policy_loss += -log_prob * G

                    if tf.math.is_nan(policy_loss):
                        print("NaN detected in policy_loss!")
                        break

                policy_loss /= len(states)
            gradients = tape.gradient(policy_loss, self.policy.trainable_variables)

            self.optimizer.apply_gradients(
                zip(gradients, self.policy.trainable_variables)
            )

    def train(self):
        """
        Addestramento dell'agente Reinforce per num_episodes episodi
        Durante l'addestramento:
            1. Per ogni episodio
            2. Genera un episodio seguendo la policy attuale
            3. Calcola i ritorni (rewards scontati) per ogni step dell'episodio generato
            4. Calcola la loss della policy basata sui ritorni
            5. Ottimizza la policy usando l'ottimizzatore Adam
        Args:
            None
        Returns:
            None


        """

        # LINEA 3 PSEUDOCODICE
        for i in range(self.num_episodes):

            # LINEA 4 PSEUDOCODICE, genera un episodio
            if self.discrete:
                states, action_indices, rewards = self.generate_episode(self.policy)
            else:
                states, actions, rewards = self.generate_episode(self.policy)

            self.reward_track.append(sum(rewards))

            returns = []

            # LINEA 6 PSEUDOCODICE, calcola i ritorni
            for t in range(len(rewards)):
                G = 0
                for k, r in enumerate(rewards[t:]):
                    G += r * (self.gamma**k)
                returns.append(G)

            # LINEE 7-8 PSEUDOCODICE, calcola la loss e ottimizza la policy
            # Calcola la loss della policy

            if self.discrete:
                self.train_plicy(states, returns, action_indices=action_indices)
            else:
                self.train_plicy(states, returns, actions=actions)

            if i % self.print_every == 0 and i > 0:
                avg_score = (
                    np.mean(self.reward_track[-self.print_every :])
                    if len(self.reward_track) >= self.print_every
                    else np.mean(self.reward_track)
                )
                recent_success_rate = (
                    np.mean(self.success_track[-self.print_every :])
                    if len(self.success_track) >= self.print_every
                    else np.mean(self.success_track)
                )
                print(
                    f"Episode {i}/{self.num_episodes}\tAverage Score: {avg_score:.2f}\tSuccess Rate: {recent_success_rate*100:.1f}%"
                )

                # SALVO PESI
                self.policy.save_weights(
                    "reinforce_panda_gym_discrete_policy_weights.weights.h5"
                )
                

    def save_metrics(self):
        results_df = pd.DataFrame(
            {
                "episode": range(1, len(agent.reward_track) + 1),
                "reward": agent.reward_track,
                "success_rate": agent.success_track,
            }
        )

        # Salva in CSV
        results_df.to_csv(
            self.result_path + ".csv", index=False
        )
                
    def save_model(self):
        """
        Salva il modello della policy in un file HDF5.

        Args:
            path (str): Percorso del file in cui salvare il modello.

        Returns:
            None
        """
        self.policy.save_weights(self.model_path + ".weights.keras")

    def plot_results(self):
        """
        Crea un grafico dei reward e success rate durante l'addestramento.

        1. Calcola la media mobile dei reward e success rate.
        2. Crea un grafico con 2 subplot:
            - Moving average dei reward.
            - Success rate (media mobile).
        3. Salva il grafico in una cartella "plots"

        Args:
            None

        Returns:
            None

        """

        fig, ax = plt.subplots(1, 2, figsize=(15, 5))

        # Moving average dei reward
        sma_reward = compute_moving_average(
            self.reward_track, window_size=min(50, len(self.reward_track) // 2)
        )

        ax[0].set_title("Reward Progress")
        ax[0].set_xlabel("Episode")
        ax[0].set_ylabel("Reward")
        ax[0].plot(self.reward_track, alpha=0.3, label="Raw Reward")
        ax[0].plot(sma_reward, label="Moving Average", linewidth=2)
        ax[0].legend()
        ax[0].grid(True, alpha=0.3)

        # Success rate
        sma_success_rate = compute_moving_average(
            self.success_track, window_size=min(50, len(self.success_track) // 2)
        )

        ax[1].set_title("Success Rate Progress")
        ax[1].set_xlabel("Episode")
        ax[1].set_ylabel("Success Rate")
        ax[1].plot(self.success_track, alpha=0.3, label="Raw Success Rate")
        ax[1].plot(sma_success_rate, label="Moving Average", linewidth=2)
        ax[1].set_ylim(0, 1.1)
        ax[1].legend()
        ax[1].grid(True, alpha=0.3)

        plt.tight_layout()
        os.makedirs("plots", exist_ok=True)
        fig.savefig(
            self.plot_path + ".png",
            dpi=150,
            bbox_inches="tight",
        )
        plt.close(fig)


if __name__ == "__main__":

    env = gym.make("PandaReach-v3", reward_type="dense")

    agent = Reinforce(
        env, num_episodes=65000, print_every=500, learning_rate=0.0005
    )

    obs, _ = env.reset()
    obs = agent.preprocess_obs(obs)

    print(agent.sample_action(agent.policy, obs))

    agent.train()

    agent.policy.save_weights("reinforce_panda_gym_discrete_policy_weights.weights.h5")
    agent.policy.save("reinforce_panda_gym_discrete_policy.h5")

    # Crea la directory per i risultati se non esiste
    os.makedirs("results", exist_ok=True)

    # Salva i reward in un file CSV

    # Crea un DataFrame con episode, reward e success rate
    results_df = pd.DataFrame(
        {
            "episode": range(1, len(agent.reward_track) + 1),
            "reward": agent.reward_track,
            "success_rate": agent.success_track,
        }
    )

    # Salva in CSV
    results_df.to_csv("./results/reinforce_training_discrete_results.csv", index=False)
