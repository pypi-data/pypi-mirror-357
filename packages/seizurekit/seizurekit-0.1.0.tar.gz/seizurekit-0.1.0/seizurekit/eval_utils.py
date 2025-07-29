import numpy as np
from scipy.stats import mode



def apply_temporal_smoothing_probs(probabilities, smoothing_window=3):
    """Apply temporal smoothing to 1D probability array"""
    if len(probabilities) < smoothing_window or smoothing_window < 1:
        return probabilities
    
    # Use valid mode to avoid edge effects
    smoothed = np.convolve(probabilities, 
                            np.ones(smoothing_window) / smoothing_window, 
                            mode='same')
    return smoothed

def apply_temporal_smoothing_preds(preds, window_size=3):
    """
    Applies temporal smoothing to the predictions using a moving mode filter.
    
    Args:
        preds (np.ndarray): Predictions of shape (N,).
        window_size (int): Size of the smoothing window.
        
    Returns:
        np.ndarray: Smoothed predictions.
    """
    if window_size < 1:
        return preds

    smoothed_preds = np.copy(preds)
    half_window = window_size // 2

    for i in range(len(preds)):
        start = max(0, i - half_window)
        end = min(len(preds), i + half_window + 1)
        smoothed_preds[i] = mode(preds[start:end], keepdims=False).mode

    return smoothed_preds

def hysteresis_thresholding(probs, high_thresh=0.7, low_thresh=0.3,
                            initial_state=0, only_pos_probs=False):
    
    """
    Apply hysteresis thresholding to a sequence of binary classification probabilities.
    If high_thresh == low_thresh, performs simple thresholding.
    Args:
        probs (np.ndarray): Array of shape (T, 2), where each row is [p_neg, p_pos] from softmax,
                            or shape (T,) if only positive probabilities are provided.
        high_thresh (float): Threshold to switch from negative to positive.
        low_thresh (float): Threshold to switch from positive to negative.
        initial_state (int): Starting state (0=negative, 1=positive).
        only_pos_probs (bool): If True, `probs` is expected to be a 1D array of positive class probabilities.

    Returns:
        np.ndarray: Array of shape (T,), with values 0 or 1 representing the predicted class at each time step.
    """
    # probs = np.asarray(probs)  # Ensure input is a NumPy array

    if only_pos_probs:
        if probs.ndim != 1:
            raise ValueError("Expected 1D array for positive probabilities when only_pos_probs=True.")
        pos_probs = probs
    else:
        if probs.ndim != 2 or probs.shape[1] != 2:
            raise ValueError("Expected 2D array of shape (T, 2) when only_pos_probs=False.")
        pos_probs = probs[:, 1]
        
    n = len(pos_probs)

    if high_thresh == low_thresh:
        return (pos_probs >= high_thresh).astype(int)
    # Initialize predictions array
    preds = np.zeros(n, dtype=int)
    current_state = initial_state

    for i, p in enumerate(pos_probs):
        if current_state == 0:
            # Only switch to positive if we exceed the high threshold
            if p >= high_thresh:
                current_state = 1
        else:
            # Only switch to negative if we fall below the low threshold
            if p < low_thresh:
                current_state = 0
        preds[i] = current_state

    return preds

    
def seprate_synchronize_events(gt, pred):
    """
    Extracts non-seizure → seizure events from ground truth (x) and aligns them with model outputs (y).
    
    Args:
        gt (list or np.ndarray): Ground truth labels (0 = non-seizure, 1 = seizure).
        pred (list or np.ndarray): Model outputs (same length as x).

    Returns:
        List of dicts, each containing:
            - 'start': start index of the event
            - 'end': end index of the event
            - 'ground_truth': list of ground truth labels for the event
            - 'model_output': list of model outputs for the event
    """

    x = np.array(gt)
    y = np.array(pred)

    events = []
    i = 0
    n = len(x)

    while i < n:
        # Find start of a non-seizure segment
        if x[i] == 0:
            start = i
            while i < n and x[i] == 0:
                i += 1
            # Now i is at the start of a seizure segment (1s)
            if i < n and x[i] == 1:
                while i < n and x[i] == 1:
                    i += 1
                end = i  # i now points to the end of seizure segment
                event = {
                    'start': start,
                    'end': end,
                    'ground_truth': x[start:end],#.tolist(),
                    'model_output': y[start:end]#.tolist()
                }
                events.append(event)
        else:
            i += 1  # Skip any 1s not preceded by a 0

    return events

def split_by_patient_id(patient_ids, pred_array):
    """
    Splits the predictions into a list of tuples (patient_id, array) for each unique patient_id.
    
    Args:
        patient_ids (np.ndarray): Array of patient IDs.
        pred_array (np.ndarray): Array of predictions corresponding to patient IDs.
        
    Returns:
        List of tuples (patient_id, array).
    """
    # check if patient_ids is a numpy array else convert it
    if not isinstance(patient_ids, np.ndarray):
        patient_ids = np.array(patient_ids)
    seen = set()
    unique_ids = []
    for pid in patient_ids:
        if pid not in seen:
            unique_ids.append(pid)
            seen.add(pid)

    # Build two lists of (patient_id, array) tuples
    patient_pred_events = [
        (pid, pred_array[patient_ids == pid])
        for pid in unique_ids
    ]
    
    return patient_pred_events

#%%
