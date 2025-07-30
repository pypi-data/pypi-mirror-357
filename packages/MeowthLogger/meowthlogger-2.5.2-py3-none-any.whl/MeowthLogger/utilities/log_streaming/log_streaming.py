import os


def get_log_stream_html(
    title: str = "Log streamer", ws_url: str = None
) -> str:
    path = os.path.abspath(
        os.path.join(__file__, os.pardir, "LogStreaming.html")
    )
    with open(path, encoding="utf-8") as file:
        html = file.read()

    html = html.replace("{{ENV_TITLE}}", title)

    return html
