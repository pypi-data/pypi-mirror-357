import numpy as np
import matplotlib.pyplot as plt
from seizurekit.eval_utils import hysteresis_thresholding

def create_toy_data():
    """Generates synthetic ground truth and model probability data."""
    # Time steps
    t = np.linspace(0, 100, 500)
    
    # Ground truth: a seizure event between t=40 and t=60
    y_true = np.zeros_like(t)
    y_true[(t > 40) & (t < 60)] = 1
    
    # Model probabilities: noisy sine wave shifted to simulate a detection
    noise = np.random.normal(0, 0.1, t.shape)
    y_prob = 0.5 * (1 + np.sin((t - 45) / 5)) + noise
    y_prob = np.clip(y_prob, 0, 1) # Ensure probs are in [0, 1]
    
    return t, y_true, y_prob

def plot_seizure_data(t, y_true, y_prob, y_pred):
    """
    A placeholder function to visualize seizure detection results.
    """
    plt.figure(figsize=(12, 6))
    
    plt.plot(t, y_prob, label='Model Probability', color='blue', alpha=0.7)
    plt.plot(t, y_true, label='Ground Truth', color='black', linestyle='--', lw=2)
    plt.plot(t, y_pred, label='Hysteresis Prediction', color='red', linestyle='-.', lw=2)
    
    plt.title('Toy Seizure Detection Example')
    plt.xlabel('Time Steps')
    plt.ylabel('Label / Probability')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.ylim(-0.1, 1.1)
    plt.show()

if __name__ == '__main__':
    # Generate data
    time_steps, ground_truth, model_probs = create_toy_data()
    
    # Get predictions using a utility from your toolkit
    predictions = hysteresis_thresholding(model_probs, high_thresh=0.75, low_thresh=0.35, only_pos_probs=True)
    
    # Visualize the results
    plot_seizure_data(time_steps, ground_truth, model_probs, predictions)