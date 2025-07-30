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
import torchvision.models as models

class ResNetWrapper(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.resnet = models.resnet18(weights=None)
        # CIFAR-10 images are 3x32x32, while ImageNet are 3x224x224.
        # We adapt the first conv layer.
        self.resnet.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.resnet.maxpool = nn.Identity()
        num_ftrs = self.resnet.fc.in_features
        self.resnet.fc = nn.Linear(num_ftrs, num_classes)

    def forward(self, x):
        return self.resnet(x)

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

    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    cifar10_data_dir = "temp_data/CIFAR10"
    svhn_data_dir = "temp_data/SVHN"
    output_dir = "output/"

    os.makedirs(cifar10_data_dir, exist_ok=True)
    os.makedirs(svhn_data_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    train_dataset = datasets.CIFAR10(cifar10_data_dir, train=True, download=True, transform=transform_train)
    val_dataset = datasets.CIFAR10(cifar10_data_dir, train=False, download=True, transform=transform_test)
    ood_val_dataset = datasets.SVHN(svhn_data_dir, split='test', download=True, transform=transform_test)

    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=100, shuffle=False, num_workers=2)
    ood_val_loader = DataLoader(ood_val_dataset, batch_size=100, shuffle=False, num_workers=2)

    model = ResNetWrapper().to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()

    pi_monitor = SigmaPI(alpha=1.0, gamma=0.5)

    # Initialize metric dictionaries
    metric_keys = ['loss', 'acc', 'pi', 'surprise', 'tau']
    step_metrics = {f'train_{key}': [] for key in metric_keys}
    
    epoch_metrics = {f'train_{key}': [] for key in metric_keys}
    for val_set in ['cifar10_val', 'svhn_ood']:
        for key in metric_keys:
            epoch_metrics[f'{val_set}_{key}'] = []

    epochs = 5
    global_step = 0
    for epoch in range(1, epochs + 1):
        print(f"\n--- Epoch {epoch} ---")
        global_step = train(model, device, train_loader, optimizer, epoch, loss_fn, pi_monitor, step_metrics, epoch_metrics, global_step)

        # In-distribution validation
        val_loss, val_acc, val_pi, val_surprise, val_tau = validate(model, device, val_loader, loss_fn, pi_monitor, dataset_name="CIFAR10 Val")
        epoch_metrics['cifar10_val_loss'].append((global_step - 1, val_loss))
        epoch_metrics['cifar10_val_acc'].append((global_step - 1, val_acc))
        epoch_metrics['cifar10_val_pi'].append((global_step - 1, val_pi))
        epoch_metrics['cifar10_val_surprise'].append((global_step - 1, val_surprise))
        epoch_metrics['cifar10_val_tau'].append((global_step - 1, val_tau))

        # OOD validation
        ood_loss, ood_acc, ood_pi, ood_surprise, ood_tau = validate(model, device, ood_val_loader, loss_fn, pi_monitor, dataset_name="SVHN OOD")
        epoch_metrics['svhn_ood_loss'].append((global_step - 1, ood_loss))
        epoch_metrics['svhn_ood_acc'].append((global_step - 1, ood_acc))
        epoch_metrics['svhn_ood_pi'].append((global_step - 1, ood_pi))
        epoch_metrics['svhn_ood_surprise'].append((global_step - 1, ood_surprise))
        epoch_metrics['svhn_ood_tau'].append((global_step - 1, ood_tau))

    plot_metrics(step_metrics, epoch_metrics, output_dir, model_name="ResNet-CIFAR10-OOD_Step")
    print(f"\nPlots saved to: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
