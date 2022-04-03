import pywt
import numpy as np
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV

def forecast(data):
    '''
    Decomposes 1-D array "data" into multiple components using Discrete Wavelet Transform,
    denoises each component using thresholding, 
    use Support Vector Regression (SVR) to forecast each component,
    recombine components for aggregate forecast

    returns: the value of the aggregate forecast 1 time-step into the future
    '''

    w = pywt.Wavelet('sym6')  # Daubechies/Symlets are good choices for denoising 
    
    threshold = 0.1 #standard 

    # Decompose into wavelet components
    coeffs = pywt.wavedec(data, w)
    
    # if we want at least 3 levels (components), solve for:
    #   log2(len(data) / wave_length - 1) >= 3. 16 *10
    #   in this case, since we wave_length(sym6) == 11, after solving we get len(data) >= 152,
    #   hence why our RollingWindow is of length 152 in main.py

    for i in range(len(coeffs)):
        if i > 0:
            # we don't want to threshold the approximation coefficients
            coeffs[i] = pywt.threshold(coeffs[i], threshold*max(coeffs[i]))
        forecasted = __svm_forecast(coeffs[i])
        coeffs[i] = np.roll(coeffs[i], -1)
        coeffs[i][-1] = forecasted
        
    datarec = pywt.waverec(coeffs, w)
    return datarec[-1]

def __svm_forecast(data, sample_size=10):
    '''
    Paritions "data" and fits an SVM model to this data, then forecasts the
    value one time-step into the future
    '''
    X, y = __partition_array(data, size=sample_size)

    param_grid = {'C': [.05, .1, .5, 1, 5, 10], 'epsilon': [0.001, 0.005, 0.01, 0.05, 0.1]}
    gsc = GridSearchCV(SVR(), param_grid, scoring='neg_mean_squared_error')
    
    model = gsc.fit(X, y).best_estimator_

    return model.predict(data[np.newaxis, -sample_size:])[0]
    
def __partition_array(arr, size=None, splits=None):
    '''
    partitions 1-D array "arr" in a Rolling fashion if "size" is specified, 
    else, divides the into "splits" pieces

    returns: list of paritioned arrays, list of the values 1 step ahead of each partitioned array
    '''

    arrs = []
    values = []

    if not (bool(size is None) ^ bool(splits is None)):
        raise ValueError('Size XOR Splits should not be None')

    if size:
        arrs = [arr[i:i + size] for i in range(len(arr) - size)]
        values = [arr[i] for i in range(size, len(arr))]

    elif splits:
        size = len(arr) // splits
        if len(arr) % size == 0:
            arrs = [arr[i:i + size] for i in range(size - 1, len(arr) - 1, size)]
            values = [arr[i] for i in range(2 * size - 1, len(arr), size)]
        else:
            arrs = [arr[i:i + size] for i in range(len(arr) % size - 1, len(arr) - 1, size)]
            values = [arr[value].iloc[i] for i in range(len(arr) % size + size - 1, len(arr), size)]

    return np.array(arrs), np.array(values)
