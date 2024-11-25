import numpy as np
from numpy.typing import NDArray
from sklearn.metrics import confusion_matrix, auc
from spidet.spike_detection.thresholding import ThresholdGenerator

def true_values(y: NDArray, window_size: int = 1, true_value: int = 1, false_value = 0) -> NDArray:
    indices = np.nonzero(y)
    result = np.zeros(len(y))

    side = window_size // 2

    for index in np.nditer(indices):
        result[max(0, index-side):index + side + 1] = 1

    return result

def true_positive_rate( X: NDArray, y_true: NDArray, window_size: int = 1) -> float:
    '''
    AKA recall
    TPR = True Positive / (True Positive + False Negative)
    '''
    assert len(X) == len(y_true)

    tp = np.count_nonzero(np.logical_and(X == 1, true_values(y_true, window_size) == 1))
    fn = np.count_nonzero(np.logical_and(X == 0, y_true == 1))

    if tp == 0:
        return 0
    return tp / (tp + fn)

def positive_predictive_value(X: NDArray, y_true: NDArray, window_size: int = 1) -> float:
    '''
    AKA precision
    PPV = True Positive / (True Positive + False Positive)
    '''
    assert len(X) == len(y_true)

    y_large = true_values(y_true, window_size)

    tp = np.count_nonzero(np.logical_and(X == 1, y_large == 1))
    fp = np.count_nonzero(np.logical_and(X == 1, y_large == 0))

    if tp == 0:
        return 0
    return tp / (tp + fp)

def false_positive_rate(X: NDArray, y_true: NDArray, window_size=1) -> float:
    '''
    FPR = False Positives / (False Positives + True Negatives)
    '''
    assert len(X) == len(y_true)

    y_large = true_values(y_true, window_size)

    fp = np.count_nonzero(np.logical_and(X == 1, y_large == 0))
    tn = np.count_nonzero(np.logical_and(X == 0, y_large == 0))
    
    if fp == 0:
        return 0
    return fp / (fp + tn)

def accuracy(X, y_true):
    assert len(X) == len(y_true)
    
    return np.count_nonzero(X == y_true) / len(y_true)

def apply_window(X, size=10):
    # 1 index ~20ms -> 10 ~200 ms
    res = np.array_split(X, np.arange(0, len(X), size)[1:])
    last_size = res[-1].shape[0]
    res[-1] = np.concatenate([np.zeros(size-last_size), res[-1]], axis=None)
    res = np.sum(res, axis=1)
    res[res > 0] = 1
    return res

def activation_functions_metrics(H, y_true, thresholds=[0,1], window=0):
    # setup thresholding
    threshold_generator = ThresholdGenerator(activation_function_matrix=H)
    generated_threshold = threshold_generator.generate_threshold()
    
    N = H.shape[0]
    
    ppv = [[] for _ in range(N)]
    tpr = [[] for _ in range(N)]
    fpr = [[] for _ in range(N)]
    event_count = [[] for _ in range(N)]
    y_preds = [[] for _ in range(N)]
    
    if window > 0:
        y_true = apply_window(y_true, window)
    
    for threshold in (thresholds):
        annotations = threshold_generator.find_events(threshold)
        annotations = [annotations[key] for key in annotations.keys()]

        for index, events in enumerate(annotations):
            y_score = events['event_mask']
            
            if window > 0:
                y_score = apply_window(y_score, window)
            
            tn, fp, fn, tp = confusion_matrix(y_true, y_score).ravel()
            
            if tp == 0:
                ppv[index].append(0)
                tpr[index].append(0)
            else:
                ppv[index].append(tp / (tp + fp))            
                tpr[index].append(tp / (tp + fn))
            
            if fp == 0:
                fpr[index].append(0)
            else:
                fpr[index].append(fp / (fp + tn))
            
            event_count[index].append(y_score.sum())
            y_preds[index].append(y_score)

    return ppv, tpr, fpr, event_count, generated_threshold, y_preds

def auc_roc_pr(ppv, tpr, fpr):
    return auc(tpr, ppv), auc(fpr, tpr)
