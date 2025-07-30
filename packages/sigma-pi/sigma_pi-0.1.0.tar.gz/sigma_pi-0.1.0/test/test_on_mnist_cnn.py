import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from main import SigmaPI
from test.plot_utils import plot_metrics

class AddGaussianNoise(object):
    def __init__(self, mean=0., std=1.):
        self.std = std
        self.mean = mean
        
    def __call__(self, tensor):
        return tensor + torch.randn(tensor.size()) * self.std + self.mean
    
    def __repr__(self):
        return self.__class__.__name__ + '(mean={0}, std={1})'.format(self.mean, self.std)

class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(2)
        self.fc1 = nn.Linear(32 * 7 * 7, 64)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(64, 10)

    def forward(self, x):
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = x.view(-1, 32 * 7 * 7)
        x = self.relu3(self.fc1(x))
        return self.fc2(x)

def train(model, device, train_loader, optimizer, epoch, loss_fn, pi_monitor, step_metrics, epoch_metrics, global_step):
    model.train()
    epoch_summary = {
        'loss': [], 'acc': [], 'pi': [], 'surprise': [], 'tau': []
    }

    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        logits = model(data)
        loss_epsilon = loss_fn(logits, target)
        loss_epsilon.backward()
        optimizer.step()

        pi_metrics = pi_monitor.calculate(model, loss_epsilon, logits)
        pred = logits.argmax(dim=1, keepdim=True)
        correct = pred.eq(target.view_as(pred)).sum().item()
        accuracy = 100. * correct / len(data)

        # Record step-level metrics
        step_metrics['train_loss'].append((global_step, loss_epsilon.item()))
        step_metrics['train_acc'].append((global_step, accuracy))
        step_metrics['train_pi'].append((global_step, pi_metrics['pi_score']))
        step_metrics['train_surprise'].append((global_step, pi_metrics['surprise']))
        step_metrics['train_tau'].append((global_step, pi_metrics['tau']))

        # Accumulate for epoch summary
        epoch_summary['loss'].append(loss_epsilon.item())
        epoch_summary['acc'].append(accuracy)
        epoch_summary['pi'].append(pi_metrics['pi_score'])
        epoch_summary['surprise'].append(pi_metrics['surprise'])
        epoch_summary['tau'].append(pi_metrics['tau'])

        if batch_idx % 100 == 0:
            print(f"Train Epoch: {epoch} [{batch_idx * len(data)}/{len(train_loader.dataset)} ({100. * batch_idx / len(train_loader):.0f}%)]\tLoss: {loss_epsilon.item():.6f}\tPI: {pi_metrics['pi_score']:.4f}\tSurprise: {pi_metrics['surprise']:.4f}\tTau: {pi_metrics['tau']:.4f}")
        
        global_step += 1
    
    # Record epoch-level metrics
    avg_loss = sum(epoch_summary['loss']) / len(epoch_summary['loss'])
    avg_acc = sum(epoch_summary['acc']) / len(epoch_summary['acc'])
    avg_pi = sum(epoch_summary['pi']) / len(epoch_summary['pi'])
    avg_surprise = sum(epoch_summary['surprise']) / len(epoch_summary['surprise'])
    avg_tau = sum(epoch_summary['tau']) / len(epoch_summary['tau'])
    
    epoch_metrics['train_loss'].append((global_step - 1, avg_loss))
    epoch_metrics['train_acc'].append((global_step - 1, avg_acc))
    epoch_metrics['train_pi'].append((global_step - 1, avg_pi))
    epoch_metrics['train_surprise'].append((global_step - 1, avg_surprise))
    epoch_metrics['train_tau'].append((global_step - 1, avg_tau))

    print(f"Train Epoch {epoch} Summary: Avg loss: {avg_loss:.4f}, Avg Accuracy: {avg_acc:.2f}%\tAvg PI: {avg_pi:.4f}\tAvg Surprise: {avg_surprise:.4f}\tAvg Tau: {avg_tau:.4f}")
    
    return global_step

def validate(model, device, val_loader, loss_fn, pi_monitor, dataset_name="Validation"):
    model.eval()
    val_loss, correct = 0, 0
    all_pi_scores, all_surprises, all_taus = [], [], []
    
    for data, target in val_loader:
        data, target = data.to(device), target.to(device)
        
        logits = model(data)
        loss_epsilon = loss_fn(logits, target)
        
        model.zero_grad()
        loss_epsilon.backward()
        
        pi_metrics = pi_monitor.calculate(model, loss_epsilon, logits)
        all_pi_scores.append(pi_metrics['pi_score'])
        all_surprises.append(pi_metrics['surprise'])
        all_taus.append(pi_metrics['tau'])

        with torch.no_grad():
            val_loss += loss_epsilon.item()
            pred = logits.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

    avg_loss = val_loss / len(val_loader)
    accuracy = 100. * correct / len(val_loader.dataset)
    avg_pi = sum(all_pi_scores) / len(all_pi_scores) if all_pi_scores else 0
    avg_surprise = sum(all_surprises) / len(all_surprises) if all_surprises else 0
    avg_tau = sum(all_taus) / len(all_taus) if all_taus else 0

    print(f"{dataset_name} set: Average loss: {avg_loss:.4f}, Accuracy: {correct}/{len(val_loader.dataset)} ({accuracy:.0f}%)\tAvg PI: {avg_pi:.4f}\tAvg Surprise: {avg_surprise:.4f}\tAvg Tau: {avg_tau:.4f}")
    return avg_loss, accuracy, avg_pi, avg_surprise, avg_tau


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    mnist_data_dir = "temp_data/MNIST"
    fashion_mnist_data_dir = "temp_data/FashionMNIST"
    output_dir = "output/"

    os.makedirs(mnist_data_dir, exist_ok=True)
    os.makedirs(fashion_mnist_data_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    train_dataset = datasets.MNIST(mnist_data_dir, train=True, download=True, transform=transform)
    val_dataset = datasets.MNIST(mnist_data_dir, train=False, download=True, transform=transform)
    ood_val_dataset = datasets.FashionMNIST(fashion_mnist_data_dir, train=False, download=True, transform=transform)

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=1000, shuffle=False)
    ood_val_loader = DataLoader(ood_val_dataset, batch_size=1000, shuffle=False)

    noisy_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,)),
        AddGaussianNoise(0., 1.0)
    ])
    noisy_mnist_val_dataset = datasets.MNIST(mnist_data_dir, train=False, download=True, transform=noisy_transform)
    noisy_mnist_val_loader = DataLoader(noisy_mnist_val_dataset, batch_size=1000, shuffle=False)

    model = SimpleCNN().to(device)
    optimizer = optim.Adam(model.parameters())
    loss_fn = nn.CrossEntropyLoss()

    pi_monitor = SigmaPI(alpha=1.0, gamma=0.5)

    # Initialize metric dictionaries
    metric_keys = ['loss', 'acc', 'pi', 'surprise', 'tau']
    step_metrics = {f'train_{key}': [] for key in metric_keys}
    
    epoch_metrics = {f'train_{key}': [] for key in metric_keys}
    for val_set in ['mnist_val', 'noisy_mnist_val', 'fashionmnist_ood']:
        for key in metric_keys:
            epoch_metrics[f'{val_set}_{key}'] = []

    epochs = 5
    global_step = 0
    for epoch in range(1, epochs + 1):
        print(f"\n--- Epoch {epoch} ---")
        global_step = train(model, device, train_loader, optimizer, epoch, loss_fn, pi_monitor, step_metrics, epoch_metrics, global_step)

        # Validation for MNIST
        val_loss, val_acc, val_pi, val_surprise, val_tau = validate(model, device, val_loader, loss_fn, pi_monitor, dataset_name="MNIST Val")
        epoch_metrics['mnist_val_loss'].append((global_step - 1, val_loss))
        epoch_metrics['mnist_val_acc'].append((global_step - 1, val_acc))
        epoch_metrics['mnist_val_pi'].append((global_step - 1, val_pi))
        epoch_metrics['mnist_val_surprise'].append((global_step - 1, val_surprise))
        epoch_metrics['mnist_val_tau'].append((global_step - 1, val_tau))

        # Validation for Noisy MNIST
        noisy_val_loss, noisy_val_acc, noisy_val_pi, noisy_val_surprise, noisy_val_tau = validate(model, device, noisy_mnist_val_loader, loss_fn, pi_monitor, dataset_name="Noisy MNIST Val")
        epoch_metrics['noisy_mnist_val_loss'].append((global_step - 1, noisy_val_loss))
        epoch_metrics['noisy_mnist_val_acc'].append((global_step - 1, noisy_val_acc))
        epoch_metrics['noisy_mnist_val_pi'].append((global_step - 1, noisy_val_pi))
        epoch_metrics['noisy_mnist_val_surprise'].append((global_step - 1, noisy_val_surprise))
        epoch_metrics['noisy_mnist_val_tau'].append((global_step - 1, noisy_val_tau))

        # Validation for FashionMNIST OOD
        ood_val_loss, ood_val_acc, ood_val_pi, ood_val_surprise, ood_val_tau = validate(model, device, ood_val_loader, loss_fn, pi_monitor, dataset_name="FashionMNIST OOD")
        epoch_metrics['fashionmnist_ood_loss'].append((global_step - 1, ood_val_loss))
        epoch_metrics['fashionmnist_ood_acc'].append((global_step - 1, ood_val_acc))
        epoch_metrics['fashionmnist_ood_pi'].append((global_step - 1, ood_val_pi))
        epoch_metrics['fashionmnist_ood_surprise'].append((global_step - 1, ood_val_surprise))
        epoch_metrics['fashionmnist_ood_tau'].append((global_step - 1, ood_val_tau))

    plot_metrics(step_metrics, epoch_metrics, output_dir, model_name="SimpleCNN_Step")
    print(f"\nPlots saved to: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
