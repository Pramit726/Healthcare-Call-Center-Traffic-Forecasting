import base64
import io
import pandas as pd
import matplotlib.pyplot as plt


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
