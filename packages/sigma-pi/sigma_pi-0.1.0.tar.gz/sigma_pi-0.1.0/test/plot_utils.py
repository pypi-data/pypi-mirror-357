import matplotlib.pyplot as plt
import os
from datetime import datetime
from typing import Dict, List, Tuple

def plot_metrics(
    step_metrics: Dict[str, List[Tuple[int, float]]],
    epoch_metrics: Dict[str, List[Tuple[int, float]]],
    output_dir: str,
    model_name: str = "model"
) -> None:
    
    plt.figure(figsize=(18, 15))
    
    metric_types = ['loss', 'acc', 'pi', 'surprise', 'tau']
    plot_titles = {
        'loss': 'Loss',
        'acc': 'Accuracy',
        'pi': 'Predictive Integrity (PI)',
        'surprise': 'Surprise (Gradient Norm)',
        'tau': 'Tau (Entropy)'
    }
    y_labels = {
        'loss': 'Loss',
        'acc': 'Accuracy (%)',
        'pi': 'PI Score',
        'surprise': 'Surprise',
        'tau': 'Tau'
    }

    for i, metric_type in enumerate(metric_types):
        plt.subplot(3, 2, i + 1)
        
        # Plot step-level data (only for training)
        train_key = f'train_{metric_type}'
        if train_key in step_metrics and step_metrics[train_key]:
            steps, values = zip(*step_metrics[train_key])
            plt.plot(steps, values, alpha=0.5, label=f'Train {metric_type} (Step)')

        # Plot epoch-level data
        for key, data in epoch_metrics.items():
            if metric_type in key and data:
                steps, values = zip(*data)
                label = key.replace('_', ' ').title()
                plt.plot(steps, values, marker='o', linestyle='-', label=f'{label} (Epoch Avg)')

        plt.title(f'{plot_titles[metric_type]} over Steps')
        plt.xlabel('Global Steps')
        plt.ylabel(y_labels[metric_type])
        plt.legend()
        plt.grid(True)

    plt.tight_layout()
    
    current_date = datetime.now().strftime("%Y%m%d")
    file_name = f"{current_date}-{model_name}.png"
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()
