from .parse_formula import parse_formula
import statsmodels.api as sm
import pandas as pd

def fit(formula: str, data: pd.DataFrame = None, method: str = "ols"):
    """
    Fits a statistical model based on a specified formula and data.

    Parameters:
    - formula (str): A string representing the statistical formula (e.g., 'Y ~ X1 + X2 - X3').
    - data (DataFrame, optional): The dataset containing the variables specified in the formula.
    - method (str, optional): The method used for fitting the model. Defaults to 'ols' (Ordinary Least Squares).
                              Supported methods: 'ols' for linear regression, 'logistic' for logistic regression.

    Returns:
    - model (statsmodels object): The fitted model object, which can be used for further analysis, such as
                                  making predictions or evaluating model performance.

    Raises:
    - ValueError: If the input data is empty or the specified variables are not found in the data.
    - NotImplementedError: If an unsupported method is specified.

    Notes:
    - The function currently supports OLS (Ordinary Least Squares) and logistic regression.
      Additional methods like random forest or k-nearest neighbors could be added as needed.
    """

    def check_response_and_convert(Y_out):
        """Convert categorical response variable to dummies if necessary."""
        if not pd.api.types.is_numeric_dtype(Y_out):
            Y_out = pd.get_dummies(Y_out, drop_first=True)
            if Y_out.shape[1] > 1:
                raise ValueError("Response variable was converted to multiple columns, indicating it is multi-class. "
                                 "This function currently supports binary response variables only.")
        return Y_out
    
    Y_name, X_names, Y_out, X_out = parse_formula(formula, data)
    
    # Ensure Y_out is a Series and retains its name
    if isinstance(Y_out, (pd.Series, pd.DataFrame)):
        Y_out.name = Y_name
    else:
        Y_out = pd.Series(Y_out, name=Y_name)
    
    # Ensure X_out is always a DataFrame
    if isinstance(X_out, pd.Series):
        X_out = X_out.to_frame()
    
    if X_out.empty:
        raise ValueError("The input data is empty or the specified variables are not found in the data.")
    
    # SKIP dummy processing - parse_formula already handled it
    
    if method.lower() == "ols":
        model = sm.OLS(Y_out, X_out).fit()
    elif method.lower() == "logistic":
        Y_out = check_response_and_convert(Y_out)
        model = sm.GLM(Y_out, X_out, family=sm.families.Binomial()).fit()
    else:
        raise NotImplementedError(f"Method '{method}' is not implemented. Supported methods: 'ols', 'logistic'.")
    
    return model
