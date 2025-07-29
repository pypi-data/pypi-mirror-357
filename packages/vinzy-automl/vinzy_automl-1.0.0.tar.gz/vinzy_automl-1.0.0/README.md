# Vinzy AutoML - Automated Machine Learning Package by Vinayak Bhosale

**Vinzy AutoML** is a comprehensive automated machine learning package that simplifies the process of model selection, hyperparameter tuning, and performance evaluation. Designed for both beginners and experienced data scientists, it supports over 60 machine learning models with parallel processing capabilities.

---

## 🔑 Key Features

- 🚀 Automated model selection for regression and classification problems  
- ⚡ Parallel training using multithreading for faster execution  
- 📊 Comprehensive performance metrics with built-in visualization tools  
- 🔍 Hyperparameter tuning with GridSearchCV  
- 🤖 Support for 60+ models including:
  - Scikit-learn models
  - XGBoost, LightGBM, and CatBoost (optional)  
- 🎯 Automatic best model selection based on problem type  
- 🎨 Beautiful visualizations including performance charts and radar plots

---

## 📦 Installation

Install the base package:

```bash
pip install vinzy_automl
```

For full functionality including XGBoost, LightGBM, and CatBoost:

```bash
pip install vinzy_automl[full]
```

---

## 🧪 Basic Usage

### 🔹 Regression Example

```python
from vinzy_automl import AutoML
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split

# Create sample dataset
X, y = make_regression(n_samples=1000, n_features=20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Initialize and train AutoML
automl = AutoML()
results = automl.fit(
    X_train, y_train,
    X_test, y_test,
    problem_type='regression', #or 'classification'
    grid_search=['RandomForest', 'XGBoost'],  # Models to tune
    exclude_models=['Lasso', 'Ridge'],        # Models to skip
    max_workers=4                             # Threads to use
)

# View results
print(results)
# View results in a dataframe
print(automl.get_results_in_dataframe(sort_by='R2'))
automl.plot_performance()
```

### 🔹 Classification Example

```python
from vinzy_automl import AutoML
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

# Create sample dataset
X, y = make_classification(n_samples=1000, n_classes=3)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Initialize and train AutoML
automl = AutoML()
results = automl.fit(
    X_train, y_train,
    X_test, y_test,
    problem_type='classification', #or 'regression'
    grid_search=['RandomForest', 'XGBoost'],  # Models to tune
    exclude_models=['GaussianNB', 'MultinomialNB'],   # Models to skip
    max_workers=4                             # Threads to use
)

# Get best model and make predictions
best_name, best_model, best_score = automl.get_best_model()
predictions = automl.predict(X_test)

# Visualize results
automl.plot_model_comparison_radar()
```

# To obtain models names use
```python
# To obtain models names use
print(automl.nomenclature())
```

---

## ⚙️ Advanced Features

### 🔧 Custom Models and Parameters

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

# Add custom models
custom_models = {
    'MyRF': RandomForestRegressor(n_estimators=200),
    'MySVR': SVR(kernel='poly')
}

# Custom hyperparameter grids
custom_params = {
    'MyRF': {'max_depth': [5, 10, None]},
    'MySVR': {'C': [0.1, 1, 10], 'degree': [2, 3]}
}

automl.fit(
    X_train, y_train,
    X_test, y_test,
    problem_type='regression',
    custom_models=custom_models,
    custom_param_grids=custom_params
)
```

### 🧵 Full Pipeline Training

```python
# Train best model on full dataset
final_model = automl.train_best_model(X_full, y_full)

# Save the trained model
import joblib
joblib.dump(final_model, 'best_model.pkl')
```

---

## 📊 Visualization Options

```python
# Performance comparison
automl.plot_performance(figsize=(12, 8), save_path='performance.png')

# Training time analysis
automl.plot_training_time_comparison()

# Radar chart of top 5 models
automl.plot_model_comparison_radar()
```

---

## 📚 Supported Models

### ✅ Regression (40+ Models)

```text
LinearRegression, Ridge, Lasso, ElasticNet, BayesianRidge, KernelRidge, 
Lars, LassoLars, OrthogonalMatchingPursuit, PassiveAggressiveRegressor, 
SGDRegressor, HuberRegressor, TheilSenRegressor, RANSACRegressor, 
QuantileRegressor, DecisionTree, RandomForest, ExtraTrees, GradientBoosting, 
AdaBoost, VotingRegressor, BaggingRegressor, HistGradientBoosting, SVR, 
LinearSVR, NuSVR, KNN, MLP, GaussianProcess, XGBoost, LightGBM, CatBoost
```

### ✅ Classification (40+ Models)

```text
LogisticRegression, GaussianNB, MultinomialNB, BernoulliNB, 
LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis, 
PassiveAggressiveClassifier, SGDClassifier, RidgeClassifier, Perceptron, 
DecisionTree, RandomForest, ExtraTrees, GradientBoosting, AdaBoost, 
VotingClassifier, BaggingClassifier, HistGradientBoosting, SVC, LinearSVC, 
NuSVC, KNN, MLP, GaussianProcess, LabelPropagation, LabelSpreading, 
XGBoost, LightGBM, CatBoost
```

---

## ℹ️ Package Information

```python
automl = AutoML()
automl.author()
```

```
╔══════════════════════════════════════════════════════════════╗
║                         AutoML Package                       ║
║    An Automated Machine Learning Library By Vinayak Bhosale  ║
╚══════════════════════════════════════════════════════════════╝

📦 Package: AutoML
👨‍💻 Author: Vinayak Bhosale
📅 Copyright: © 2025
🔖 Version: 1.0.0
📄 License: MIT License
📝 Description: A comprehensive AutoML library for automated machine learning

🚀 Features:
   🤖 Automated model selection and training
   🔄 Multi-threaded parallel processing
   📊 Comprehensive performance visualization
   🔍 Hyperparameter optimization with GridSearch
   📈 Support for regression and classification
   🎯 20+ built-in machine learning algorithms
   ⚡ Support for XGBoost, LightGBM, and CatBoost
   📋 Detailed performance metrics and comparisons
   💾 Model persistence and reusability
   🎨 Beautiful visualization with radar charts

====================================================================
Thank you for using AutoML! Happy Machine Learning! 🎉
====================================================================
```

---

## 📘 Documentation

For detailed usage and customization:

```python
# View help guide
automl.help_automl()

# View method documentation
help(AutoML.fit)
help(AutoML.plot_performance)
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.