import numpy as np
import pandas as pd
import time
import concurrent.futures
from queue import Queue
from typing import List, Dict, Optional, Tuple, Any

# Core scikit-learn imports
from sklearn.linear_model import (
    LinearRegression, Ridge, Lasso, ElasticNet, LogisticRegression,
    BayesianRidge, Lars, LassoLars, OrthogonalMatchingPursuit,
    PassiveAggressiveRegressor, SGDRegressor, PassiveAggressiveClassifier, SGDClassifier,
    HuberRegressor,
    QuantileRegressor,
    TheilSenRegressor,
    RANSACRegressor,
    RidgeClassifier,
    Perceptron,
)
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestRegressor, RandomForestClassifier,
    GradientBoostingRegressor, GradientBoostingClassifier,
    AdaBoostRegressor, AdaBoostClassifier,
    ExtraTreesRegressor, ExtraTreesClassifier,
    VotingRegressor, VotingClassifier,
    BaggingRegressor, BaggingClassifier,
    HistGradientBoostingRegressor, HistGradientBoostingClassifier,
)
from sklearn.svm import SVR, SVC, LinearSVR, LinearSVC, NuSVR, NuSVC
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.gaussian_process import GaussianProcessRegressor, GaussianProcessClassifier
from sklearn.kernel_ridge import KernelRidge
from sklearn.semi_supervised import LabelPropagation, LabelSpreading
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
import warnings


# Try to import additional models (XGBoost, LightGBM, CatBoost, HistGradientBoosting)
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    import catboost as cb
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

try:
    from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
    HIST_GRADIENT_BOOSTING_AVAILABLE = True
except ImportError:
    HIST_GRADIENT_BOOSTING_AVAILABLE = False

class AutoML:
    """
    AutoML class for automatic machine learning model selection and training.

    This class allows users to:
    - Train multiple ML models in parallel using threading
    - Compare model performance across different metrics
    - Optionally perform grid search on selected models
    - Train the best model based on performance
    """

    def __init__(self):
        self.models = {}
        self.results = {}
        self.best_model = None
        self.best_model_name = None
        self.best_score = None
        self.trained_models = {}
        self.problem_type = None
        self.is_fitted = False


    def _get_regression_models(self) -> Dict:

        """Get dictionary of regression models with additional models."""

        models = {
            # Your existing models...
            'LinearRegression': LinearRegression(),
            'Ridge': Ridge(),
            'Lasso': Lasso(),
            'ElasticNet': ElasticNet(),
            'BayesianRidge': BayesianRidge(),
            'KernelRidge': KernelRidge(),
            'Lars': Lars(),
            'LassoLars': LassoLars(),
            'OrthogonalMatchingPursuit': OrthogonalMatchingPursuit(),
            'PassiveAggressiveRegressor': PassiveAggressiveRegressor(max_iter=1000),
            'SGDRegressor': SGDRegressor(max_iter=1000),

            # Additional Linear Models
            'HuberRegressor': HuberRegressor(),
            'TheilSenRegressor': TheilSenRegressor(),
            'RANSACRegressor': RANSACRegressor(),

            # Tree-based models
            'DecisionTree': DecisionTreeRegressor(),
            'RandomForest': RandomForestRegressor(),
            'ExtraTrees': ExtraTreesRegressor(),
            'GradientBoosting': GradientBoostingRegressor(),
            'AdaBoost': AdaBoostRegressor(),
                      'VotingRegressor':VotingRegressor(estimators=[
                  ('ridge', Ridge(alpha=1.0)),
                  ('dt', DecisionTreeRegressor(max_depth=5))
              ]),


            # Additional Ensemble Models
            'BaggingRegressor': BaggingRegressor(),
            'HistGradientBoosting': HistGradientBoostingRegressor(),

            # SVM Models
            'SVR': SVR(),
            'LinearSVR': LinearSVR(max_iter=1000),
            'NuSVR': NuSVR(),

            # Other Models
            'KNN': KNeighborsRegressor(),
            'MLP': MLPRegressor(max_iter=1000),
            'GaussianProcess': GaussianProcessRegressor(),
        }

        # Add QuantileRegressor if sklearn version supports it
        try:
            models['QuantileRegressor'] = QuantileRegressor()
        except:
            pass

        # Add XGBoost if available
        if XGBOOST_AVAILABLE:
            models['XGBoost'] = xgb.XGBRegressor()

        # Add LightGBM if available
        if LIGHTGBM_AVAILABLE:
            models['LightGBM'] = lgb.LGBMRegressor()

        # Add CatBoost if available
        if CATBOOST_AVAILABLE:
            models['CatBoost'] = cb.CatBoostRegressor(verbose=0)

        if HIST_GRADIENT_BOOSTING_AVAILABLE:
            models['HistGradientBoostingRegressor'] = HistGradientBoostingRegressor()

        return models


    def _get_classification_models(self) -> Dict:
        """Get dictionary of classification models with additional models."""
        models = {
            # Your existing models...
            'LogisticRegression': LogisticRegression(max_iter=1000),
            'GaussianNB': GaussianNB(),
            'MultinomialNB': MultinomialNB(),
            'BernoulliNB': BernoulliNB(),
            'LinearDiscriminantAnalysis': LinearDiscriminantAnalysis(),
            'QuadraticDiscriminantAnalysis': QuadraticDiscriminantAnalysis(),
            'PassiveAggressiveClassifier': PassiveAggressiveClassifier(max_iter=1000),
            'SGDClassifier': SGDClassifier(max_iter=1000),

            # Additional Linear Models
            'RidgeClassifier': RidgeClassifier(),
            'Perceptron': Perceptron(max_iter=1000),

            # Tree-based models
            'DecisionTree': DecisionTreeClassifier(),
            'RandomForest': RandomForestClassifier(),
            'ExtraTrees': ExtraTreesClassifier(),
            'GradientBoosting': GradientBoostingClassifier(),
            'AdaBoost': AdaBoostClassifier(),
            'VotingClassifier':VotingClassifier(estimators=[
                    ('lr', LogisticRegression()),
                    ('dt', DecisionTreeClassifier()),
                    ('svc', SVC(probability=True))  # probability=True required for 'soft' voting
                ], voting='soft'),  # or 'hard',

            # Additional Ensemble Models
            'BaggingClassifier': BaggingClassifier(),
            'HistGradientBoosting': HistGradientBoostingClassifier(),

            # SVM Models
            'SVC': SVC(probability=True),
            'LinearSVC': LinearSVC(max_iter=1000, dual=False),
            'NuSVC': NuSVC(probability=True),

            # Other Models
            'KNN': KNeighborsClassifier(),
            'MLP': MLPClassifier(max_iter=1000),
            'GaussianProcess': GaussianProcessClassifier(),

            # Semi-supervised models (if you have unlabeled data)
            'LabelPropagation': LabelPropagation(),
            'LabelSpreading': LabelSpreading(),
        }

        # Add XGBoost if available
        if XGBOOST_AVAILABLE:
            models['XGBoost'] = xgb.XGBClassifier()

        # Add LightGBM if available
        if LIGHTGBM_AVAILABLE:
            models['LightGBM'] = lgb.LGBMClassifier()

        # Add CatBoost if available
        if CATBOOST_AVAILABLE:
            models['CatBoost'] = cb.CatBoostClassifier(verbose=0)

        if HIST_GRADIENT_BOOSTING_AVAILABLE:
            models['HistGradientBoostingClassifier'] = HistGradientBoostingClassifier()

        return models

    def _get_default_param_grids(self) -> Dict:
        """Get default parameter grids for grid search."""
        param_grids = {
            # Linear models
            'LinearRegression': {'fit_intercept': [True, False], 'positive': [True, False]},
            'Ridge': {'alpha': [0.01, 0.1, 1.0, 10.0, 100.0]},
            'Lasso': {'alpha': [0.01, 0.1, 1.0, 10.0, 100.0]},
            'ElasticNet': {'alpha': [0.01, 0.1, 1.0, 10.0], 'l1_ratio': [0.1, 0.5, 0.9]},
            'BayesianRidge': {'alpha_1': [1e-6, 1e-5, 1e-4], 'alpha_2': [1e-6, 1e-5, 1e-4]},
            'KernelRidge': {'alpha': [0.1, 1.0, 10.0], 'kernel': ['linear', 'rbf']},
            'Lars': {'n_nonzero_coefs': [None, 10, 20], 'eps': [1e-4, 1e-3]},
            'LassoLars': {'alpha': [0.01, 0.1, 1.0]},
            'OrthogonalMatchingPursuit': {'n_nonzero_coefs': [5, 10, 15, 20, None]},
            'PassiveAggressiveRegressor': {'C': [0.1, 1.0, 10.0], 'max_iter': [1000]},
            'SGDRegressor': {'alpha': [0.0001, 0.001, 0.01], 'loss': ['squared_error', 'huber'], 'max_iter': [1000]},

            # Tree-based models
            'DecisionTree': {'max_depth': [None, 5, 10, 15], 'min_samples_split': [2, 5, 10]},
            'RandomForest': {'n_estimators': [50, 100, 200], 'max_depth': [None, 10, 20]},
            'ExtraTrees': {'n_estimators': [50, 100, 200], 'max_depth': [None, 10, 20]},
            'GradientBoosting': {'n_estimators': [50, 100, 200], 'learning_rate': [0.01, 0.1, 0.2], 'max_depth': [3, 5, 7]},
            'AdaBoost': {'n_estimators': [50, 100, 200], 'learning_rate': [0.01, 0.1, 1.0]},

            # SVM models
            'SVR': {'C': [0.1, 1, 10], 'kernel': ['linear', 'rbf', 'poly'], 'gamma': ['scale', 'auto']},
            'LinearSVR': {'C': [0.1, 1, 10], 'loss': ['epsilon_insensitive', 'squared_epsilon_insensitive']},
            'SVC': {'C': [0.1, 1, 10], 'kernel': ['linear', 'rbf', 'poly'], 'gamma': ['scale', 'auto']},
            'LinearSVC': {'C': [0.1, 1, 10], 'loss': ['hinge', 'squared_hinge']},

            # Other models
            'KNN': {'n_neighbors': [3, 5, 7, 9], 'weights': ['uniform', 'distance']},
            'MLP': {'hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 50)], 'alpha': [0.0001, 0.001, 0.01], 'max_iter': [1000]},
            'LogisticRegression': {'C': [0.1, 1, 10, 100], 'solver': ['liblinear', 'lbfgs']},

            # Naive Bayes models
            'GaussianNB': {'var_smoothing': [1e-9, 1e-8, 1e-7]},
            'MultinomialNB': {'alpha': [0.1, 0.5, 1.0, 2.0]},
            'BernoulliNB': {'alpha': [0.1, 0.5, 1.0, 2.0]},

            # Discriminant Analysis
            'LinearDiscriminantAnalysis': {'solver': ['svd', 'lsqr']},
            'QuadraticDiscriminantAnalysis': {'reg_param': [0.0, 0.1, 0.5]},

            # Other classification models
            'PassiveAggressiveClassifier': {'C': [0.1, 1.0, 10.0], 'max_iter': [1000]},
            'SGDClassifier': {'alpha': [0.0001, 0.001, 0.01], 'loss': ['hinge', 'log_loss', 'modified_huber'], 'max_iter': [1000]},
             #Additional Linear Models
            'HuberRegressor': {'epsilon': [1.35, 1.5, 2.0], 'alpha': [0.0001, 0.001, 0.01]},
            'TheilSenRegressor': {'max_subpopulation': [1e4, 1e5]},
            'RANSACRegressor': {'max_trials': [100, 200, 500]},
            'QuantileRegressor': {'quantile': [0.25, 0.5, 0.75], 'alpha': [0.01, 0.1, 1.0]},
            'RidgeClassifier': {'alpha': [0.01, 0.1, 1.0, 10.0]},
            'Perceptron': {'alpha': [0.0001, 0.001, 0.01], 'max_iter': [1000]},

            # Additional Ensemble Models
            'BaggingRegressor': {'n_estimators': [10, 50, 100], 'max_samples': [0.5, 0.8, 1.0]},
            'BaggingClassifier': {'n_estimators': [10, 50, 100], 'max_samples': [0.5, 0.8, 1.0]},
            'HistGradientBoosting': {'learning_rate': [0.01, 0.1, 0.2], 'max_iter': [100, 200]},
            'VotingClassifier': {'voting': ['hard', 'soft'], 'weights': [None, [1, 1], [0.7, 0.3]], 'n_jobs': [-1]},
            'VotingRegressor': {'weights': [None, [1, 1], [0.7, 0.3]], 'n_jobs': [-1]},

            # Additional SVM Models
            'NuSVR': {'nu': [0.25, 0.5, 0.75], 'C': [0.1, 1, 10], 'kernel': ['linear', 'rbf']},
            'NuSVC': {'nu': [0.25, 0.5, 0.75], 'kernel': ['linear', 'rbf']},

            #Anomoly
            'IsolationForest': {'n_estimators': [50, 100, 200], 'max_samples': ['auto', 0.6, 0.8, 1.0], 'contamination': ['auto', 0.01, 0.05, 0.1], 'max_features': [0.5, 0.75, 1.0], 'bootstrap': [False, True], 'n_jobs': [-1]},
            # Gaussian Process
            'GaussianProcess': {
                'alpha': [1e-10, 1e-5, 1e-2],
                'normalize_y': [True, False],
                'n_restarts_optimizer': [0, 5, 10],
            },
            # Semi-supervised
            'LabelPropagation': {'kernel': ['knn', 'rbf'], 'gamma': [0.1, 1, 10]},
            'LabelSpreading': {'kernel': ['knn', 'rbf'], 'gamma': [0.1, 1, 10]},
        }

        # Add XGBoost parameters if available
        if XGBOOST_AVAILABLE:
            param_grids['XGBoost'] = {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.3],
                'max_depth': [3, 5, 7],
                'subsample': [0.8, 1.0]
            }

        # Add LightGBM parameters if available
        if LIGHTGBM_AVAILABLE:
            param_grids['LightGBM'] = {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.3],
                'max_depth': [3, 5, 7],
                'num_leaves': [31, 50, 100]
            }

        # Add CatBoost parameters if available
        if CATBOOST_AVAILABLE:
            param_grids['CatBoost'] = {
                'iterations': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.3],
                'depth': [4, 6, 8],
                'verbose': [0]
            }

        if HIST_GRADIENT_BOOSTING_AVAILABLE:
            param_grids['HistGradientBoosting'] = {
            'learning_rate': [0.01, 0.1, 0.2],
            'max_iter': [100, 200],
            'max_depth': [3, 5, 7],
            'min_samples_leaf': [20, 50, 100],
            'l2_regularization': [0.0, 0.1, 1.0],
            'max_leaf_nodes': [15, 31, 63]
        }

        return param_grids

    def _evaluate_regression_model(self, model_name: str, model: Any, X_train: np.ndarray,
                                  y_train: np.ndarray, X_test: np.ndarray,
                                  y_test: np.ndarray, results_queue: Queue) -> None:
        """
        Evaluate a regression model and put results in the queue.

        Args:
            model_name: Name of the model
            model: Model instance
            X_train, y_train: Training data
            X_test, y_test: Test data
            results_queue: Queue to store results
        """
        try:
            start_time = time.time()
            model.fit(X_train, y_train)
            train_time = time.time() - start_time

            # Make predictions
            y_pred = model.predict(X_test)

            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)

            results = {
                'model_name': model_name,
                'model': model,
                'mse': mse,
                'rmse': rmse,
                'r2': r2,
                'train_time': train_time
            }

            results_queue.put(results)
            print(f"Finished training {model_name}")
        except Exception as e:
            print(f"Error training {model_name}: {e}")
            results_queue.put({
                'model_name': model_name,
                'error': str(e)
            })

    def _evaluate_classification_model(self, model_name: str, model: Any, X_train: np.ndarray,
                                      y_train: np.ndarray, X_test: np.ndarray,
                                      y_test: np.ndarray, results_queue: Queue) -> None:
        """
        Evaluate a classification model and put results in the queue.

        Args:
            model_name: Name of the model
            model: Model instance
            X_train, y_train: Training data
            X_test, y_test: Test data
            results_queue: Queue to store results
        """
        try:
            start_time = time.time()
            model.fit(X_train, y_train)
            train_time = time.time() - start_time

            # Make predictions
            y_pred = model.predict(X_test)

            # For probabilities (used in ROC-AUC)
            try:
                y_prob = model.predict_proba(X_test)
                # Get the positive class probabilities for binary classification
                if y_prob.shape[1] == 2:
                    y_prob = y_prob[:, 1]
            except:
                y_prob = None

            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)

            # For binary classification
            binary = len(np.unique(y_test)) == 2

            if binary:
                precision = precision_score(y_test, y_pred, average='binary')
                recall = recall_score(y_test, y_pred, average='binary')
                f1 = f1_score(y_test, y_pred, average='binary')
                if y_prob is not None:
                    auc = roc_auc_score(y_test, y_prob)
                else:
                    auc = None
            else:
                precision = precision_score(y_test, y_pred, average='weighted')
                recall = recall_score(y_test, y_pred, average='weighted')
                f1 = f1_score(y_test, y_pred, average='weighted')
                auc = None

            results = {
                'model_name': model_name,
                'model': model,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'auc': auc,
                'train_time': train_time
            }

            results_queue.put(results)
            print(f"Finished training {model_name}")
        except Exception as e:
            print(f"Error training {model_name}: {e}")
            results_queue.put({
                'model_name': model_name,
                'error': str(e)
            })

    def _perform_grid_search(self, model_name: str, base_model: Any, param_grid: Dict,
                           X_train: np.ndarray, y_train: np.ndarray,
                           X_test: np.ndarray, y_test: np.ndarray,
                           results_queue: Queue, cv: int = 3) -> None:
        """
        Perform grid search for hyperparameter tuning and evaluate the best model.

        Args:
            model_name: Name of the model
            base_model: Base model instance
            param_grid: Parameter grid for grid search
            X_train, y_train: Training data
            X_test, y_test: Test data
            results_queue: Queue to store results
            cv: Number of cross-validation folds
        """
        try:
            if not param_grid:  # Skip if param_grid is empty
                if self.problem_type == 'regression':
                    self._evaluate_regression_model(model_name, base_model, X_train, y_train, X_test, y_test, results_queue)
                else:
                    self._evaluate_classification_model(model_name, base_model, X_train, y_train, X_test, y_test, results_queue)
                return

            print(f"Starting grid search for {model_name}...")
            start_time = time.time()

            # Perform grid search
            grid_search = GridSearchCV(
                estimator=base_model,
                param_grid=param_grid,
                cv=cv,
                n_jobs=-1,
                scoring='neg_mean_squared_error' if self.problem_type == 'regression' else 'accuracy'
            )

            grid_search.fit(X_train, y_train)
            best_model = grid_search.best_estimator_

            # Calculate training time
            train_time = time.time() - start_time

            # Evaluate the best model
            model_name = f"{model_name}_GridSearch"

            if self.problem_type == 'regression':
                y_pred = best_model.predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                r2 = r2_score(y_test, y_pred)

                results = {
                    'model_name': model_name,
                    'model': best_model,
                    'best_params': grid_search.best_params_,
                    'mse': mse,
                    'rmse': rmse,
                    'r2': r2,
                    'train_time': train_time
                }
            else:
                y_pred = best_model.predict(X_test)

                try:
                    y_prob = best_model.predict_proba(X_test)
                    if y_prob.shape[1] == 2:
                        y_prob = y_prob[:, 1]
                except:
                    y_prob = None

                accuracy = accuracy_score(y_test, y_pred)

                # For binary classification
                binary = len(np.unique(y_test)) == 2

                if binary:
                    precision = precision_score(y_test, y_pred, average='binary')
                    recall = recall_score(y_test, y_pred, average='binary')
                    f1 = f1_score(y_test, y_pred, average='binary')
                    if y_prob is not None:
                        auc = roc_auc_score(y_test, y_prob)
                    else:
                        auc = None
                else:
                    precision = precision_score(y_test, y_pred, average='weighted')
                    recall = recall_score(y_test, y_pred, average='weighted')
                    f1 = f1_score(y_test, y_pred, average='weighted')
                    auc = None

                results = {
                    'model_name': model_name,
                    'model': best_model,
                    'best_params': grid_search.best_params_,
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1': f1,
                    'auc': auc,
                    'train_time': train_time
                }

            results_queue.put(results)
            print(f"Finished grid search for {model_name}")
        except Exception as e:
            print(f"Error in grid search for {model_name}: {e}")
            results_queue.put({
                'model_name': model_name,
                'error': str(e)
            })

    def fit(self, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray,
           problem_type: str, grid_search: Optional[List[str]] = None,
           custom_models: Optional[Dict] = None, custom_param_grids: Optional[Dict] = None,
           exclude_models: Optional[List[str]] = None, max_workers: int = 4, ignore_warnings: bool = True) -> Dict:
        """
        Fit multiple models to the data and evaluate them.

        Args:
            X_train, y_train: Training data
            X_test, y_test: Test data
            problem_type: Type of problem ('regression' or 'classification')
            grid_search: List of model names to perform grid search on
            custom_models: Custom models to include
            custom_param_grids: Custom parameter grids for grid search
            max_workers: Maximum number of threads to use

        Returns:
            Dictionary of results
        """
        if ignore_warnings:
            warnings.filterwarnings('ignore')

        if problem_type not in ['regression', 'classification']:
            raise ValueError("problem_type must be either 'regression' or 'classification'")

        if exclude_models:
            for model_name in exclude_models:
                if model_name in self.models:
                    del self.models[model_name]

        self.problem_type = problem_type

        # Get appropriate models based on problem type
        if problem_type == 'regression':
            self.models = self._get_regression_models()
            if exclude_models:
              for model_name in exclude_models:
                  if model_name in self.models:
                      del self.models[model_name]
        else:
            self.models = self._get_classification_models()
            if exclude_models:
              for model_name in exclude_models:
                  if model_name in self.models:
                      del self.models[model_name]

        # Add custom models if provided
        if custom_models:
            self.models.update(custom_models)

        # Get default parameter grids
        param_grids = self._get_default_param_grids()

        # Update with custom parameter grids if provided
        if custom_param_grids:
            param_grids.update(custom_param_grids)

        # If grid_search is None, don't perform grid search on any model
        if grid_search is None:
            grid_search = []

        # Create a queue to store results
        results_queue = Queue()

        # Create threads for each model
        threads = []

        print(f"Training models using up to {max_workers} threads...")

        # Use ThreadPoolExecutor to limit the number of concurrent threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []

            for model_name, model in self.models.items():
                # Check if we should perform grid search on this model
                if model_name in grid_search:
                    # Submit grid search job
                    future = executor.submit(
                        self._perform_grid_search,
                        model_name,
                        model,
                        param_grids.get(model_name, {}),
                        X_train, y_train,
                        X_test, y_test,
                        results_queue
                    )
                else:
                    # Submit regular evaluation job
                    if problem_type == 'regression':
                        future = executor.submit(
                            self._evaluate_regression_model,
                            model_name,
                            model,
                            X_train, y_train,
                            X_test, y_test,
                            results_queue
                        )
                    else:
                        future = executor.submit(
                            self._evaluate_classification_model,
                            model_name,
                            model,
                            X_train, y_train,
                            X_test, y_test,
                            results_queue
                        )

                futures.append(future)

            # Wait for all futures to complete
            concurrent.futures.wait(futures)

        # Collect results
        while not results_queue.empty():
            result = results_queue.get()
            if 'error' in result:
                print(f"Model {result['model_name']} failed: {result['error']}")
                continue

            self.results[result['model_name']] = result

            # Store the trained model
            self.trained_models[result['model_name']] = result['model']

        # Find the best model
        self._find_best_model()

        self.is_fitted = True

        return self.get_results()

    def _find_best_model(self) -> None:
        """Find the best model based on the appropriate metric."""
        if not self.results:
            print("No models were successfully trained.")
            return

        if self.problem_type == 'regression':
            # For regression, lower RMSE is better
            best_score = float('inf')
            best_model_name = None

            for name, result in self.results.items():
                if result['rmse'] < best_score:
                    best_score = result['rmse']
                    best_model_name = name

            self.best_model_name = best_model_name
            self.best_model = self.results[best_model_name]['model']
            self.best_score = best_score

        else:
            # For classification, higher F1 score is better
            best_score = -float('inf')
            best_model_name = None

            for name, result in self.results.items():
                if result['f1'] > best_score:
                    best_score = result['f1']
                    best_model_name = name

            self.best_model_name = best_model_name
            self.best_model = self.results[best_model_name]['model']
            self.best_score = best_score

    def get_results(self) -> Dict:
        """Get the results of model evaluation."""
        if not self.is_fitted:
            raise ValueError("Models have not been fitted yet. Call fit() first.")

        formatted_results = {}

        if self.problem_type == 'regression':
            for name, result in self.results.items():
                formatted_results[name] = {
                    'MSE': result['mse'],
                    'RMSE': result['rmse'],
                    'R²': result['r2'],
                    'Training Time (s)': result['train_time']
                }
                if 'best_params' in result:
                    formatted_results[name]['Best Parameters'] = result['best_params']
        else:
            for name, result in self.results.items():
                formatted_results[name] = {
                    'Accuracy': result['accuracy'],
                    'Precision': result['precision'],
                    'Recall': result['recall'],
                    'F1 Score': result['f1'],
                    'Training Time (s)': result['train_time']
                }
                if result['auc'] is not None:
                    formatted_results[name]['AUC'] = result['auc']
                if 'best_params' in result:
                    formatted_results[name]['Best Parameters'] = result['best_params']

        return formatted_results

    def get_clean_results(self) -> None:
        """Get the results of model evaluation in a clean format."""
        if self.problem_type == 'regression':
            print("\n=== Regression Results ===:")
            for model_name, metrics in self.results.items():
                print(f"\n{model_name}:")
                for metric_name, value in metrics.items():
                    print(f"  {metric_name}: {value}")
            best_model_name, best_model, best_score = self.get_best_model()
            print(f"\nBest model: {best_model_name} with RMSE: {best_score}")

        else:
            print("\n=== Classification Results ===")
            for model, metrics in self.results.items():
                print(f"\n{model}:")
                for metric, value in metrics.items():
                    if isinstance(value, dict):
                        print(f"  {metric}:")
                        for k, v in value.items():
                            print(f"    {k}: {v}")
                    else:
                        print(f"  {metric}: {value}")
            best_name, best_model, best_score = self.get_best_model()
            print(f"\nBest Model: {best_name} (F1 Score: {best_score:.4f})")

    def get_results_in_dataframe(self, sort_by: str = None) -> pd.DataFrame:
        """
        Returns the model evaluation results as a pandas DataFrame, sorted by a specified metric.
        Automatically adapts to classification or regression metrics.

        Parameters:
            sort_by (str): Metric to sort by. Defaults to:
                          - "R²" for regression
                          - "Accuracy" for classification

        Returns:
            pd.DataFrame: Sorted model evaluation results.
        """
        results_df = pd.DataFrame(self.get_results()).T

        # Determine type from available columns
        if "R²" in results_df.columns:
            # Regression
            default_sort = "R²"
            sort_mapping = {
                "R2": ("R²", False),
                "RMSE": ("RMSE", True),
                "MSE": ("MSE", True),
                "T": ("Training Time (s)", True)
            }
        elif "Accuracy" in results_df.columns:
            # Classification
            default_sort = "Accuracy"
            sort_mapping = {
                "Accuracy": ("Accuracy", False),
                "Precision": ("Precision", False),
                "Recall": ("Recall", False),
                "F1": ("F1 Score", False),
                "AUC": ("AUC", False),
                "T": ("Training Time (s)", True)
            }
        else:
            raise ValueError("Unrecognized result format: no common metrics found.")

        # Determine metric to sort by
        if sort_by is None:
            column, ascending = default_sort, False
        else:
            if sort_by not in sort_mapping:
                raise ValueError(f"Invalid sort_by: {sort_by}. Choose from: {list(sort_mapping.keys())}")
            column, ascending = sort_mapping[sort_by]

        if column not in results_df.columns:
            raise ValueError(f"Metric '{column}' not found in results. Available columns: {list(results_df.columns)}")

        return results_df.sort_values(by=column, ascending=ascending)



    def get_best_model(self) -> Tuple[str, Any, float]:
        """Get the best model, its name, and its score."""
        if not self.is_fitted:
            raise ValueError("Models have not been fitted yet. Call fit() first.")

        return self.best_model_name, self.best_model, self.best_score

    def train_best_model(self, X_train: np.ndarray, y_train: np.ndarray) -> Any:
        """
        Train the best model on the full training set.

        Args:
            X_train, y_train: Training data

        Returns:
            Trained best model
        """
        if not self.is_fitted:
            raise ValueError("Models have not been fitted yet. Call fit() first.")

        print(f"Training the best model ({self.best_model_name}) on the full dataset...")

        # Create a fresh instance of the best model
        if '_GridSearch' in self.best_model_name:
            # For grid search models, use the best parameters
            base_model_name = self.best_model_name.replace('_GridSearch', '')

            if self.problem_type == 'regression':
                base_models = self._get_regression_models()
            else:
                base_models = self._get_classification_models()

            base_model = base_models[base_model_name]
            best_params = self.results[self.best_model_name]['best_params']

            # Create a new model with the best parameters
            best_model = type(base_model)(**best_params)
        else:
            # For regular models, use the same parameters
            best_model = type(self.best_model)()

        # Train the model on the full training set
        best_model.fit(X_train, y_train)

        return best_model

    def predict(self, X: np.ndarray, model_name: Optional[str] = None) -> np.ndarray:
        """
        Make predictions using a trained model.

        Args:
            X: Input features
            model_name: Name of the model to use (default: best model)

        Returns:
            Predictions
        """
        if not self.is_fitted:
            raise ValueError("Models have not been fitted yet. Call fit() first.")

        if model_name is None:
            # Use the best model
            model = self.best_model
        else:
            # Use the specified model
            if model_name not in self.trained_models:
                raise ValueError(f"Model '{model_name}' not found.")
            model = self.trained_models[model_name]

        return model.predict(X)

    def nomenclature(self):
      return {
          "Regression_models": list(self._get_regression_models().keys()),
          "Classification_models": list(self._get_classification_models().keys())
      }

    def author(self):
        """
        Display comprehensive package information including author details,
        version, features, and usage statistics.

        Returns:
            dict: Comprehensive package information
        """
        # ASCII Art Banner
        banner = """
        ╔══════════════════════════════════════════════════════════════╗
        ║                         AutoML Package                       ║
        ║    An Automated Machine Learning Library By Vinayak Bhosale  ║
        ╚══════════════════════════════════════════════════════════════╝
        """

        # Package information
        package_info = {
            "author": "Vinayak Bhosale",
            "copyright": "© 2025",
            "version": "1.0.0",
            "release_date": "2025",
            "license": "MIT License",
            "description": "A comprehensive AutoML library for automated machine learning",

            # Package features
            "features": [
                "🤖 Automated model selection and training",
                "🔄 Multi-threaded parallel processing",
                "📊 Comprehensive performance visualization",
                "🔍 Hyperparameter optimization with GridSearch",
                "📈 Support for regression and classification",
                "🎯 20+ built-in machine learning algorithms",
                "⚡ Support for XGBoost, LightGBM, and CatBoost",
                "📋 Detailed performance metrics and comparisons",
                "💾 Model persistence and reusability",
                "🎨 Beautiful visualization with radar charts"
            ],
        }

        # Print formatted information
        print(banner)
        print(f"📦 Package: AutoML")
        print(f"👨‍💻 Author: {package_info['author']}")
        print(f"📅 Copyright: {package_info['copyright']}")
        print(f"🔖 Version: {package_info['version']}")
        print(f"📄 License: {package_info['license']}")
        print(f"📝 Description: {package_info['description']}")

        print(f"\n🚀 Features:")
        for feature in package_info['features']:
            print(f"   {feature}")

        print(f"\n{'='*60}")
        print(f"Thank you for using AutoML! Happy Machine Learning! 🎉")
        print(f"{'='*60}")


    def plot_performance(self, figsize: Tuple[int, int] = (15, 10), save_path: Optional[str] = None) -> None:
        """
        Plot performance metrics for all trained models.

        Args:
            figsize: Figure size (width, height)
            save_path: Path to save the plot (optional)
        """
        if not self.is_fitted:
            raise ValueError("Models have not been fitted yet. Call fit() first.")

        if not self.results:
            print("No results to plot.")
            return

        # Set style
        plt.style.use('seaborn-v0_8')

        if self.problem_type == 'regression':
            # Create subplots for regression metrics
            fig, axes = plt.subplots(2, 2, figsize=figsize)
            fig.suptitle('Model Performance Comparison - Regression', fontsize=16, fontweight='bold')

            # Extract data
            model_names = list(self.results.keys())
            mse_values = [self.results[name]['mse'] for name in model_names]
            rmse_values = [self.results[name]['rmse'] for name in model_names]
            r2_values = [self.results[name]['r2'] for name in model_names]
            train_times = [self.results[name]['train_time'] for name in model_names]

            # Sort models by RMSE for better visualization
            sorted_indices = np.argsort(rmse_values)
            model_names = [model_names[i] for i in sorted_indices]
            mse_values = [mse_values[i] for i in sorted_indices]
            rmse_values = [rmse_values[i] for i in sorted_indices]
            r2_values = [r2_values[i] for i in sorted_indices]
            train_times = [train_times[i] for i in sorted_indices]

            # Color the best model differently
            colors = ['#2E86AB' if name != self.best_model_name else '#A23B72' for name in model_names]

            # Plot 1: RMSE
            axes[0, 0].barh(model_names, rmse_values, color=colors)
            axes[0, 0].set_xlabel('RMSE')
            axes[0, 0].set_title('Root Mean Square Error (Lower is Better)')
            axes[0, 0].grid(True, alpha=0.3)

            # Plot 2: R² Score
            axes[0, 1].barh(model_names, r2_values, color=colors)
            axes[0, 1].set_xlabel('R² Score')
            axes[0, 1].set_title('R² Score (Higher is Better)')
            axes[0, 1].grid(True, alpha=0.3)

            # Plot 3: MSE
            axes[1, 0].barh(model_names, mse_values, color=colors)
            axes[1, 0].set_xlabel('MSE')
            axes[1, 0].set_title('Mean Square Error (Lower is Better)')
            axes[1, 0].grid(True, alpha=0.3)

            # Plot 4: Training Time
            axes[1, 1].barh(model_names, train_times, color=colors)
            axes[1, 1].set_xlabel('Training Time (seconds)')
            axes[1, 1].set_title('Training Time')
            axes[1, 1].grid(True, alpha=0.3)

        else:  # Classification
            # Determine number of subplots based on available metrics
            has_auc = any(self.results[name]['auc'] is not None for name in self.results.keys())
            n_plots = 5 if has_auc else 4

            if n_plots == 5:
                fig, axes = plt.subplots(2, 3, figsize=(18, 10))
                axes = axes.flatten()
                # Remove the last subplot if we have 5 metrics
                fig.delaxes(axes[5])
            else:
                fig, axes = plt.subplots(2, 2, figsize=figsize)
                axes = axes.flatten()

            fig.suptitle('Model Performance Comparison - Classification', fontsize=16, fontweight='bold')

            # Extract data
            model_names = list(self.results.keys())
            accuracy_values = [self.results[name]['accuracy'] for name in model_names]
            precision_values = [self.results[name]['precision'] for name in model_names]
            recall_values = [self.results[name]['recall'] for name in model_names]
            f1_values = [self.results[name]['f1'] for name in model_names]
            train_times = [self.results[name]['train_time'] for name in model_names]

            if has_auc:
                auc_values = [self.results[name]['auc'] if self.results[name]['auc'] is not None else 0
                            for name in model_names]

            # Sort models by F1 score for better visualization
            sorted_indices = np.argsort(f1_values)[::-1]  # Descending order for F1
            model_names = [model_names[i] for i in sorted_indices]
            accuracy_values = [accuracy_values[i] for i in sorted_indices]
            precision_values = [precision_values[i] for i in sorted_indices]
            recall_values = [recall_values[i] for i in sorted_indices]
            f1_values = [f1_values[i] for i in sorted_indices]
            train_times = [train_times[i] for i in sorted_indices]

            if has_auc:
                auc_values = [auc_values[i] for i in sorted_indices]

            # Color the best model differently
            colors = ['#2E86AB' if name != self.best_model_name else '#A23B72' for name in model_names]

            # Plot 1: Accuracy
            axes[0].barh(model_names, accuracy_values, color=colors)
            axes[0].set_xlabel('Accuracy')
            axes[0].set_title('Accuracy (Higher is Better)')
            axes[0].grid(True, alpha=0.3)

            # Plot 2: Precision
            axes[1].barh(model_names, precision_values, color=colors)
            axes[1].set_xlabel('Precision')
            axes[1].set_title('Precision (Higher is Better)')
            axes[1].grid(True, alpha=0.3)

            # Plot 3: Recall
            axes[2].barh(model_names, recall_values, color=colors)
            axes[2].set_xlabel('Recall')
            axes[2].set_title('Recall (Higher is Better)')
            axes[2].grid(True, alpha=0.3)

            # Plot 4: F1 Score
            axes[3].barh(model_names, f1_values, color=colors)
            axes[3].set_xlabel('F1 Score')
            axes[3].set_title('F1 Score (Higher is Better)')
            axes[3].grid(True, alpha=0.3)

            # Plot 5: AUC (if available)
            if has_auc:
                axes[4].barh(model_names, auc_values, color=colors)
                axes[4].set_xlabel('AUC')
                axes[4].set_title('AUC (Higher is Better)')
                axes[4].grid(True, alpha=0.3)

        # Adjust layout
        plt.tight_layout()

        # Add legend for best model
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor='#2E86AB', label='Other Models'),
                          Patch(facecolor='#A23B72', label=f'Best Model: {self.best_model_name}')]
        fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2)

        # Save plot if path is provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")

        # Show plot
        plt.show()

    def plot_training_time_comparison(self, figsize: Tuple[int, int] = (12, 8), save_path: Optional[str] = None) -> None:
        """
        Plot a dedicated comparison of training times across all models.

        Args:
            figsize: Figure size (width, height)
            save_path: Path to save the plot (optional)
        """
        if not self.is_fitted:
            raise ValueError("Models have not been fitted yet. Call fit() first.")

        if not self.results:
            print("No results to plot.")
            return

        plt.figure(figsize=figsize)

        # Extract data
        model_names = list(self.results.keys())
        train_times = [self.results[name]['train_time'] for name in model_names]

        # Sort by training time
        sorted_indices = np.argsort(train_times)
        model_names = [model_names[i] for i in sorted_indices]
        train_times = [train_times[i] for i in sorted_indices]

        # Create color gradient
        colors = plt.cm.viridis(np.linspace(0, 1, len(model_names)))

        # Create horizontal bar plot
        bars = plt.barh(model_names, train_times, color=colors)

        # Customize plot
        plt.xlabel('Training Time (seconds)', fontsize=12)
        plt.title('Model Training Time Comparison', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='x')

        # Add value labels on bars
        for i, (bar, time_val) in enumerate(zip(bars, train_times)):
            plt.text(bar.get_width() + max(train_times) * 0.01, bar.get_y() + bar.get_height()/2,
                    f'{time_val:.2f}s', va='center', fontsize=10)

        plt.tight_layout()

        # Save plot if path is provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Training time plot saved to {save_path}")

        plt.show()

    def plot_model_comparison_radar(self, figsize: Tuple[int, int] = (10, 10), save_path: Optional[str] = None) -> None:
        """
        Create a radar chart comparing top 5 models across different metrics.

        Args:
            figsize: Figure size (width, height)
            save_path: Path to save the plot (optional)
        """
        if not self.is_fitted:
            raise ValueError("Models have not been fitted yet. Call fit() first.")

        if not self.results:
            print("No results to plot.")
            return

        # Get top 5 models
        if self.problem_type == 'regression':
            # Sort by R² score (higher is better)
            sorted_models = sorted(self.results.items(), key=lambda x: x[1]['r2'], reverse=True)[:5]
            metrics = ['R²', 'RMSE_inv', 'Speed']  # RMSE_inv = 1/(1+RMSE) for radar chart
            metric_labels = ['R² Score', 'RMSE (Inverted)', 'Speed (Inverted)']
        else:
            # Sort by F1 score (higher is better)
            sorted_models = sorted(self.results.items(), key=lambda x: x[1]['f1'], reverse=True)[:5]
            metrics = ['Accuracy', 'Precision', 'Recall', 'F1', 'Speed']
            metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'Speed (Inverted)']

        if len(sorted_models) < 2:
            print("Need at least 2 models for radar chart.")
            return

        # Prepare data
        model_names = [name for name, _ in sorted_models]

        # Normalize metrics to 0-1 scale for radar chart
        data = []
        for name, result in sorted_models:
            if self.problem_type == 'regression':
                # Normalize R² (already 0-1 or can be negative)
                r2_norm = max(0, min(1, (result['r2'] + 1) / 2))  # Shift and scale
                # Invert and normalize RMSE
                max_rmse = max([r['rmse'] for _, r in self.results.items()])
                rmse_inv_norm = 1 - (result['rmse'] / max_rmse)
                # Invert and normalize training time
                max_time = max([r['train_time'] for _, r in self.results.items()])
                speed_norm = 1 - (result['train_time'] / max_time)

                data.append([r2_norm, rmse_inv_norm, speed_norm])
            else:
                # For classification, all metrics are already 0-1
                speed_norm = 1 - (result['train_time'] / max([r['train_time'] for _, r in self.results.items()]))
                data.append([result['accuracy'], result['precision'], result['recall'], result['f1'], speed_norm])

        # Create radar chart
        fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(projection='polar'))

        # Set up angles
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle

        # Colors for different models
        colors = plt.cm.Set3(np.linspace(0, 1, len(model_names)))

        # Plot each model
        for i, (model_data, model_name, color) in enumerate(zip(data, model_names, colors)):
            values = model_data + model_data[:1]  # Complete the circle
            ax.plot(angles, values, 'o-', linewidth=2, label=model_name, color=color)
            ax.fill(angles, values, alpha=0.25, color=color)

        # Customize the chart
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metric_labels)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'])
        ax.grid(True)

        plt.title(f'Top 5 Models Comparison - {self.problem_type.title()}',
                  size=16, fontweight='bold', pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

        plt.tight_layout()

        # Save plot if path is provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Radar chart saved to {save_path}")

        plt.show()

    def help_automl(self):
        """
        AutoML Package by Vinayak Bhosale - Help Guide
        ==============================================

        This AutoML package automates machine learning workflows including:
        - Model selection for regression and classification
        - Hyperparameter tuning with GridSearch
        - Performance evaluation
        - Visualization of results

        Key Features:
        - Supports 60+ models including XGBoost, LightGBM, CatBoost
        - Parallel training using multithreading
        - Comprehensive performance metrics
        - Visualization tools (bar charts, radar plots)
        - Automatic best model selection

        Basic Usage:
        ------------
        1. Initialize AutoML:
        automl = AutoML()

        2. Fit models:
        results = automl.fit(
            X_train, y_train,
            X_test, y_test,
            problem_type='regression' or 'classification',
            grid_search=['RandomForest', 'XGBoost'],  # Models to tune
            exclude_models=['Lasso', 'Ridge'],        # Models to skip
            max_workers=4                             # Threads to use
        )

        3. Get results:
        - automl.get_results()              # Returns dictionary of results
        - automl.get_results_in_dataframe() # Returns sorted DataFrame
        - automl.get_clean_results()        # Prints formatted results

        4. Retrieve best model:
        name, model, score = automl.get_best_model()

        5. Make predictions:
        predictions = automl.predict(X_new)

        6. Visualize results:
        automl.plot_performance(figsize=(12, 8))
        automl.plot_model_comparison_radar()

        Advanced Features:
        ------------------
        - Custom Models: Pass your own models via `custom_models` parameter
        Example: custom_models={'MyModel': MyCustomModel()}

        - Custom Hyperparameters: Provide custom search grids via `custom_param_grids`
        Example: custom_param_grids={'RandomForest': {'n_estimators': [50, 100]}}

        - Full Pipeline Training: Train best model on full dataset:
        final_model = automl.train_best_model(X_full, y_full)

        - Model Nomenclature: View all available models:
        print(automl.nomenclature())

        - Package Information: 
        automl.author()  # Shows package details and features

        Example Workflow:
        -----------------
        >>> from automl import AutoML
        >>> automl = AutoML()
        >>> results = automl.fit(
        ...     X_train, y_train,
        ...     X_test, y_test,
        ...     problem_type='classification',
        ...     grid_search=['XGBoost', 'RandomForest'],
        ...     max_workers=8
        ... )
        >>> print(automl.get_results_in_dataframe(sort_by='F1'))
        >>> best_name, best_model, best_score = automl.get_best_model()
        >>> predictions = automl.predict(X_new)
        >>> automl.plot_performance(save_path='results.png')

        Notes:
        ------
        - Install optional dependencies for full functionality:
            pip install xgboost lightgbm catboost

        - Use `ignore_warnings=True` in fit() to suppress warnings

        - For large datasets, consider using a subset of models via 'exclude_models'

        Supported Models:
        -----------------
        Regression (40+):
            LinearRegression, Ridge, Lasso, ElasticNet, XGBoost, LightGBM,
            CatBoost, RandomForest, GradientBoosting, SVR, and more...

        Classification (40+):
            LogisticRegression, RandomForestClassifier, XGBClassifier,
            LightGBMClassifier, CatBoostClassifier, SVC, and more...

        Visualization Options:
        ----------------------
        1. plot_performance()        - Comprehensive metrics comparison
        2. plot_training_time_comparison() - Training time analysis
        3. plot_model_comparison_radar() - Radar chart of top 5 models

        For detailed implementation and customization:
        See method docstrings using help(AutoML.method_name)
        """
        print(self.help_automl.__doc__)
