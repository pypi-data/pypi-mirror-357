# SigmaPI: Observe the Mind of Your Model

[![PyPI version](https://badge.fury.io/py/sigma-pi.svg)](https://badge.fury.io/py/sigma-pi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SigmaPI** is a lightweight, universal SDK to calculate Predictive Integrity (PI), a metric from the Integrated Predictive Workspace Theory (IPWT) of consciousness. It provides a powerful, real-time proxy for your model's "cognitive state" during training.

Stop just looking at `loss`. Start observing how your model _learns_.

## Why Use SigmaPI?

- **Early Warning for Training Instability:** Detects subtle shifts in model "cognition" before loss metrics diverge.
- **Insight into OOD Impact:** Quantifies the "surprise" your model experiences when encountering out-of-distribution data.
- **Understanding Model Overfitting:** Reveals when your model's internal world becomes too rigid or too chaotic.
- **Quantifying Cognitive Load:** Provides a novel metric for the "effort" your model expends to integrate new information.

## What is Predictive Integrity (PI)?

PI is a single score from 0 to 1 that reflects the integrity of a model's internal world model. It's calculated from three core components:

1. **Epsilon (ε):** The raw prediction error (scalar loss value).
2. **Tau (τ):** The model's own uncertainty, derived from its output logits.
3. **Surprise (S):** The global gradient norm. How much does the model need to change its "worldview" to accommodate new data?

A high PI score indicates a healthy learning state: the model is accurate, confident, and stable. A sudden drop in PI can signal overfitting, bad data, or an impending collapse in training stability, often _before_ the loss function shows clear signs of trouble.

## Model Zoo: Comparative Results

Here's a comparison of how different architectures handle in-distribution (CIFAR-10) vs. out-of-distribution (SVHN) data.

| SimpleCNN (on MNIST) | ResNet (on CIFAR-10) | Vision Transformer (on CIFAR-10) |
| :---: | :---: | :---: |
| *A simple CNN on a simple task.* | *Deeper architecture, but struggles with OOD.* | *ViT shows more robust PI on OOD data.* |
| <img src="output/20250625-SimpleCNN_Step.png" width="300"> | <img src="output/20250625-ResNet-CIFAR10-OOD_Step.png" width="300"> | <img src="output\20250625-ViT-CIFAR10-OOD_Step.png" width="300"> |

## Installation

```bash
pip install sigma-pi
```

## How to Use

Integrate it into your PyTorch training loop in just three steps:

```python
from main import SigmaPI

# 1. Initialize the monitor
pi_monitor = SigmaPI(alpha=1.0, gamma=0.5)

# 2. In your training loop
logits = model(data)
loss = loss_fn(logits, target)
loss.backward()  # Compute gradients before PI calculation

# 3. Calculate PI metrics
pi_metrics = pi_monitor.calculate(
    model=model,
    loss_epsilon=loss,
    logits=logits
)

# Access metrics
print(f"Loss: {loss.item():.4f}, PI: {pi_metrics['pi_score']:.4f}, Surprise: {pi_metrics['surprise']:.4f}")
```

The returned `pi_metrics` dictionary contains:

- `pi_score`: The overall predictive integrity (0-1)
- `surprise`: Gradient norm indicating model adaptation
- `normalized_error`: Error scaled by model uncertainty
- `cognitive_cost`: Combined cost of error and surprise
- Additional component metrics for detailed analysis

## Further Reading

PI is a concept derived from the **Integrated Predictive Workspace Theory (IPWT)**, a computational theory of consciousness. To understand the deep theory behind this tool, please refer to:

- **IPWT:** <https://github.com/dmf-archive/IPWT>
- **OpenPoPI:** [Private] - The original research-grade implementation used to validate the theory on EEG data.

## License

This project is licensed under the MIT License.
