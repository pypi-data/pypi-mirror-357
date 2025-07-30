#!/usr/bin/env python3
# timeseries_compute/stats_model.py

"""
Time Series Statistical Modeling Module.

This module implements various time series models for analyzing and forecasting
financial and economic data, with a focus on ARIMA for conditional mean modeling
and GARCH for volatility modeling. It supports both univariate and multivariate
approaches.

Key Components:
- ModelARIMA: ARIMA model for conditional mean forecasting
- ModelGARCH: GARCH model for volatility forecasting
- ModelMultivariateGARCH: Multivariate GARCH for correlation/covariance modeling
- ModelFactory: Factory pattern for creating appropriate model instances

Key Functions:
- run_arima: Convenience function for ARIMA modeling
- run_garch: Convenience function for GARCH modeling
- run_multivariate_garch: Function for multivariate GARCH analysis
- calculate_correlation_matrix: Compute correlation matrices
- calculate_portfolio_risk: Assess risk based on volatility and correlations

Supported Models:
- ARIMA(p,d,q): For modeling conditional means
- GARCH(p,q): For modeling conditional volatility
- CCC-GARCH: Constant Conditional Correlation
- DCC-GARCH: Dynamic Conditional Correlation with EWMA

Typical Usage Flow:
1. Start with prepared data from data_processor.py
2. Fit ARIMA models to capture conditional mean
3. Extract residuals and fit GARCH models for volatility
4. For multiple series, analyze correlations with multivariate GARCH
5. Generate forecasts and risk metrics

The models in this module follow standard econometric practices and use
statsmodels and arch packages for the underlying implementations.
"""

import logging as l

# handle data transformation and preparation tasks
import numpy as np
import pandas as pd

# import model specific libraries
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model

# type hinting
from typing import Dict, Any, Tuple, Union, Optional, List
from timeseries_compute import data_processor
from timeseries_compute.data_processor import (
    calculate_ewma_covariance,
    calculate_ewma_volatility,
)


class ModelARIMA:
    """
    Applies the ARIMA (AutoRegressive Integrated Moving Average) model on all columns of a DataFrame.

    Attributes:
        data (pd.DataFrame): The input data on which ARIMA models will be applied.
        order (Tuple[int, int, int]): The (p, d, q) order of the ARIMA model.
        steps (int): The number of steps to forecast.
        models (Dict[str, ARIMA]): A dictionary to store ARIMA models for each column.
        fits (Dict[str, ARIMA]): A dictionary to store fitted ARIMA models for each column.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        order: Tuple[int, int, int] = (1, 1, 1),
        steps: int = 5,
    ) -> None:
        """
        Initializes the ARIMA model with the given data, order, and steps.

        Args:
            data (pd.DataFrame): The input data for the ARIMA model.
            order (Tuple[int, int, int]): The (p, d, q) order of the ARIMA model.
            steps (int): The number of steps to forecast.
        """
        ascii_banner = """
        \n
        \t> ARIMA <\n"""
        l.info(ascii_banner)

        self.data = data
        self.order = order
        self.steps = steps
        self.models: Dict[str, Any] = {}  # Store models for each column
        self.fits: Dict[str, Any] = {}  # Store fits for each column

    def fit(self) -> Dict[str, Any]:
        """
        Fits an ARIMA model to each column in the dataset.

        Returns:
            Dict[str, Any]: A dictionary where the keys are column names and the values are the
                fitted ARIMA models for each column.
        """
        for column in self.data.columns:
            model = ARIMA(self.data[column], order=self.order)
            self.fits[column] = model.fit()
        return self.fits

    def summary(self) -> Dict[str, str]:
        """
        Returns the model summaries for all columns.

        Returns:
            Dict[str, str]: A dictionary containing the model summaries for each column.
        """
        summaries = {}
        for column, fit in self.fits.items():
            summaries[column] = str(fit.summary())
        return summaries

    def forecast(self) -> Dict[str, Union[float, list]]:
        """
        Generates forecasts for each fitted model.

        Returns:
            Dict[str, Union[float, list]]: A dictionary where the keys are the column names and the values
                are the forecasted values. If steps=1, returns a float. If steps>1, returns a list.
        """
        forecasts = {}
        for column, fit in self.fits.items():
            forecast_result = fit.forecast(steps=self.steps)
            
            # Handle single-step vs multi-step forecasts
            if self.steps == 1:
                # For single-step forecast, return a float
                forecasts[column] = float(forecast_result.iloc[0])
            else:
                # For multi-step forecasts, return a list
                forecasts[column] = forecast_result.tolist() if hasattr(forecast_result, "tolist") else forecast_result
        return forecasts


def run_arima(
    df_stationary: pd.DataFrame,
    p: int = 1,
    d: int = 1,
    q: int = 1,
    forecast_steps: int = 5,
) -> Tuple[Dict[str, object], Dict[str, Union[float, List[float]]]]:
    """
    Runs an ARIMA model on stationary time series data.

    This function fits ARIMA(p,d,q) models to each column in the provided DataFrame
    and generates forecasts for the specified number of steps ahead. It performs minimal
    logging to display only core information about the model and forecasts.

    Args:
        df_stationary (pd.DataFrame): The DataFrame with stationary time series data
        p (int): Autoregressive lag order, default=1
        d (int): Degree of differencing, default=1
        q (int): Moving average lag order, default=1
        forecast_steps (int): Number of steps to forecast, default=5

    Returns:
        Tuple[Dict[str, object], Dict[str, Union[float, List[float]]]]:
            - First element: Dictionary of fitted ARIMA models for each column
            - Second element: Dictionary of forecasted values for each column
    """
    l.info(f"\n## Running ARIMA(p={p}, d={d}, q={q})")

    # Ensure data is properly prepared with Date as index
    df_stationary = data_processor.prepare_timeseries_data(df_stationary)

    model_arima = ModelFactory.create_model(
        model_type="ARIMA",
        data=df_stationary,
        order=(p, d, q),
        steps=forecast_steps,
    )
        
    # Better approach: Explicit type checking with proper exception
    if not isinstance(model_arima, ModelARIMA):
        raise TypeError(f"Expected ModelARIMA, got {type(model_arima)}")
    
    arima_fit = model_arima.fit()

    l.info(f"## ARIMA model fitted to columns: {list(arima_fit.keys())}")

    arima_forecast = model_arima.forecast()

    # Debug: Check what we actually got from forecast
    l.info(f"## DEBUG: Raw forecast results from model_arima.forecast():")
    for col, value in arima_forecast.items():
        try:
            if hasattr(value, '__len__') and not isinstance(value, (str, float, int)):
                value_len = len(value)
            else:
                value_len = 'N/A'
        except TypeError:
            value_len = 'N/A'
        l.info(
            f"   DEBUG {col}: type={type(value)}, length={value_len}, value={value}"
        )

    l.info(f"## ARIMA {forecast_steps}-step forecast values:")
    for col, value in arima_forecast.items():
        if isinstance(value, (list, np.ndarray)) and hasattr(value, '__iter__'):
            # Format list of forecast values
            try:
                value_str = ", ".join(f"{v:.4f}" for v in value)
                l.info(f"   {col}: [{value_str}]")
            except (TypeError, ValueError):
                l.info(f"   {col}: {value}")
        else:
            # Format single forecast value
            try:
                l.info(f"   {col}: {value:.4f}")
            except (TypeError, ValueError):
                l.info(f"   {col}: {value}")

    return arima_fit, arima_forecast


class ModelGARCH:
    """
    Represents a GARCH model for time series data.

    Attributes:
        data (pd.DataFrame): The input time series data.
        p (int): The order of the GARCH model for the lag of the squared residuals.
        q (int): The order of the GARCH model for the lag of the conditional variance.
        dist (str): The distribution to use for the GARCH model (e.g., 'normal', 't').
        models (Dict[str, arch_model]): A dictionary to store models for each column of the data.
        fits (Dict[str, arch_model]): A dictionary to store fitted models for each column of the data.
    """

    def __init__(
        self, data: pd.DataFrame, p: int = 1, q: int = 1, dist: str = "normal"
    ) -> None:
        """
        Initializes the GARCH model with the given parameters.

        Args:
            data (pd.DataFrame): The input data for the GARCH model.
            p (int): The order of the GARCH model.
            q (int): The order of the ARCH model.
            dist (str): The distribution to be used in the model (e.g., 'normal', 't').
        """
        ascii_banner = """
        \n\t> GARCH <\n"""
        l.info(ascii_banner)

        self.data = data
        self.p = p
        self.q = q
        # Validate and set distribution
        valid_dists = ['normal', 'gaussian', 't', 'studentst', 'skewstudent', 'skewt', 'ged']
        self.dist = dist if dist in valid_dists else 'normal'
        self.models: Dict[str, Any] = {}  # Store models for each column
        self.fits: Dict[str, Any] = {}  # Store fits for each column

    def fit(self) -> Dict[str, Any]:
        """
        Fits a GARCH model to each column of the data.

        Returns:
            Dict[str, Any]: A dictionary where the keys are column names and the values
                are the fitted GARCH models.
        """
        from typing import cast, Literal
        
        for column in self.data.columns:
            # Cast dist to the correct literal type to satisfy Pylance
            dist_literal = cast(Literal['normal', 'gaussian', 't', 'studentst', 'skewstudent', 'skewt', 'ged', 'generalized error'], self.dist)
            model = arch_model(
                self.data[column], vol="GARCH", p=self.p, q=self.q, dist=dist_literal
            )
            self.fits[column] = model.fit(disp="off")
        return self.fits

    def summary(self) -> Dict[str, str]:
        """
        Returns the model summaries for all columns.

        Returns:
            Dict[str, str]: A dictionary containing the model summaries for each column.
        """
        summaries = {}
        for column, fit in self.fits.items():
            summaries[column] = str(fit.summary())
        return summaries

    def forecast(self, steps: int) -> Dict[str, float]:
        """
        Generates forecasted variance for each fitted model.

        Args:
            steps (int): The number of steps ahead to forecast.

        Returns:
            Dict[str, float]: A dictionary where keys are column names and values are the forecasted variances for the specified horizon.
        """
        forecasts = {}
        for column, fit in self.fits.items():
            forecasts[column] = fit.forecast(horizon=steps).variance.iloc[-1]
        return forecasts


class ModelMultivariateGARCH:
    """Implements multivariate GARCH models including CC-GARCH and DCC-GARCH."""

    def __init__(
        self, data: pd.DataFrame, p: int = 1, q: int = 1, model_type: str = "cc"
    ):
        """
        Initialize multivariate GARCH model.

        Args:
            data: DataFrame with multiple time series
            p: GARCH order
            q: ARCH order
            model_type: 'cc' for Constant Correlation or 'dcc' for Dynamic Conditional Correlation
        """
        # If data has Date column, set it as index for time series operations
        self.data = data
        self.data = data
        self.p = p
        self.q = q
        self.model_type = model_type
        self.fits = {}

    def fit_cc_garch(self) -> Dict[str, Any]:
        """Fit Constant Conditional Correlation GARCH model."""
        # First fit univariate GARCH models
        univariate_models = {}
        for column in self.data.columns:
            model = arch_model(self.data[column], vol="GARCH", p=self.p, q=self.q)
            univariate_models[column] = model.fit(disp="off")

        # Calculate constant correlation matrix
        residuals = pd.DataFrame()
        for column in self.data.columns:
            residuals[column] = univariate_models[column].resid

        correlation_matrix = residuals.corr()

        # Store results
        self.cc_results = {
            "univariate_models": univariate_models,
            "correlation": correlation_matrix,
        }
        return self.cc_results

    def fit_dcc_garch(self, lambda_val: float = 0.95):
        """
        Fit Dynamic Conditional Correlation GARCH model using EWMA for correlation.

        Args:
            lambda_val: EWMA decay factor

        Returns:
            Dictionary with DCC-GARCH results
        """
        # Fit univariate GARCH models
        univariate_models = {}
        conditional_vols = pd.DataFrame(index=self.data.index)

        for column in self.data.columns:
            model = arch_model(self.data[column], vol="GARCH", p=self.p, q=self.q)
            fit = model.fit(disp="off")
            univariate_models[column] = fit
            conditional_vols[column] = np.sqrt(fit.conditional_volatility)

        # Calculate standardized residuals
        std_residuals = pd.DataFrame(index=self.data.index)
        for column in self.data.columns:
            std_residuals[column] = self.data[column] / conditional_vols[column]

        # Calculate EWMA correlation for all pairs
        correlations = {}
        columns = self.data.columns
        for i in range(len(columns)):
            for j in range(i + 1, len(columns)):
                col_pair = f"{columns[i]}_{columns[j]}"
                correlations[col_pair] = calculate_ewma_covariance(
                    std_residuals[columns[i]], std_residuals[columns[j]], lambda_val
                )

        self.dcc_results = {
            "univariate_models": univariate_models,
            "conditional_vols": conditional_vols,
            "correlations": correlations,
        }

        return self.dcc_results


# These functions should be outside the class
def calculate_correlation_matrix(standardized_residuals: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate constant conditional correlation matrix from standardized residuals.

    Args:
        standardized_residuals (pd.DataFrame): DataFrame of standardized residuals from GARCH models

    Returns:
        pd.DataFrame: Correlation matrix
    """
    return standardized_residuals.corr()


def calculate_dynamic_correlation(
    ewma_cov: pd.Series, ewma_vol1: pd.Series, ewma_vol2: pd.Series
) -> pd.Series:
    """
    Calculate dynamic conditional correlation from EWMA covariance and volatilities.

    Args:
        ewma_cov (pd.Series): EWMA covariance between two series
        ewma_vol1 (pd.Series): EWMA volatility of first series
        ewma_vol2 (pd.Series): EWMA volatility of second series

    Returns:
        pd.Series: Dynamic conditional correlation
    """
    return ewma_cov / (ewma_vol1 * ewma_vol2)


def construct_covariance_matrix(volatilities: list, correlation: float) -> np.ndarray:
    """
    Construct a 2x2 covariance matrix using volatilities and correlation.

    Args:
        volatilities (list): List of volatilities [vol1, vol2]
        correlation (float): Correlation coefficient

    Returns:
        np.ndarray: 2x2 covariance matrix
    """
    correlation = float(correlation)  # Ensure correlation is a float
    cov_matrix = np.outer(volatilities, volatilities)
    cov_matrix[0, 1] *= correlation
    cov_matrix[1, 0] *= correlation
    return cov_matrix


def calculate_portfolio_risk(weights: np.ndarray, cov_matrix: np.ndarray) -> tuple:
    """
    Calculate portfolio variance and volatility for given weights and covariance matrix.

    Args:
        weights (np.ndarray): Array of portfolio weights
        cov_matrix (np.ndarray): Covariance matrix

    Returns:
        tuple: (portfolio_variance, portfolio_volatility)
    """
    portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    portfolio_volatility = np.sqrt(portfolio_variance)
    return portfolio_variance, portfolio_volatility


def run_multivariate_garch(
    df_stationary: pd.DataFrame,
    arima_fits: Optional[Dict[str, Any]] = None,
    garch_fits: Optional[Dict[str, Any]] = None,
    lambda_val: float = 0.95,
) -> Dict[str, Any]:
    """
    Runs multivariate GARCH analysis on the provided stationary DataFrame.

    This function implements both Constant Conditional Correlation (CCC) and
    Dynamic Conditional Correlation (DCC) GARCH models. It either uses provided
    ARIMA and GARCH models or fits new ones if not provided.

    Args:
        df_stationary (pd.DataFrame): The stationary time series data for GARCH modeling
        arima_fits (dict, optional): Dictionary of fitted ARIMA models for each column
        garch_fits (dict, optional): Dictionary of fitted GARCH models for each column
        lambda_val (float, optional): EWMA decay factor for DCC model. Defaults to 0.95.

    Returns:
        dict: Dictionary containing multivariate GARCH results
            - 'arima_residuals': DataFrame of ARIMA residuals
            - 'conditional_volatilities': DataFrame of conditional volatilities
            - 'standardized_residuals': DataFrame of standardized residuals
            - 'cc_correlation': Constant conditional correlation matrix
            - 'cc_covariance_matrix': Covariance matrix using CCC
            - 'dcc_correlation': Series of dynamic conditional correlations
            - 'dcc_covariance': Series of dynamic conditional covariances

    Example:
        >>> # Create stationary returns for two assets
        >>> returns = pd.DataFrame({
        ...     'Asset1': [0.01, -0.02, 0.015, -0.01, 0.02],
        ...     'Asset2': [0.015, -0.01, 0.02, -0.015, 0.01]
        ... })
        >>> # Run multivariate GARCH analysis
        >>> results = run_multivariate_garch(returns)
        >>> # Access the correlation matrix
        >>> print(results['cc_correlation'])
        >>> # Plot dynamic correlation over time
        >>> plt.plot(results['dcc_correlation'])
    """
    results = {}

    # 1. If ARIMA fits not provided, fit ARIMA models to filter out conditional mean
    if arima_fits is None:
        arima_fits, _ = run_arima(
            df_stationary=df_stationary, p=1, d=0, q=1, forecast_steps=1
        )

    # 2. Extract ARIMA residuals
    arima_residuals = pd.DataFrame(index=df_stationary.index)
    for column in df_stationary.columns:
        if hasattr(arima_fits[column], "resid"):
            arima_residuals[column] = arima_fits[column].resid
        else:
            # If no residuals available, use original series
            arima_residuals[column] = df_stationary[column]

    results["arima_residuals"] = arima_residuals

    # 3. If GARCH fits not provided, fit GARCH models
    if garch_fits is None:
        garch_fits, _ = run_garch(
            df_stationary=arima_residuals, p=1, q=1, forecast_steps=1
        )

    # 4. Extract conditional volatilities
    cond_vol = {}
    for column in arima_residuals.columns:
        cond_vol[column] = np.sqrt(garch_fits[column].conditional_volatility)

    cond_vol_df = pd.DataFrame(cond_vol, index=arima_residuals.index)
    results["conditional_volatilities"] = cond_vol_df

    # 5. Calculate standardized residuals
    std_resid = {}
    for column in arima_residuals.columns:
        std_resid[column] = arima_residuals[column] / cond_vol[column]

    std_resid_df = pd.DataFrame(std_resid, index=arima_residuals.index)
    results["standardized_residuals"] = std_resid_df

    # 6. Constant Conditional Correlation (CCC-GARCH)
    cc_corr = calculate_correlation_matrix(std_resid_df)
    results["cc_correlation"] = cc_corr

    # 7. Get latest volatilities for covariance matrix
    if len(arima_residuals.columns) == 2:
        columns = list(arima_residuals.columns)
        latest_vols = [cond_vol[col].iloc[-1] for col in columns]

        # Construct covariance matrix using CCC
        try:
            # Simplified approach: just use numpy conversion
            correlation_float = float(np.asarray(cc_corr.iloc[0, 1]))
        except (TypeError, ValueError) as e:
            # Fallback to default correlation if conversion fails
            correlation_float = 0.5
            l.warning(f"Failed to convert correlation value ({e}), using default: {correlation_float}")
        
        cc_cov_matrix = construct_covariance_matrix(
            volatilities=latest_vols, correlation=correlation_float
        )
        results["cc_covariance_matrix"] = cc_cov_matrix

    # 8. Dynamic Conditional Correlation (DCC-GARCH)
    if len(arima_residuals.columns) == 2:
        columns = list(std_resid_df.columns)

        # Calculate EWMA covariance
        ewma_cov = calculate_ewma_covariance(
            std_resid_df[columns[0]], std_resid_df[columns[1]], lambda_val=lambda_val
        )

        # Calculate EWMA volatilities for standardized residuals
        ewma_vol1 = calculate_ewma_volatility(
            std_resid_df[columns[0]], lambda_val=lambda_val
        )

        ewma_vol2 = calculate_ewma_volatility(
            std_resid_df[columns[1]], lambda_val=lambda_val
        )

        # Calculate dynamic correlation
        dcc_corr = calculate_dynamic_correlation(ewma_cov, ewma_vol1, ewma_vol2)
        results["dcc_correlation"] = dcc_corr

        # Calculate dynamic covariance
        dcc_cov = dcc_corr * (cond_vol_df[columns[0]] * cond_vol_df[columns[1]])
        results["dcc_covariance"] = dcc_cov

    return results


class ModelFactory:
    """
    Factory class for creating instances of different statistical models.

    Methods:
        create_model(model_type: str, **kwargs) -> Any:
            Static method that creates and returns an instance of a model based on the provided model_type.
    """

    @staticmethod
    def create_model(
        model_type: str,
        data: pd.DataFrame,
        # ARIMA parameters with defaults
        order: Tuple[int, int, int] = (1, 1, 1),
        steps: int = 5,
        # GARCH parameters with defaults
        p: int = 1,
        q: int = 1,
        dist: str = "normal",
        # Multivariate GARCH parameters
        mv_model_type: str = "cc",
    ) -> Union[ModelARIMA, ModelGARCH, ModelMultivariateGARCH]:
        """
        Creates and returns an instance of a statistical model based on the specified type.

        Args:
            model_type (str): Type of model to create ("ARIMA", "GARCH", or "MVGARCH")
            data (pd.DataFrame): Input data for the model
            order (Tuple[int, int, int]): (p,d,q) order for ARIMA models
            steps (int): Forecast horizon for ARIMA models
            p (int): GARCH order parameter
            q (int): ARCH order parameter
            dist (str): Error distribution for GARCH models
            mv_model_type (str): Type of multivariate GARCH model ("cc" or "dcc")

        Returns:
            Union[ModelARIMA, ModelGARCH, ModelMultivariateGARCH]: The created model instance

        Raises:
            ValueError: If an unsupported model type is provided
        """
        l.info(f"Creating model type: {model_type}")
        if model_type.lower() == "arima":
            return ModelARIMA(data=data, order=order, steps=steps)
        elif model_type.lower() == "garch":
            return ModelGARCH(data=data, p=p, q=q, dist=dist)
        elif model_type.lower() == "mvgarch":
            return ModelMultivariateGARCH(data=data, p=p, q=q, model_type=mv_model_type)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")


def run_garch(
    df_stationary: pd.DataFrame,
    p: int = 1,
    q: int = 1,
    dist: str = "normal",
    forecast_steps: int = 5,
) -> Tuple[Dict[str, Any], Dict[str, float]]:
    """
    Runs the GARCH model on the provided stationary DataFrame.

    This function fits GARCH(p,q) models to each column in the provided DataFrame
    and generates volatility forecasts. It performs minimal logging to display only
    core information about the model and forecasts.

    Args:
        df_stationary (pd.DataFrame): The stationary time series data for GARCH modeling
        p (int): The GARCH lag order, default=1
        q (int): The ARCH lag order, default=1
        dist (str): The error distribution - 'normal', 't', etc., default="normal"
        forecast_steps (int): The number of steps to forecast, default=5

    Returns:
        Tuple[Dict[str, Any], Dict[str, float]]:
            - First element: Dictionary of fitted GARCH models for each column
            - Second element: Dictionary of forecasted volatility values for each column
    """
    l.info(f"\n## Running GARCH(p={p}, q={q}, dist={dist})")
    # Ensure data is properly prepared for time series analysis
    try:
        df_stationary = data_processor.prepare_timeseries_data(df_stationary)
    except Exception as e:
        l.error(f"Error preparing data for GARCH model: {e}")
        raise ValueError(f"Failed to prepare data for GARCH model: {str(e)}")

    # Create and fit the GARCH model
    try:
        model_garch = ModelFactory.create_model(
            model_type="GARCH",
            data=df_stationary,
            p=p,
            q=q,
            dist=dist,
        )
        
        # Type assertion to ensure correct type
        if not isinstance(model_garch, ModelGARCH):
            raise TypeError(f"Expected ModelGARCH, got {type(model_garch)}")
        
        garch_fit = model_garch.fit()

        l.info(f"## GARCH model fitted to columns: {list(garch_fit.keys())}")

        garch_forecast = model_garch.forecast(steps=forecast_steps)
        l.info(f"## GARCH {forecast_steps}-step volatility forecast:")
        for col, value in garch_forecast.items():
            # More robust type checking to handle edge cases
            try:
                # Check if it's specifically a list or array, not just any iterable
                if isinstance(value, (list, tuple, np.ndarray)) and len(value) > 0:
                    # Try to iterate and format
                    value_str = ", ".join(f"{v:.6f}" for v in value)
                    l.info(f"   {col}: [{value_str}]")
                else:
                    # Handle as scalar value
                    if isinstance(value, (int, float)):
                        l.info(f"   {col}: {value:.6f}")
                    else:
                        l.info(f"   {col}: {value}")
            except (TypeError, ValueError, AttributeError):
                # Fallback for any type conversion issues
                l.info(f"   {col}: {value}")

        return garch_fit, garch_forecast

    except Exception as e:
        l.error(f"Error during GARCH model fitting or forecasting: {e}")
        raise RuntimeError(f"GARCH model failed: {str(e)}")


def calculate_stats(series: pd.Series, annualization_factor: int = 250) -> Dict[str, float]:
    """
    Calculate comprehensive descriptive statistics for a time series.

    This function computes a comprehensive set of statistical measures commonly used 
    in financial time series analysis, including central tendency, dispersion, 
    distribution shape, and annualized volatility metrics.

    Args:
        series (pd.Series): Time series data to analyze. Should contain numeric values.
        annualization_factor (int, optional): Factor used to annualize volatility. 
            Common values:
            - 250: For daily financial data (trading days per year)
            - 252: Alternative daily factor accounting for holidays
            - 52: For weekly data
            - 12: For monthly data
            - 4: For quarterly data
            - 1: For annual data or no annualization
            Defaults to 250.

    Returns:
        Dict[str, float]: Dictionary containing comprehensive statistics:
            - 'n': Number of observations in the series
            - 'mean': Arithmetic mean of the series
            - 'median': Median value (50th percentile)
            - 'min': Minimum value in the series
            - 'max': Maximum value in the series
            - 'std': Standard deviation (sample standard deviation)
            - 'var': Variance (sample variance)
            - 'skew': Skewness - measure of asymmetry (0 = symmetric)
            - 'kurt': Excess kurtosis - measure of tail heaviness (0 = normal)
            - 'annualized_vol': Annualized volatility (std * sqrt(annualization_factor))
            - 'annualized_return': Annualized return (mean * annualization_factor)
            - 'sharpe_approx': Approximate Sharpe ratio (annualized_return / annualized_vol)

    Raises:
        ValueError: If the series is empty or contains no numeric data
        TypeError: If the series contains non-numeric data that cannot be converted

    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Daily stock returns
        >>> returns = pd.Series(np.random.normal(0.001, 0.02, 252))
        >>> stats = calculate_stats(returns, annualization_factor=252)
        >>> print(f"Annualized Return: {stats['annualized_return']:.2%}")
        >>> print(f"Annualized Volatility: {stats['annualized_vol']:.2%}")
        >>> print(f"Sharpe Ratio: {stats['sharpe_approx']:.2f}")
        >>>
        >>> # Monthly data
        >>> monthly_data = pd.Series([0.02, -0.01, 0.03, 0.01, -0.02])
        >>> monthly_stats = calculate_stats(monthly_data, annualization_factor=12)

    Note:
        - Skewness interpretation: >0 (right tail), <0 (left tail), =0 (symmetric)
        - Kurtosis interpretation: >0 (heavy tails), <0 (light tails), =0 (normal)
        - Sharpe ratio calculation assumes zero risk-free rate for simplicity
        - For non-return data, annualized metrics may not be meaningful
    """
    if series.empty:
        raise ValueError("Cannot calculate statistics for empty series")
    
    # Remove any NaN values for calculation
    clean_series = series.dropna()
    
    if clean_series.empty:
        raise ValueError("Series contains no valid numeric data after removing NaN values")
    
    # Basic statistics
    n = len(clean_series)
    mean_val = clean_series.mean()
    std_val = clean_series.std()
    
    # Calculate annualized metrics
    annualized_vol = std_val * np.sqrt(annualization_factor)
    annualized_return = mean_val * annualization_factor
    
    # Approximate Sharpe ratio (assuming zero risk-free rate)
    sharpe_approx = annualized_return / annualized_vol if annualized_vol != 0 else 0.0
    
    # Calculate statistics with robust scalar conversion
    try:
        var_val = float(np.asarray(clean_series.var()))
        skew_val = float(np.asarray(clean_series.skew()))
        kurt_val = float(np.asarray(clean_series.kurtosis()))
    except (TypeError, ValueError):
        # Fallback values if conversion fails
        var_val = float(std_val ** 2) if std_val is not None else 0.0
        skew_val = 0.0
        kurt_val = 0.0
    
    return {
        "n": float(n),
        "mean": float(mean_val),
        "median": float(clean_series.median()),
        "min": float(clean_series.min()),
        "max": float(clean_series.max()),
        "std": float(std_val),
        "var": var_val,
        "skew": skew_val,
        "kurt": kurt_val,
        "annualized_vol": float(annualized_vol),
        "annualized_return": float(annualized_return),
        "sharpe_approx": float(sharpe_approx),
    }


# Moved ARIMA and GARCH-related functions from spillover_processor.py
# These functions support the spillover analysis workflows

def fit_arima_model(
    returns_series: pd.Series,
    order: Tuple[int, int, int] = (1, 0, 0)
) -> Any:
    """
    Fit ARIMA model to a single returns series.

    Args:
        returns_series: Time series of returns for a single asset
        order: ARIMA order (p, d, q)

    Returns:
        Fitted ARIMA model
    """
    from statsmodels.tsa.arima.model import ARIMA

    l.info(f"Fitting ARIMA model with order={order}")

    # Fit ARIMA model
    model = ARIMA(returns_series, order=order)
    fitted_model = model.fit()

    l.info("ARIMA model fitted successfully")

    return fitted_model


def fit_garch_model(
    returns_series: pd.Series,
    p: int = 1,
    q: int = 1
) -> Any:
    """
    Fit GARCH model to a single returns series.

    Args:
        returns_series: Time series of returns for a single asset
        p: Order of the GARCH terms
        q: Order of the ARCH terms

    Returns:
        Fitted GARCH model
    """
    from arch import arch_model

    l.info(f"Fitting GARCH model with p={p}, q={q}")

    # Fit GARCH model
    model = arch_model(returns_series, vol='GARCH', p=p, q=q)
    fitted_model = model.fit(disp='off')

    l.info("GARCH model fitted successfully")

    return fitted_model


def fit_dcc_garch_model(
    returns_df: pd.DataFrame,
    garch_order: Tuple[int, int] = (1, 1)
) -> Any:
    """
    Fit a DCC-GARCH model to multivariate returns data.

    Args:
        returns_df: DataFrame of returns for multiple assets
        garch_order: GARCH order (p, q)

    Returns:
        Dictionary containing standardized residuals and correlation matrix
    """
    from arch.univariate import arch_model

    l.info("Fitting DCC-GARCH model")

    # Fit univariate GARCH models for each series
    univariate_models = {}
    standardized_residuals = {}

    for column in returns_df.columns:
        model = arch_model(returns_df[column], vol='GARCH', p=garch_order[0], q=garch_order[1])
        fitted_model = model.fit(disp='off')
        univariate_models[column] = fitted_model
        standardized_residuals[column] = fitted_model.std_resid

    # Create a DataFrame of standardized residuals
    standardized_residuals_df = pd.DataFrame(standardized_residuals)

    # Calculate the correlation matrix of standardized residuals
    correlation_matrix = calculate_correlation_matrix(standardized_residuals_df)

    l.info("DCC-GARCH model fitted successfully")

    return {
        'standardized_residuals': standardized_residuals_df,
        'correlation_matrix': correlation_matrix
    }
