import numpy as np
from .utils import dot_custom, sigmoid, sigmoid_derivative


# Single Neuron
class Neuron:
    """A single neuron with weights and bias, using sigmoid activation."""
    def __init__(self, n_inputs, activation=True):
        # Initialize weights and bias
        self.weights = np.random.randn(n_inputs) * 0.1 # scaled init
        self.bias = 0.0
        self.activation = activation

    def forward(self, x):
        self.last_input = x
        self.last_z = dot_custom(self.weights, x) + self.bias
        self.last_output = sigmoid(self.last_z) if self.activation else self.last_z
        return self.last_output

    def backward(self, dL_dy, learning_rate):
        # Ensure input is 1D
        self.last_input = np.asarray(self.last_input).flatten()

        if self.activation:
            dz = sigmoid_derivative(self.last_z) * dL_dy
        else:
            dz = dL_dy

        dz = float(np.squeeze(dz))

        for i in range(len(self.weights)):
            self.weights[i] -= learning_rate * dz * self.last_input[i]
        self.bias -= learning_rate * dz
    
# Fully Connected Layer
class Layer:
    """A layer of neurons, each neuron can have its own activation function."""
    def __init__(self, n_inputs, n_neurons, activation=True):
        self.neurons = [Neuron(n_inputs, activation=activation) for _ in range(n_neurons)]

    def forward(self, x):
        self.last_input = x
        self.outputs = np.array([neuron.forward(x) for neuron in self.neurons])
        return self.outputs

    def backward(self, dL_dy_list, learning_rate):
        for neuron, dL_dy in zip(self.neurons, dL_dy_list):
            neuron.backward(dL_dy, learning_rate)
    
# Multi-Layer Perceptron with Backprop
class MLP:
    """A simple Multi-Layer Perceptron with one hidden layer and backpropagation.
    
    Paramters:
        - input_size: Number of input features.
        - hidden_size: Number of neurons in the hidden layer.
        - learning_rate: Learning rate for weight updates."""
    def __init__(self, input_size, hidden_size, learning_rate=0.01):
        self.hidden = Layer(input_size, hidden_size,  activation=True)
        self.output = Neuron(hidden_size, activation=False)
        self.lr = learning_rate
        self.loss_history = []

    def forward(self, x):
        self.hidden_output = self.hidden.forward(x)
        return self.output.forward(self.hidden_output)

    def compute_loss(self, y_true, y_pred):
        return (y_true - y_pred) ** 2

    def compute_loss_derivative(self, y_true, y_pred):
        return -2 * (y_true - y_pred)

    def train(self, X, y, epochs=100):
        for epoch in range(epochs):
            total_loss = 0
            for xi, yi in zip(X, y):
                y_pred = self.forward(xi)
                loss = self.compute_loss(yi, y_pred)
                total_loss += loss
                dL_dy = self.compute_loss_derivative(yi, y_pred)
                
                # Backward pass
                self.output.backward(dL_dy, self.lr)
                dL_dh = dL_dy * self.output.weights  # Gradient w.r.t. each hidden neuron output
                self.hidden.backward(dL_dh, self.lr)


            avg_loss = total_loss / len(X)
            self.loss_history.append(avg_loss)

            if epoch % 10 == 0:
                print(f"epoch: {epoch}, | loss: {avg_loss:.6f}")

    def predict(self, X):
        return [self.forward(xi) for xi in X]