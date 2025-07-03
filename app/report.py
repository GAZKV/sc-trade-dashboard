import io
import base64
from pathlib import Path
from jinja2 import Template
import json
import matplotlib.pyplot as plt


def fig_to_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()

HTML_TEMPLATE = Path(__file__).parent / "web" / "templates" / "dashboard.html"


def render_html(ctx: dict, dst: Path):
    """Render dashboard template with embedded JSON context."""
    template = Template(HTML_TEMPLATE.read_text(encoding="utf-8"))
    html = template.render(ctx_json=json.dumps(ctx))
    dst.write_text(html, encoding="utf-8")
