import io
import base64
from pathlib import Path
from jinja2 import Template
import matplotlib.pyplot as plt


def fig_to_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()

HTML_TEMPLATE = Path(__file__).parent / "web" / "templates" / "dashboard.html"


def render_html(ctx: dict, dst: Path):
    template = Template(HTML_TEMPLATE.read_text(encoding="utf-8"))
    dst.write_text(template.render(**ctx), encoding="utf-8")
