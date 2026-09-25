import base64
import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

__all__ = ["fig_to_base64_uri"]


def fig_to_base64_uri(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
    plt.close(fig)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"
