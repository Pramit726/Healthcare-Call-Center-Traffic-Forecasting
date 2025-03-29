import base64
import io
from pathlib import Path
from typing import Any, List, Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import statsmodels.tsa.stattools as sts
from matplotlib.gridspec import GridSpec
from scipy.stats import (
    chi2_contingency,
    f_oneway,
    jarque_bera,
    levene,
    mannwhitneyu,
    ttest_ind,
)

from ml.constants.constants import DATA_DIR


def get_data(name: str, data_type_dir: str) -> pd.DataFrame:
    """Reads a CSV file from the specified data directory.

    :param name: Name of the file (without extension).
    :type name: str
    :param data_type_dir: Subdirectory type (e.g., 'raw', 'processed').
    :type data_type_dir: str
    :return: The loaded data as a pandas DataFrame.
    :rtype: pd.DataFrame
    :raises FileNotFoundError: If the file is not found.
    """
    file_name = f"{name}.csv"
    current_path = Path(__file__)
    root_path = current_path.parent.parent.parent
    file_path = Path(root_path) / DATA_DIR / data_type_dir / file_name
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {file_path}") from e


def outlier_overview(
    dataframe: pd.DataFrame, column_name: str, cat_col: Optional[str] = None
) -> pd.DataFrame:
    """Provides an overview of a numerical column with box plot and statistics.

    :param dataframe: The DataFrame containing the data.
    :type dataframe: pd.DataFrame
    :param column_name: The name of the numerical column.
    :type column_name: str
    :param cat_col: The name of the categorical column for grouping (optional).
    :type cat_col: Optional[str]
    :return: Descriptive statistics of the numerical column.
    :rtype: pd.DataFrame
    """
    stats = (
        dataframe.groupby(cat_col)[column_name].describe()
        if cat_col
        else dataframe[column_name].describe()
    )

    plt.figure(figsize=(10, 5))
    sns.boxplot(data=dataframe, x=cat_col, y=column_name, ax=plt.gca())
    plt.title(f"Box Plot of '{column_name}'" + (f" by '{cat_col}'" if cat_col else ""))
    plt.tight_layout()
    plt.show()

    return stats


def export_data(dataframe: pd.DataFrame, dir_name: str, name: str) -> None:
    """Exports a DataFrame to a CSV file.

    :param dataframe: The DataFrame to be exported.
    :type dataframe: pd.DataFrame
    :param dir_name: Subdirectory type (e.g., 'raw', 'processed').
    :type dir_name: str
    :param name: Name of the file (without extension).
    :type name: str
    :raises RuntimeError: If data export fails.
    """
    current_path = Path(__file__)
    root_path = current_path.parent.parent.parent
    export_dir = root_path / DATA_DIR / dir_name
    export_dir.mkdir(parents=True, exist_ok=True)
    file_path = export_dir / f"{name}.csv"

    try:
        dataframe.to_csv(file_path, index=False)
        print(f"Data exported to: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to export data to {file_path}") from e


def remove_outliers(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Removes outliers based on price, screen size, and battery capacity.

    :param dataframe: The input DataFrame.
    :type dataframe: pd.DataFrame
    :return: The DataFrame with outliers removed.
    :rtype: pd.DataFrame
    """
    return dataframe.assign(
        extended_upto=lambda x: x["extended_upto"]
        .fillna(0)
        .where(x["extended_memory_available"] == 0, x["extended_upto"])
    ).loc[
        lambda x: (x["price"] <= 200000)
        & (x["screen_size"] < 7)
        & (x["battery_capacity"] <= 7000)
    ]


def numerical_analysis(
    dataframe: pd.DataFrame,
    column_name: str,
    cat_col: Optional[str] = None,
    bins: str = "auto",
) -> None:
    """Performs numerical analysis with KDE, boxplot, and histogram.

    :param dataframe: Input DataFrame.
    :type dataframe: pd.DataFrame
    :param column_name: Column name for numerical analysis.
    :type column_name: str
    :param cat_col: Categorical column for grouping (hue).
    :type cat_col: Optional[str]
    :param bins: Number of bins or binning strategy for histogram.
    :type bins: str
    """
    fig = plt.figure(figsize=(15, 10))
    grid = GridSpec(nrows=2, ncols=2, figure=fig)
    ax1 = fig.add_subplot(grid[0, 0])
    ax2 = fig.add_subplot(grid[0, 1])
    ax3 = fig.add_subplot(grid[1, :])
    sns.kdeplot(data=dataframe, x=column_name, hue=cat_col, ax=ax1)
    sns.boxplot(data=dataframe, x=column_name, hue=cat_col, ax=ax2)
    sns.histplot(
        data=dataframe, x=column_name, bins=bins, hue=cat_col, kde=True, ax=ax3
    )
    plt.tight_layout()
    plt.show()


def numerical_categorical_analysis(
    dataframe: pd.DataFrame, cat_column_1: str, num_column: str
) -> None:
    """Performs numerical-categorical analysis.

    :param dataframe: Input DataFrame.
    :type dataframe: pd.DataFrame
    :param cat_column_1: Categorical column.
    :type cat_column_1: str
    :param num_column: Numerical column.
    :type num_column: str
    """
    fig, (ax1, ax2) = plt.subplots(2, 2, figsize=(15, 7.5))
    sns.barplot(data=dataframe, x=cat_column_1, y=num_column, ax=ax1[0])
    sns.boxplot(data=dataframe, x=cat_column_1, y=num_column, ax=ax1[1])
    sns.violinplot(data=dataframe, x=cat_column_1, y=num_column, ax=ax2[0])
    sns.stripplot(data=dataframe, x=cat_column_1, y=num_column, ax=ax2[1])
    plt.tight_layout()
    plt.show()


def categorical_analysis(dataframe: pd.DataFrame, column_name: str) -> None:
    """Performs categorical analysis with value counts and countplot.

    :param dataframe: Input DataFrame.
    :type dataframe: pd.DataFrame
    :param column_name: Column name for analysis.
    :type column_name: str
    """
    display(  # type: ignore
        pd.DataFrame(
            {
                "Count": dataframe[column_name].value_counts(),
                "Percentage": dataframe[column_name]
                .value_counts(normalize=True)
                .mul(100)
                .round(2)
                .astype("str")
                .add("%"),
            }
        )
    )
    print("*" * 50)
    unique_categories = dataframe[column_name].unique().tolist()
    number_of_categories = dataframe[column_name].nunique()
    print(f"Unique categories in {column_name}: {unique_categories}")
    print("*" * 50)
    print(f"Number of categories in {column_name}: {number_of_categories}")
    sns.countplot(data=dataframe, x=column_name)
    plt.xticks(rotation=45)
    plt.show()


def multivariate_analysis(
    dataframe: pd.DataFrame, num_column: str, cat_column_1: str, cat_column_2: str
) -> None:
    """Performs multivariate analysis with barplot, boxplot, violin plot, and stripplot.

    :param dataframe: Input DataFrame.
    :type dataframe: pd.DataFrame
    :param num_column: Numerical column.
    :type num_column: str
    :param cat_column_1: Primary categorical column.
    :type cat_column_1: str
    :param cat_column_2: Secondary categorical column (for hue).
    :type cat_column_2: str
    """
    fig, axes = plt.subplots(2, 2, figsize=(18, 10))

    sns.barplot(
        data=dataframe, x=cat_column_1, y=num_column, hue=cat_column_2, ax=axes[0, 0]
    )
    sns.boxplot(
        data=dataframe, x=cat_column_1, y=num_column, hue=cat_column_2, ax=axes[0, 1]
    )
    sns.violinplot(
        data=dataframe, x=cat_column_1, y=num_column, hue=cat_column_2, ax=axes[1, 0]
    )
    sns.stripplot(
        data=dataframe,
        x=cat_column_1,
        y=num_column,
        hue=cat_column_2,
        dodge=True,
        ax=axes[1, 1],
    )  # dodge for overlapping points

    plt.tight_layout()
    plt.show()


def chi_2_test(
    dataframe: pd.DataFrame, col1: str, col2: str, alpha: float = 0.05
) -> None:
    """Performs Chi-squared test for independence.

    :param dataframe: Input DataFrame.
    :type dataframe: pd.DataFrame
    :param col1: First categorical column.
    :type col1: str
    :param col2: Second categorical column.
    :type col2: str
    :param alpha: Significance level.
    :type alpha: float
    """
    data = dataframe.loc[:, [col1, col2]].dropna()
    contingency_table = pd.crosstab(data[col1], data[col2])
    _, p_val, _, _ = chi2_contingency(contingency_table)
    print(f"Chi-squared p-value: {p_val}")  # More informative output
    if p_val <= alpha:
        print(
            f"Reject the null hypothesis. Significant association between {col1} and {col2}."
        )
    else:
        print(
            f"Fail to reject the null hypothesis. No significant association between {col1} and {col2}."
        )


def anova_test(
    dataframe: pd.DataFrame, num_col: str, cat_col: str, alpha: float = 0.05
) -> None:
    """Performs ANOVA test.

    :param dataframe: Input DataFrame.
    :type dataframe: pd.DataFrame
    :param num_col: Numerical column.
    :type num_col: str
    :param cat_col: Categorical column.
    :type cat_col: str
    :param alpha: Significance level.
    :type alpha: float
    """
    data = dataframe.loc[:, [num_col, cat_col]].dropna()

    if data[cat_col].dtype == "bool":
        data[cat_col] = data[cat_col].astype("category")

    cat_group = data.groupby(cat_col, observed=False)
    groups = [group[num_col].values for _, group in cat_group]

    _, p_val = f_oneway(*groups)

    print(f"ANOVA p-value: {p_val}")
    if p_val <= alpha:
        print(
            f"Reject the null hypothesis. Significant relationship between {num_col} and {cat_col}."
        )
    else:
        print(
            f"Fail to reject the null hypothesis. No significant relationship between {num_col} and {cat_col}."
        )


def test_for_normality(
    dataframe: pd.DataFrame, column_name: str, alpha: float = 0.05
) -> None:
    """Tests for normality using Jarque-Bera test.

    :param dataframe: Input DataFrame.
    :type dataframe: pd.DataFrame
    :param column_name: Column to test.
    :type column_name: str
    :param alpha: Significance level.
    :type alpha: float
    """
    data = dataframe[column_name].dropna()  # Handle missing values before the test
    print("Jarque Bera Test for Normality")
    _, p_val = jarque_bera(data)
    print(f"Jarque-Bera p-value: {p_val}")  # More informative output
    if p_val <= alpha:
        print("Reject the null hypothesis. Data is not normally distributed.")
    else:
        print("Fail to reject the null hypothesis. Data is normally distributed.")


def two_sample_independent_ttest(
    dataframe: pd.DataFrame, num_col: str, cat_col: str, alpha: float = 0.05
) -> None:
    """Performs a two-sample independent t-test.

    :param dataframe: Input DataFrame.
    :type dataframe: pd.DataFrame
    :param num_col: Numerical column.
    :type num_col: str
    :param cat_col: Categorical column (two categories).
    :type cat_col: str
    :param alpha: Significance level.
    :type alpha: float
    :raises ValueError: If cat_col has more or less than two unique values.
    """
    data = dataframe.loc[:, [num_col, cat_col]].dropna()

    categories = data[cat_col].unique()
    if len(categories) != 2:
        raise ValueError(
            f"{cat_col} must have exactly two categories, found {len(categories)}."
        )

    group1 = data[data[cat_col] == categories[0]][num_col]
    group2 = data[data[cat_col] == categories[1]][num_col]

    _, p_var = levene(group1, group2)
    equal_var = p_var > alpha

    t_stat, p_val = ttest_ind(group1, group2, equal_var=equal_var)

    print(f"T-statistic: {t_stat:.4f}, p-value: {p_val:.4f}")
    if p_val <= alpha:
        print(
            f"Reject the null hypothesis. Means of {num_col} differ between categories of {cat_col}."
        )
    else:
        print(f"Fail to reject the null hypothesis. Means of {num_col} do not differ.")


def mann_whitney_test(
    dataframe: pd.DataFrame,
    num_col: str,
    cat_col: str,
    group_1: Any,
    group_2: Any,
    alpha: float = 0.05,
) -> None:
    """Performs Mann-Whitney U test.

    :param dataframe: Input DataFrame.
    :type dataframe: pd.DataFrame
    :param num_col: Numerical column.
    :type num_col: str
    :param cat_col: Categorical column (two categories).
    :type cat_col: str
    :param group_1: First category.
    :type group_1: Any
    :param group_2: Second category.
    :type group_2: Any
    :param alpha: Significance level.
    :type alpha: float
    :raises ValueError: If cat_col has more or less than two unique values.
    """
    unique_categories = dataframe[cat_col].dropna().unique()
    if len(unique_categories) != 2:
        raise ValueError(
            f"{cat_col} must have exactly two categories, found {len(unique_categories)}."
        )

    group_1_data = dataframe[dataframe[cat_col] == group_1][num_col].dropna()
    group_2_data = dataframe[dataframe[cat_col] == group_2][num_col].dropna()

    stat, p_value = mannwhitneyu(group_1_data, group_2_data, alternative="two-sided")

    print(f"Mann-Whitney U statistic: {stat}")
    print(f"P-value: {p_value}")
    if p_value <= alpha:
        print(
            f"Reject the null hypothesis. Significant difference in {num_col} between {group_1} and {group_2}."
        )
    else:
        print(
            f"Fail to reject the null hypothesis. No significant difference in {num_col} between {group_1} and {group_2}."
        )


def levene_test(dataframe: pd.DataFrame, num_col: str, cat_col: str) -> None:
    """Performs Levene's Test to check for homogeneity of variances.

    :param dataframe: Input DataFrame.
    :type dataframe: pd.DataFrame
    :param num_col: Numerical column.
    :type num_col: str
    :param cat_col: Categorical column.
    :type cat_col: str
    """
    data = dataframe.loc[:, [num_col, cat_col]].dropna()

    groups: List[Any] = [
        group[num_col].values for _, group in data.groupby(cat_col)
    ]  # Type hint for groups

    stat, p_val = levene(*groups)

    print(f"Levene's Test p-value: {p_val}")

    if p_val <= 0.05:
        print(
            "Reject the null hypothesis. Variances across groups are significantly different."
        )
    else:
        print(
            "Fail to reject the null hypothesis. Variances are not significantly different."
        )


def make_columns_readable(columns: pd.Index) -> pd.Index:
    """
    Transforms column names to be more readable for end-users.

    :param columns: The original column index (typically from a Pandas DataFrame).
    :type columns: pd.Index
    :return: A new column index with readable names.
    :rtype: pd.Index
    """

    readable_columns = []
    for col in columns:
        col = col.replace("standard_scaling__", "")
        col = col.replace("minmax_scaling__", "")
        col = col.replace("nominal_encoding__", "")
        col = col.replace("ordinal_encoding__", "")
        col = col.replace("_", " ")

        # Specific changes to make it more readable
        col = col.replace("brand name", "Brand")
        col = col.replace("processor brand", "Processor")
        col = col.replace("connectivity features", "Connectivity")
        col = col.replace("storage expandability", "Storage Expandable")
        col = col.replace("fast charging available", "Fast Charging")
        col = col.replace("extended memory available", "Memory Expandable")
        col = col.replace("num cores", "Cores")
        col = col.replace("ram capacity", "RAM")
        col = col.replace("internal memory", "Internal Storage")
        col = col.replace("fast charging", "Fast Charging (Watts)")
        col = col.replace("refresh rate", "Refresh Rate (Hz)")
        col = col.replace("num rear cameras", "Rear Cameras")
        col = col.replace("num front cameras", "Front Cameras")
        col = col.replace("primary camera rear", "Rear Camera (MP)")
        col = col.replace("primary camera front", "Front Camera (MP)")
        col = col.replace("extended upto", "Expandable Memory (GB)")
        col = col.replace("performance score", "Performance Score")
        col = col.replace("camera quality", "Camera Quality")
        col = col.replace("screen size", "Screen Size (inches)")
        col = col.replace("resolution", "Resolution")
        col = col.replace("has 5g", "5G")
        col = col.replace("has nfc", "NFC")
        col = col.replace("has ir blaster", "IR Blaster")
        col = col.replace("apple", "Apple")
        col = col.replace("infinix", "Infinix")
        col = col.replace("iqoo", "iQOO")
        col = col.replace("motorola", "Motorola")
        col = col.replace("oneplus", "OnePlus")
        col = col.replace("oppo", "Oppo")
        col = col.replace("poco", "Poco")
        col = col.replace("realme", "Realme")
        col = col.replace("samsung", "Samsung")
        col = col.replace("tecno", "Tecno")
        col = col.replace("vivo", "Vivo")
        col = col.replace("xiaomi", "Xiaomi")
        col = col.replace("bionic", "Bionic")
        col = col.replace("dimensity", "Dimensity")
        col = col.replace("exynos", "Exynos")
        col = col.replace("helio", "Helio")
        col = col.replace("snapdragon", "Snapdragon")
        col = col.replace("tiger", "Tiger")
        col = col.replace("unisoc", "Unisoc")
        col = col.replace("other", "Other")

        readable_columns.append(col)

    return pd.Index(readable_columns)


def encode_fig(fig: plt.Figure) -> str:
    """
    Encodes a matplotlib figure as a base64 string.

    :param fig: The matplotlib figure to encode.
    :type fig: plt.Figure
    :return: The encoded figure as a base64 string.
    :rtype: str
    """

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return img_base64


def adfuller_test(series: pd.Series) -> dict:
    """
    Performs the Augmented Dickey-Fuller (ADF) test for stationarity and provides interpretation.

    :param series: The time series data to test.
    :type series: pd.Series
    :return: A dictionary containing the test statistic, p-value, critical values, and interpretation.
    :rtype: dict
    """
    result = sts.adfuller(series, autolag="AIC")
    test_stat, p_value, _, _, critical_values, _ = result

    # Interpretation
    interpretation = (
        "The series is likely stationary." if p_value < 0.05 else "The series is likely non-stationary."
    )

    return {
        "Test Statistic": test_stat,
        "P-Value": p_value,
        "Critical Values": critical_values,
        "Interpretation": interpretation,
    }


def kpss_test(series: pd.Series) -> dict:
    """
    Performs the Kwiatkowski-Phillips-Schmidt-Shin (KPSS) test for stationarity and provides interpretation.

    :param series: The time series data to test.
    :type series: pd.Series
    :return: A dictionary containing the test statistic, p-value, critical values, and interpretation.
    :rtype: dict
    """
    result = sts.kpss(series, regression="c", nlags="auto")
    test_stat, p_value, _, critical_values = result

    # Interpretation
    interpretation = (
        "The series is likely non-stationary." if p_value < 0.05 else "The series is likely stationary."
    )

    return {
        "Test Statistic": test_stat,
        "P-Value": p_value,
        "Critical Values": critical_values,
        "Interpretation": interpretation,
    }


def prepare_monthly_healthcare_series(df, start_year):
    """
    Prepares a monthly Pandas Series from a DataFrame, specifically for healthcare data.

    Args:
        df (pd.DataFrame): The input DataFrame containing healthcare data.
        start_year (int): The starting year for the monthly DatetimeIndex.

    Returns:
        pd.Series: A Pandas Series with a monthly DatetimeIndex and the "Healthcare" column.
    """
    analysis_df = (
        df.sort_index()
        .assign(index=pd.date_range(start=f"{start_year}-01", periods=len(df), freq='M'))
        .set_index("index")
        .asfreq('M')
        .drop(columns=["month"]) 
        ["Healthcare"]
    )
    return analysis_df