# AlgoMake

A custom machine learning library built from scratch to deepen understanding of fundamental algorithms.

## Overview

AlgoMake is a personal project aimed at implementing various machine learning models and utility functions without relying heavily on established libraries like Scikit-learn or TensorFlow for core algorithm logic. The goal is to provide transparent and educational implementations of common machine learning concepts.

## Features

-   **Base Estimator:** A foundational `BaseEstimator` class for consistent API design.
-   **Gaussian Mixture Models (GMM):** A complete implementation of GMM using the Expectation-Maximization (EM) algorithm, optimized to run without `scipy` dependencies for its core components.
-   **K-Nearest Neighbors (KNN):** (Mention if implemented)
-   **Linear Models:** (Mention if implemented, e.g., Linear Regression, Logistic Regression)
-   **Preprocessing Tools:** (Mention if implemented, e.g., StandardScaler, MinMaxScaler)
-   **Evaluation Metrics:** (Mention if implemented, e.g., Accuracy, MSE)
-   **Modular Design:** Easy to extend with new algorithms.
-   **Comprehensive Testing:** Each component is rigorously tested using `pytest`.

## Installation

You can install AlgoMake directly from source:

```bash
git clone [https://github.com/yourusername/AlgoMake.git](https://github.com/yourusername/AlgoMake.git)
cd AlgoMake
pip install -e .