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