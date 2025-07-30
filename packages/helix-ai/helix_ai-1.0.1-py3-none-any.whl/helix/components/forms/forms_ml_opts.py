"""Machine Learning model options forms for Helix.

This module contains form functions for both selecting and configuring different
machine learning models through Streamlit UI elements. Each function handles the
parameter configuration for a specific model type, supporting both manual parameter
setting and hyperparameter search options.

Functions:
    - ml_options_form: The main form for setting up the machine learning pipeline.
    - _linear_model_opts: Configuration for linear regression/classification
    - _random_forest_opts: Configuration for random forest models
    - _xgboost_opts: Configuration for XGBoost models
    - _svm_opts: Configuration for Support Vector Machines
    - _mlrem_opts: Configuration for Multiple Linear Regression with EM
    - _brnn_opts: Configuration for Bayesian Regularised Neural Networks
"""

import streamlit as st

from helix.components.configuration import data_split_options_box
from helix.options.choices.ui import SVM_KERNELS
from helix.options.enums import (
    ActivationFunctions,
    ExecutionStateKeys,
    MachineLearningStateKeys,
    ModelNames,
    PlotOptionKeys,
    ProblemTypes,
)
from helix.options.search_grids import (
    BRNN_GRID,
    LINEAR_MODEL_GRID,
    MLREM_GRID,
    RANDOM_FOREST_GRID,
    SVM_GRID,
    XGB_GRID,
)


###########################################################################
# Below are the options for which models will be used
###########################################################################
@st.experimental_fragment
def ml_options_form(problem_type: ProblemTypes = ProblemTypes.Regression):
    """
    The form for setting up the machine learning pipeline.
    """

    use_hyperparam_search = st.toggle(
        "Use hyper-parameter search",
        value=True,
        key=ExecutionStateKeys.UseHyperParamSearch,
    )
    if use_hyperparam_search:
        st.success(
            """
            **✨ Hyper-parameters will be searched automatically**.

            Helix will determine the best hyper-parameters
            and return the model with the best performance.
            """
        )
    else:
        st.info(
            """
            **🛠️ Manually set the hyper-parameters you wish to use for your models.**
            """
        )

    data_split_opts = data_split_options_box(not use_hyperparam_search)
    st.session_state[ExecutionStateKeys.DataSplit] = data_split_opts

    st.subheader("Select and configure which models to train")
    model_types = {}
    if problem_type == ProblemTypes.Regression:
        string_toggle = "Linear Regression"
        # Only show MLREM for regression problems
        if st.toggle(
            "Multiple Linear Regression with Expectation Maximisation",
            value=False,
            help="MLREM is only available for regression problems. Note that if you run hyperparamenter optimisation, the processing time will take longer",
        ):
            mlrem_model_type = _mlrem_opts(use_hyperparam_search)
            model_types.update(mlrem_model_type)
    else:
        string_toggle = "Logistic Regression"

    if st.toggle(string_toggle, value=False):
        lm_model_type = _linear_model_opts(use_hyperparam_search)
        model_types.update(lm_model_type)

    if st.toggle("Random Forest", value=False):
        rf_model_type = _random_forest_opts(use_hyperparam_search)
        model_types.update(rf_model_type)

    if st.toggle("XGBoost", value=False):
        xgb_model_type = _xgboost_opts(use_hyperparam_search)
        model_types.update(xgb_model_type)

    if st.toggle("Support Vector Machine", value=False):
        svm_model_type = _svm_opts(use_hyperparam_search)
        model_types.update(svm_model_type)

    # if st.toggle("Bayesian Regularised Neural Network", value=False):
    #     brnn_model_type = _brnn_opts(use_hyperparam_search)
    #     model_types.update(brnn_model_type)

    st.session_state[MachineLearningStateKeys.ModelTypes] = model_types
    st.subheader("Select outputs to save")
    st.toggle(
        "Save models",
        key=MachineLearningStateKeys.SaveModels,
        value=True,
        help="Save the models that are trained to disk?",
    )
    st.toggle(
        "Save plots",
        key=PlotOptionKeys.SavePlots,
        value=True,
        help="Save the plots to disk?",
    )


###########################################################################
# Below are the individual model options functions
###########################################################################
def _linear_model_opts(use_hyperparam_search: bool) -> dict:
    model_types = {}
    if not use_hyperparam_search:
        st.write("Options:")
        fit_intercept = st.checkbox("Fit intercept")
        params = {
            "fit_intercept": fit_intercept,
        }
        st.divider()
    else:
        params = LINEAR_MODEL_GRID
    model_types[ModelNames.LinearModel.value] = {
        "use": True,
        "params": params,
    }
    return model_types


def _random_forest_opts(use_hyperparam_search: bool) -> dict:
    model_types = {}
    if not use_hyperparam_search:
        st.write("Options:")
        n_estimators_rf = st.number_input(
            "Number of estimators", value=100, key="n_estimators_rf"
        )
        min_samples_split = st.number_input("Minimum samples split", value=2)
        min_samples_leaf = st.number_input("Minimum samples leaf", value=1)
        col1, col2 = st.columns([0.25, 0.75], vertical_alignment="bottom", gap="small")
        use_rf_max_depth = col1.checkbox(
            "Set max depth",
            value=False,
            help="If disabled or 0, then nodes are expanded until all leaves are pure"
            " or until all leaves contain less than 'Minimum samples split'.",
        )
        max_depth_rf = col2.number_input(
            "Maximum depth",
            value="min",
            min_value=0,
            key="max_depth_rf",
            disabled=not use_rf_max_depth,
        )
        params = {
            "n_estimators": n_estimators_rf,
            "min_samples_split": min_samples_split,
            "min_samples_leaf": min_samples_leaf,
            "max_depth": max_depth_rf if max_depth_rf > 0 else None,
        }
        st.divider()
    else:
        params = RANDOM_FOREST_GRID
    model_types[ModelNames.RandomForest.value] = {
        "use": True,
        "params": params,
    }
    return model_types


def _xgboost_opts(use_hyperparam_search: bool) -> dict:
    model_types = {}
    if not use_hyperparam_search:
        if st.checkbox("Set XGBoost options"):
            st.write("Options:")
            n_estimators_xgb = st.number_input(
                "Number of estimators", value=100, key="n_estimators_xgb"
            )
            learning_rate = st.number_input("Learning rate", value=0.01)
            subsample = st.number_input("Subsample size", value=0.5)
            col1, col2 = st.columns(
                [0.25, 0.75], vertical_alignment="bottom", gap="small"
            )
            use_xgb_max_depth = col1.checkbox(
                "Set max depth",
                value=False,
                help="If disabled or 0, then nodes are expanded until all leaves are pure.",
            )
            max_depth_xbg = col2.number_input(
                "Maximum depth",
                value="min",
                min_value=0,
                key="max_depth_xgb",
                disabled=not use_xgb_max_depth,
            )
        else:
            n_estimators_xgb = None
            max_depth_xbg = None
            learning_rate = None
            subsample = None
        params = {
            "kwargs": {
                "n_estimators": n_estimators_xgb,
                "max_depth": max_depth_xbg,
                "learning_rate": learning_rate,
                "subsample": subsample,
            }
        }
        st.divider()
    else:
        params = XGB_GRID

    model_types[ModelNames.XGBoost.value] = {
        "use": True,
        "params": params,
    }
    return model_types


def _svm_opts(use_hyperparam_search: bool) -> dict:
    model_types = {}
    if not use_hyperparam_search:
        st.write("Options:")
        kernel = st.selectbox("Kernel", options=SVM_KERNELS)
        degree = st.number_input("Degree", min_value=0, value=3)
        c = st.number_input("C", value=1.0, min_value=0.0)
        params = {
            "kernel": kernel.lower(),
            "degree": degree,
            "C": c,
        }
        st.divider()
    else:
        params = SVM_GRID

    model_types[ModelNames.SVM.value] = {
        "use": True,
        "params": params,
    }
    return model_types


def _mlrem_opts(use_hyperparam_search: bool) -> dict:
    model_types = {}
    if not use_hyperparam_search:
        st.write("Options")
        # Basic parameters
        alpha = st.number_input(
            "Alpha (regularisation)", value=0.05, min_value=0.05, step=1.0
        )
        max_beta = st.number_input(
            "Maximum Beta",
            value=40,
            help="Will test beta values from 0.1 to max_beta",
        )
        weight_threshold = st.number_input(
            "Weight Threshold",
            value=1e-3,
            min_value=1e-3,
            step=1e-4,
            format="%.4f",
            help="Features with weights below this will be removed",
        )

        # Advanced options
        st.write("Advanced Options:")
        max_iterations = st.number_input(
            "Max Iterations", value=300, min_value=1, step=50
        )
        tolerance = st.number_input("Tolerance", value=0.01, format="%.4f", step=0.001)

        params = {
            "alpha": alpha,
            "max_beta": max_beta,
            "weight_threshold": weight_threshold,
            "max_iterations": max_iterations,
            "tolerance": tolerance,
        }
        st.divider()
    else:
        params = MLREM_GRID

    model_types[ModelNames.MLREM.value] = {
        "use": True,
        "params": params,
    }
    return model_types


def _brnn_opts(use_hyperparam_search: bool) -> dict:
    model_types = {}
    if not use_hyperparam_search:
        st.write("Options")
        # Basic parameters
        num_hidden_layers = st.number_input(
            "Number of Hidden Layers", value=2, min_value=1, step=1
        )
        hidden_layer_sizes = st.number_input(
            "Hidden Units", value=25, min_value=1, step=5
        )
        activation = st.selectbox(
            "Activation Function",
            options=[af.value for af in ActivationFunctions],
            index=0,
        )
        batch_size = st.number_input(
            "Batch Size", value=32, min_value=1, step=1, help="Batch size for training"
        )
        learning_rate = st.number_input(
            "Learning Rate", value=0.01, format="%.4f", step=1e-3
        )
        max_iter = st.number_input("Max Iterations", value=200, min_value=1, step=50)
        random_state = st.number_input("Random State", value=42, min_value=0, step=1)

        params = {
            "hidden_layer_sizes": [
                hidden_layer_sizes for _ in range(num_hidden_layers - 2)
            ],
            "activation": activation,
            "batch_size": batch_size,
            "learning_rate_init": learning_rate,
            "max_iter": max_iter,
            "random_state": random_state,
        }
        st.divider()
    else:
        params = BRNN_GRID

    model_types[ModelNames.BRNN.value] = {
        "use": True,
        "params": params,
    }
    return model_types
