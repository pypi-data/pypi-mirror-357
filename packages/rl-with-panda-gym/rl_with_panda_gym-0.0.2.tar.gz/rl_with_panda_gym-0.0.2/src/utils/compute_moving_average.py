import numpy as np

def compute_moving_average(data, window_size=10):
        """
        Calcola la media mobile dei reward ottenuti durante l'addestramento.
        
        Args:
            data: lista dei reward per episodio
            window_size: dimensione della finestra per il calcolo della media mobile (default: 10).
        
        Returns:
            Array con le medie mobili. Il primo valore corrisponde alla media
            dei primi window_size episodi.
            
        """
        if len(data) < window_size:
            return np.array([])
        
        weights = np.ones(window_size) / window_size
        sma = np.convolve(data, weights, mode='valid')
        return sma