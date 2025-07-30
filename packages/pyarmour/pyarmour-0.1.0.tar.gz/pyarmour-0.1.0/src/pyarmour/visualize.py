import numpy as np
import matplotlib.pyplot as plt
from typing import Union, Tuple, Optional, List
from matplotlib import colors

def plot_images(images: np.ndarray, labels: np.ndarray, predictions: np.ndarray, 
                adversarial: bool = False, num_images: int = 5,
                show_difference: bool = False, 
                cmap: str = 'gray') -> None:
    """Plot multiple images with their labels and predictions.
    
    Args:
        images: Input images
        labels: True labels
        predictions: Model predictions
        adversarial: Whether these are adversarial examples
        num_images: Number of images to display
        show_difference: Whether to show difference map
        cmap: Colormap to use
    """
    fig = plt.figure(figsize=(15, 3))
    
    for i in range(min(num_images, len(images))):
        plt.subplot(1, num_images, i + 1)
        img = images[i]
        
        # If image is in channel-first format (1, 28, 28), convert to channel-last
        if img.shape[0] == 1:
            img = img[0]
        
        plt.imshow(img, cmap=cmap)
        
        title = f"Label: {labels[i]}
Prediction: {np.argmax(predictions[i])}"
        if adversarial:
            title = "Adversarial " + title
        
        plt.title(title)
        plt.axis('off')
    
    plt.tight_layout()
    plt.show()

def plot_accuracy_curve(accuracies: np.ndarray, epsilons: Optional[np.ndarray] = None,
                       title: str = "Accuracy vs Epsilon") -> None:
    """Plot the accuracy curve.
    
    Args:
        accuracies: Array of accuracies
        epsilons: Corresponding epsilon values
        title: Plot title
    """
    plt.figure(figsize=(10, 5))
    
    if epsilons is not None:
        plt.plot(epsilons, accuracies, marker='o')
        plt.xlabel("Epsilon")
    else:
        plt.plot(accuracies)
        plt.xlabel("Iteration")
    
    plt.title(title)
    plt.ylabel("Accuracy")
    plt.grid(True)
    plt.show()

def plot_perturbation_distribution(perturbations: np.ndarray, 
                                  title: str = "Perturbation Distribution",
                                  bins: int = 50) -> None:
    """Plot the distribution of perturbation magnitudes.
    
    Args:
        perturbations: Array of perturbations
        title: Plot title
        bins: Number of histogram bins
    """
    plt.figure(figsize=(10, 5))
    plt.hist(np.abs(perturbations).flatten(), bins=bins)
    plt.title(title)
    plt.xlabel("Perturbation Magnitude")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()

def plot_difference_map(original: np.ndarray, adversarial: np.ndarray,
                       title: str = "Difference Map") -> None:
    """Plot the difference map between original and adversarial images.
    
    Args:
        original: Original images
        adversarial: Adversarial images
        title: Plot title
    """
    difference = adversarial - original
    
    # Normalize difference map
    diff_min = difference.min()
    diff_max = difference.max()
    diff_range = diff_max - diff_min
    
    fig = plt.figure(figsize=(10, 5))
    
    # Plot difference map
    plt.subplot(1, 2, 1)
    plt.imshow(difference[0], cmap='seismic',
              norm=colors.Normalize(vmin=-diff_range/2, vmax=diff_range/2))
    plt.colorbar()
    plt.title(title)
    plt.axis('off')
    
    # Plot absolute difference
    plt.subplot(1, 2, 2)
    plt.imshow(np.abs(difference[0]), cmap='gray')
    plt.colorbar()
    plt.title("Absolute Difference")
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

def plot_confusion_matrix(original_preds: np.ndarray, adv_preds: np.ndarray,
                         labels: np.ndarray, num_classes: int = 10) -> None:
    """Plot confusion matrix comparing original and adversarial predictions.
    
    Args:
        original_preds: Original predictions
        adv_preds: Adversarial predictions
        labels: True labels
        num_classes: Number of classes
    """
    from sklearn.metrics import confusion_matrix
    import seaborn as sns
    
    # Get predicted classes
    original_classes = np.argmax(original_preds, axis=1)
    adv_classes = np.argmax(adv_preds, axis=1)
    
    # Create confusion matrices
    original_cm = confusion_matrix(labels, original_classes, labels=np.arange(num_classes))
    adv_cm = confusion_matrix(labels, adv_classes, labels=np.arange(num_classes))
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot original confusion matrix
    sns.heatmap(original_cm, annot=True, fmt='d', cmap='Blues', ax=ax1)
    ax1.set_title('Original Predictions')
    ax1.set_xlabel('Predicted')
    ax1.set_ylabel('True')
    
    # Plot adversarial confusion matrix
    sns.heatmap(adv_cm, annot=True, fmt='d', cmap='Reds', ax=ax2)
    ax2.set_title('Adversarial Predictions')
    ax2.set_xlabel('Predicted')
    ax2.set_ylabel('True')
    
    plt.tight_layout()
    plt.show()
