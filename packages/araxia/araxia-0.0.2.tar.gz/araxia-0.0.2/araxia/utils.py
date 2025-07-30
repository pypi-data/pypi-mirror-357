def exp_custom(x, terms=10):
    result = 1.0 # x^0 / 0
    numerator = 1.0
    denominator = 1.0

    for n in range(1, terms):
        numerator *= x
        denominator *= n
        result += numerator / denominator

    return result

def dot_custom(a, b):
    return sum(a[i] * b[i] for i in range(len(a)))

def sigmoid(z):
    return 1 / (1 + exp_custom(-z))

def sigmoid_derivative(x):
    s = sigmoid(x)
    return s * (1 - s)

def train_test_split(X, y, test_size=0.2):
    if len(X) != len(y):
        raise ValueError(f"X and y must have the same length: X: {len(X)}, y: {len(y)}")
    
    n = X.shape[0]
    stop = int(n - (n * test_size))
    X_train = X.iloc[0:stop, :-1]
    y_train = y.iloc[0:stop, -1:]

    X_test = X.iloc[stop:, :-1]
    y_test = y.iloc[stop:, -1:]
    return X_train, y_train, X_test, y_test