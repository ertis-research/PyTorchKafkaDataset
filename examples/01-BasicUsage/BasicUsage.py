import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision.transforms import ToTensor

# Cuando se haga paquete como tal, podremos borrar las dos siguientes lineas
from sys import path
path.append('C:\\Users\\AntonioJ\\Trabajo\\PyTorch\\PyTorchKafkaDataset\\src')

from TrainingKafkaDataset import TrainingKafkaDataset

# Defining a Model
class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28*28, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 10),
            nn.ReLU()
        )
    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

# Define Train Function
def train(dataloader, model, loss_fn, optimizer, device):
    size = len(dataloader.dataset)
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)
        
        # Compute prediction error
        pred = model(X)
        loss = loss_fn(pred, y)
        
        # Backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch % 100 == 0:
            loss, current = loss.item(), batch * len(X)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")

# Define Test Function
def test(dataloader, model, loss_fn, device):
    size = len(dataloader.dataset)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
    test_loss /= size
    correct /= size
    print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")

###################################

# Control message to Kafka 
kafkaControl = {'topic': 'pytorch_mnist_test:0:0:20000,pytorch:0:20000:50000,pytorch_mnist_test:0:120000:140000',
                'input_config': {'data_type': 'uint8', 
                                 'label_type': 'uint8', 
                                 'data_reshape': '28 28', 
                                 'label_reshape': ''}, 
                }
boo_svr = ["localhost:9094"]
grp_id = 'sink'

df = TrainingKafkaDataset(kafkaControl, boo_svr, grp_id, ToTensor())

print("Dataset length", len(df))

train_set, test_set = torch.utils.data.random_split(df, [60000, 10000]) # Podria splitear segun el validation_rate y el total_msg, pero he preferido seguir con el ejemplo

batch_size = 64
train_dataloader = DataLoader(train_set, batch_size=batch_size)
test_dataloader  = DataLoader(test_set, batch_size=batch_size)

for X, y in train_dataloader:
    print("Shape of X [N, C, H, W]: ", X.shape)
    print("Shape of y: ", y.shape, y.dtype)
    break

# Get cpu or gpu device for training.
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using {} device".format(device))

model = NeuralNetwork().to(device)
print(model)

loss_fn = nn.CrossEntropyLoss()
learning_rate = 1e-3
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)

epochs = 15
for t in range(epochs):
    print(f"Epoch {t+1}\n-------------------------------")
    train(train_dataloader, model, loss_fn, optimizer, device)
    test(test_dataloader, model, loss_fn, device)
print("Done!")