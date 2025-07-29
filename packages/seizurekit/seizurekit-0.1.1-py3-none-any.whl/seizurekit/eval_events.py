import numpy as np
from .eval_utils import (seprate_synchronize_events,
                                apply_temporal_smoothing_preds,
                                hysteresis_thresholding,)

def compute_event_level_metrics(
    gt_events,
    pred_events,
    window_sec=10,
    onset_tolerance_sec=30
):
    """
    Event-level TP/FN/FP with ±tolerance, plus FA/h over non-seizure time.
    """
    tol_w = onset_tolerance_sec // window_sec
    
    TP = FN = FP = 0
    latencies = []
    
    # Flatten GT to measure total non-seizure time
    gt_flat = np.hstack(gt_events)
    non_seizure_windows = np.sum(gt_flat == 0)
    non_seizure_hours = non_seizure_windows * window_sec / 3600.0
    
    num_events = len(gt_events)
    detected = 0
    
    for gt, pred in zip(gt_events, pred_events):
        gt = np.asarray(gt)
        pred = np.asarray(pred)
        
        # Find seizure onset index
        seiz_idx = np.flatnonzero(gt == 1)
        if seiz_idx.size == 0:
            # No seizure label in this segment
            continue
        onset = seiz_idx[0]
        start = max(0, onset - tol_w)
        end   = onset + tol_w
        
        # TP vs FN
        if np.any(pred[start:end+1] == 1):
            TP += 1
            detected += 1
            # First detection for latency
            first = np.flatnonzero(pred[start:end+1] == 1)[0] + start
            latencies.append((first - onset) * window_sec)
        else:
            FN += 1
        
        # FP: any pred==1 where gt==0
        false_positions = np.flatnonzero((gt == 0) & (pred == 1))
        if false_positions.size > 0:
            FP += 1
    
    FN = num_events - TP  # ensure consistency
    event_sensitivity = TP / num_events if num_events else np.nan
    avg_latency = np.mean(latencies) if latencies else None
    
    FA_per_nonseizure_hour = FP / non_seizure_hours if non_seizure_hours else np.nan
    
    """
    Compute duration-based seizure coverage.
    """
    gt_flat = np.hstack(gt_events)
    pred_flat = np.hstack(pred_events)
    total_seizure_time = np.sum(gt_flat == 1) * window_sec
    missed_time = np.sum((gt_flat == 1) & (pred_flat == 0)) * window_sec
    coverage = ((total_seizure_time - missed_time) / total_seizure_time
                if total_seizure_time > 0 else np.nan)
    # This is the total predicted seizure duration
    predicted_seizure_burden = np.sum(pred_flat == 1) * window_sec
    total_time = len(pred_flat) * window_sec
    burden_sec_per_hour = (predicted_seizure_burden / total_time) * 3600 if total_time > 0 else np.nan
    burden_min_per_hour = burden_sec_per_hour / 60 if total_time > 0 else np.nan
    burden_percent  = (predicted_seizure_burden / total_time) if total_time > 0 else np.nan
    return {
        'num_events': num_events,
        'TP_events': TP,
        'FN_events': FN,
        'FP_events': FP,
        'event_sensitivity': event_sensitivity,
        'latencies_sec': latencies,
        'avg_latency_sec': avg_latency,
        'FA_per_nonseizure_hour': FA_per_nonseizure_hour,
        'total_seizure_time_sec': total_seizure_time,
        'missed_seizure_time_sec': missed_time,
        'coverage': coverage,
        'burden': burden_percent,
        'burden_sec_per_hour': burden_sec_per_hour,
        'burden_min_per_hour': burden_min_per_hour,
    }


def calculate_event_level_metrics(
    all_probs,
    all_targets,
    eval_config,
    smoothing_window=5,
    hysteresis_high=0.5,
    hysteresis_low=0.5
):
    """
    Computes and prints event-level detection metrics for each modality.

    This function processes model probabilities to generate binary predictions,
    identifies discrete events, and then calculates metrics such as event recall,
    precision, F1-score, and onset/offset errors.

    Args:
        all_probs (dict): Dictionary of model probabilities, keyed by modality name.
        all_targets (np.ndarray): Ground truth labels.
        eval_config (dict): Configuration dictionary containing parameters like
                            'window_duration' and 'detection_tolerance'.
        smoothing_window (int): The size of the window for temporal smoothing on predictions.
        hysteresis_high (float): The high threshold for hysteresis thresholding.
        hysteresis_low (float): The low threshold for hysteresis thresholding.
    
    Returns:
        dict: A dictionary containing the detailed event-level metrics for each modality.
    """
    
    modalities = list(all_probs.keys())
    all_event_metrics = {}

    # Extract parameters from eval_config, with defaults
    window_sec = int(eval_config.get('window_duration', 10))
    onset_tolerance_sec = int(eval_config.get('detection_tolerance', 30))

    for modality in modalities:
        # 1. Get predictions from probabilities
        probs = all_probs[modality]
        preds = hysteresis_thresholding(probs, hysteresis_high, hysteresis_low, only_pos_probs=True)
        preds_smooth = apply_temporal_smoothing_preds(preds, smoothing_window)

        # 2. Separate into distinct events
        events = seprate_synchronize_events(all_targets, preds_smooth)

        # 3. Convert to list-of-lists format for metric calculation
        gt_event_list = [event['ground_truth'].tolist() for event in events]
        pred_event_list = [event['model_output'].tolist() for event in events]
        
        # 4. Compute metrics
        event_metrics = compute_event_level_metrics(
            gt_event_list,
            pred_event_list,
            window_sec=window_sec,
            onset_tolerance_sec=onset_tolerance_sec
        )
        all_event_metrics[modality] = event_metrics

    # 5. Print results in a nicely formatted table
    line_width = 120
    print("=" * line_width)
    print("Event-Level Detection Metrics:")
    print("-" * line_width)
    header = (
        f"{'Modality':<20} | "
        f"{'#Events':<8} | "
        f"{'TP':<5} | "
        f"{'FN':<5} | "
        f"{'FP':<5} | "
        f"{'Sens':<6} | "
        f"{'Lat (s)':<8} | "
        f"{'FA/h':<6} | "
        f"{'Cov.':<6} | "
        f"{'Burden (min/h)':<15}"
    )
    print(header)
    print("-" * line_width)

    for modality, metrics in all_event_metrics.items():
        print(
            f"{modality:<20} | "
            f"{metrics['num_events']:<8} | "
            f"{metrics['TP_events']:<5} | "
            f"{metrics['FN_events']:<5} | "
            f"{metrics['FP_events']:<5} | "
            f"{metrics['event_sensitivity']:<6.4f} | "
            f"{metrics['avg_latency_sec']:<8.4f} | "
            f"{metrics['FA_per_nonseizure_hour']:<6.4f} | "
            f"{metrics['coverage']:<6.4f} | "
            f"{metrics['burden_min_per_hour']:<15.4f}"
        )

    print("=" * line_width)
    print("Coverage(Cov.): Fraction of true seizure time detected by AI.")
    print("Burden: Time AI believes seizure is occurring, scaled to minutes/hour.")
    print("=" * line_width)

    return all_event_metrics

