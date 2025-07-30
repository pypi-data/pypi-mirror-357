# AlgoMake

**AlgoMake** is a powerful Machine Learning library designed for deep understanding, with every algorithm meticulously built from scratch using pure NumPy. Explore the core mechanics of ML without abstraction.

---

## Overview

**AlgoMake** offers a unique approach to learning and implementing machine learning. It's a comprehensive collection of fundamental algorithms, each developed from first principles with a strong emphasis on clarity and mathematical accuracy, relying solely on NumPy.

This project serves as an invaluable resource for anyone looking to gain a transparent and educational understanding of machine learning models.

---

## Why Choose AlgoMake?

In a landscape dominated by high-level ML frameworks, **AlgoMake** stands out by providing:

- **Unparalleled Transparency:** Every algorithm's core logic is exposed, allowing users to see exactly how computations are performed.
- **Pure NumPy Implementation:** Eliminates external dependencies for core algorithm computations, making the underlying mathematics explicit.
- **Enhanced Learning:** Ideal for students and practitioners who want to master the mathematical foundations and inner workings of ML models.

---

## Key Features

AlgoMake currently includes a growing suite of carefully engineered algorithms:

### Core Algorithms (`algomake/models/`)

- **Gaussian Mixture Models (GMM):**
  - Complete Expectation-Maximization (EM) algorithm from scratch
  - Custom implementation of the multivariate Gaussian PDF
  - Robust handling of numerical stability

- **Support Vector Machines (SVM):** 
  - Planned: Dual formulation, Hinge loss, Kernel trick, SMO algorithm

- **Other Models:**
  - Linear Regression, Logistic Regression 
  - K-Nearest Neighbors (KNN)
  - Decision Trees
  - Ensemble Methods (Bagging, Boosting)
  - Clustering Algorithms (K-Means)

### Preprocessing & Dimensionality Reduction (`algomake/preprocessing/`)

- **Principal Component Analysis (PCA):**
  - Manual computation of eigenvectors and eigenvalues
  - Covariance matrix and dimensionality reduction pipeline

- **Standardization/Normalization**

### Utility Components

- **BaseEstimator:** A foundational class providing a consistent `fit`, `predict`, `get_params`, and `set_params` interface.
- **Metrics:** Custom implementations of classification and regression evaluation metrics.

---

## Installation

To integrate AlgoMake into your Python environment:

```bash
git clone https://github.com/ShutterStack/AlgoMake.git
cd algomake
pip install -e .
```

For development (includes testing, formatting, etc.):

```bash
pip install -e .[dev]
```

---

## Usage Examples

### Gaussian Mixture Models (GMM)

```python
import numpy as np
from algomake.models.gmm import GaussianMixture

# Generate sample data
np.random.seed(0)
data_1 = np.random.multivariate_normal([2.0, 2.0], [[0.5, 0.2], [0.2, 0.5]], 100)
data_2 = np.random.multivariate_normal([8.0, 8.0], [[0.7, -0.3], [-0.3, 0.7]], 100)
X_train = np.vstack((data_1, data_2))

gmm = GaussianMixture(n_components=2, random_state=42, max_iter=100, tol=1e-4)
gmm.fit(X_train)

X_new = np.array([[2.1, 1.9], [8.3, 7.8], [5.0, 5.0]])
predicted_labels = gmm.predict(X_new)
probabilities = gmm.predict_proba(X_new)

print("Labels:", predicted_labels)
print("Probabilities:", np.round(probabilities, 4))
```

---

### Principal Component Analysis (PCA)

```python
import numpy as np
from algomake.preprocessing.dimensionality_reduction import PCA

X = np.array([
    [2.5, 2.4], [0.5, 0.7], [2.2, 2.9],
    [1.9, 2.2], [3.1, 3.0], [2.3, 2.7],
    [2.0, 1.6], [1.0, 1.1], [1.5, 1.6], [1.1, 0.9]
])

pca = PCA(n_components=1)
pca.fit(X)
X_transformed = pca.transform(X)

print("Transformed Data:", np.round(X_transformed, 3))
```

---

## Running Tests

Run all unit tests using `pytest`:

```bash
pytest
```
---

## Contributing

We welcome and encourage contributions! 🚀

To contribute:

1. Fork the repository  
2. Clone your fork:
   ```bash
   git clone https://github.com/ShutterStack/AlgoMake.git
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Implement changes  
5. Add unit tests  
6. Run `pytest` to ensure all tests pass  
7. Format with `black` and `isort`  
8. Commit and push your changes  
9. Open a Pull Request

---

## License

This project is licensed under the **MIT License**.

---

## Contact

Have questions, suggestions, or want to collaborate?

- GitHub Issues: [Submit here](https://github.com/ShutterStack/AlgoMake.git/issues)
- Email: patilarya3133@gmail.com

---

Enjoy learning ML from the inside out with **AlgoMake**!