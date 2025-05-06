from io import StringIO
from pydantic import BaseModel, ConfigDict
import pandas as pd
from agents import Agent, RunContextWrapper, Runner, function_tool
import sqlite3
from typing import List
import json

class InputData(BaseModel):
    df: pd.DataFrame = None
    trained_models: dict = {}  # Store all models by name
    trained_model: object = None  # Store the best model
    model_results: list = []  # Optional: store all results
    
    class Config:
        arbitrary_types_allowed = True

@function_tool  
def get_input_data(wrapper: RunContextWrapper[InputData], query: str) -> str:
    """
    Executes an SQL query and returns the results as a pandas DataFrame encoded as a JSON string.

    Requirements:
    - The query must return a full table or result set with **both input features and a target variable**.
    - All columns must have the same number of rows.

    Returns:
        An extract (up to 5 rows) of the input dataframe retrieved
    """
    cursor = sqlite3.connect("mock_fin_app_v2.sqlite").cursor()
    try:
        import pandas as pd
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=column_names)
        wrapper.context.df = df
        return df.head(5).to_json(orient='records') # JSON string of first 5 rows of a pandas dataframe
    except Exception as e:
        return json.dumps({"error": str(e)})

@function_tool
def choose_model(wrapper: RunContextWrapper[InputData], target_column: str) -> List[str]:
    """
    Infers the type of prediction task (classification vs regression) from the target column,
    and suggests 3-4 baseline models accordingly.

    Arguments:
        target_column: The name of the column to predict.

    Returns:
        A list of model names (e.g. "linear_regression", "random_forest", etc.)
    """
    import pandas as pd
    from sklearn.utils.multiclass import type_of_target

    try:
        df = wrapper.context.df
    except ValueError:
        print("Cannot fetch df from context")
        
    y = df[target_column]
    target_type = type_of_target(y)

    if target_type in ["binary", "multiclass"]:
        return ["logistic_regression", "random_forest", "xgboost", "mlp"]
    elif target_type in ["continuous"]:
        return ["linear_regression", "random_forest", "xgboost", "mlp"]
    else:
        return ["random_forest"]

@function_tool
def run_model(wrapper: RunContextWrapper[InputData], target_column: str, model_type: str) -> str:
    """
    Trains and evaluates a model of the specified type on the input data.

    Arguments:
        target_column: Name of the target variable to predict.
        model_type: One of: linear_regression, logistic_regression, random_forest, decision_tree,
                    gradient_boosting, xgboost, mlp, svm

    Requirements:
        - The input data must include the target column.
        - All columns must be equal in length.

    Returns:
        A JSON string with: {model, score, type}, where type = regression or classification.
    """
    import pandas as pd
    import numpy as np
    import json
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import accuracy_score, r2_score
    from sklearn.utils.multiclass import type_of_target

    # Load input data
    try:
        df = wrapper.context.df
    except ValueError:
        print("Error reading input dataframe from context")
        
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in input data.")
    X = df.drop(columns=[target_column])
    y = df[target_column]

    # Detect target type
    target_type = type_of_target(y)

    # Encode categorical features
    for col in X.select_dtypes(include="object").columns:
        X[col] = LabelEncoder().fit_transform(X[col].astype(str))
    if y.dtype == "object":
        y = LabelEncoder().fit_transform(y.astype(str))

    # Train/test split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # Select appropriate model
    model = None
    if model_type == "linear_regression":
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
    elif model_type == "logistic_regression":
        from sklearn.linear_model import LogisticRegression
        if target_type != "binary":
            raise ValueError("Logistic regression requires a binary classification target.")
        model = LogisticRegression()
    elif model_type == "random_forest":
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        model = RandomForestClassifier() if target_type in ["binary", "multiclass"] else RandomForestRegressor()
    elif model_type == "decision_tree":
        from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
        model = DecisionTreeClassifier() if target_type in ["binary", "multiclass"] else DecisionTreeRegressor()
    elif model_type == "gradient_boosting":
        from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
        model = GradientBoostingClassifier() if target_type in ["binary", "multiclass"] else GradientBoostingRegressor()
    elif model_type == "xgboost":
        from xgboost import XGBClassifier, XGBRegressor
        model = XGBClassifier() if target_type in ["binary", "multiclass"] else XGBRegressor()
    elif model_type == "mlp":
        from sklearn.neural_network import MLPClassifier, MLPRegressor
        model = MLPClassifier() if target_type in ["binary", "multiclass"] else MLPRegressor()
    elif model_type == "svm":
        from sklearn.svm import SVC, SVR
        model = SVC() if target_type in ["binary", "multiclass"] else SVR()
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    # Train model
    model.fit(X_train, y_train)
    y_pred = model.predict(X_val)

    y_pred, y_val = list(y_pred), list(y_val)
    
    # Score model
    score = accuracy_score(y_val, y_pred) if target_type in ["binary", "multiclass"] else r2_score(y_val, y_pred)

    # Return results
    results = {
        "model": model_type,
        "score": score,
        "type": "classification" if target_type in ["binary", "multiclass"] else "regression"
    }
    
    if wrapper.context.trained_models is None:
        wrapper.context.trained_models = {}
    wrapper.context.trained_models[model_type] = model

    
    if wrapper.context.model_results is None:
        wrapper.context.model_results = []
    wrapper.context.model_results.append(results)

    return json.dumps(results)


@function_tool
def model_card_report(results_json: str) -> str:
    """
    Takes a JSON string of model results and returns a report.
    Each item in the list should be a dict with keys: model, score, type.
    """
    import json
    results = json.loads(results_json)
    report = "## Model Report\n\n"
    for res in results:
        report += f"**Model**: {res['model']}\n"
        report += f"**Type**: {res['type']}\n"
        report += f"**Validation Score**: {res['score']:.4f}\n\n"
    best = max(results, key=lambda r: r["score"])
    report += f"### Recommended Model: {best['model']} (Score: {best['score']:.4f})\n"
    return report

@function_tool
def select_best_model(wrapper: RunContextWrapper[InputData]) -> str:
    """
    Selects the best model from previously trained models based on score and sets it as the active model.
    """
    if not wrapper.context.model_results:
        return "No model results available."

    best = max(wrapper.context.model_results, key=lambda r: r["score"])
    best_model_type = best["model"]
    best_model = wrapper.context.trained_models.get(best_model_type)

    if best_model:
        wrapper.context.trained_model = best_model
        return f"Best model selected: {best_model_type} with score {best['score']:.4f}"
    else:
        return f"Could not find model instance for '{best_model_type}' in context."

@function_tool
def feature_importance(wrapper: RunContextWrapper[InputData], model_type: str, target_column: str) -> str:
    """
    Returns feature importances from the best trained model if available.

    Arguments:
        model_type: One of: linear_regression, logistic_regression, random_forest, decision_tree,
                    gradient_boosting, xgboost, mlp, svm
        target_column: The name of the column to predict.

    Returns:
        A string with the ranked features and their importance scores.
    """
    import numpy as np

    # Access model and data from context
    model = wrapper.context.trained_model
    df = wrapper.context.df

    if model is None:
        return "❌ No trained model found in context. Please run a model first."

    if df is None or target_column not in df.columns:
        return f"❌ Input data is missing or target column '{target_column}' not found."

    # Prepare feature matrix
    X = df.drop(columns=[target_column])

    # Try to extract importances
    try:
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            coef = model.coef_
            if hasattr(coef, "ndim"):
                importances = coef if coef.ndim == 1 else coef[0]
            else:
                importances = coef
        else:
            return f"⚠️ The model type '{model_type}' does not support feature importances."
    except Exception as e:
        return f"❌ Error extracting feature importances: {e}"

    # Format output
    try:
        importances = np.asarray(importances)
        ranked = sorted(zip(X.columns, importances), key=lambda x: -abs(x[1]))
        return "\n".join([f"{f}: {round(imp, 4)}" for f, imp in ranked])
    except Exception as e:
        return f"❌ Failed to format importances: {e}"