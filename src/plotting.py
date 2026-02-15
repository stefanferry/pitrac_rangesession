import base64
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State
from dash_extensions import EventListener
from pathlib import Path
import os


def interactive_plot(df: pd.DataFrame, y_axes=None):
    """
    y_axes = {
        "ball_speed": 1,
        "club_speed": 1,
        "back_spin": 2,
        "side_spin": 2
    }
    """

    if y_axes is None:
        y_axes = {"ball_speed": 1}

    # -----------------------------
    # FIGURE SETUP
    # -----------------------------
    fig = go.Figure()

    # Y-Achsen definieren
    fig.update_layout(
        yaxis=dict(
            title=dict(text="Y1", 
            font=dict(color="blue")),
            tickfont=dict(color="blue")
        ),
        yaxis2=dict(
            title=dict(text="Y2", font=dict(color="red")),
            tickfont=dict(color="red"),
            overlaying="y",
            side="right"
        ),
        xaxis_title="Timestamp",
        title="Shot Data (Multi‑Axis)"
    )

    # -----------------------------
    # TRACES HINZUFÜGEN
    # -----------------------------
    for col, axis in y_axes.items():
        fig.add_trace(go.Scatter(
            x=df["timestamp_ball_hit_csv"],
            y=df[col],
            mode="markers",
            name=f"{col} (y{axis})",
            customdata=df[["ShotNo"]],
            meta=col,  # wichtig für Hovertemplate
            hovertemplate=(
                "Zeit: %{x}<br>"
                "%{meta}: %{y}<br>"
                "Shot: %{customdata[0]}<extra></extra>"
            ),
            yaxis=f"y{axis}"
        ))

    # -----------------------------
    # DASH APP
    # -----------------------------
    app = Dash(__name__)
    app.server.df = df

    app.layout = html.Div([
        dcc.Store(id="current-index", data=0),

        EventListener(
            id="keyboard",
            events=[{"event": "keydown"}],
            logging=False,
            children=html.Div(tabIndex=0, style={"outline": "none"})
        ),

        html.H2("Interactive Shot-Plot"),

        html.Div([
            html.Div([
                dcc.Graph(
                    id="shot-graph",
                    figure=fig,
                    style={"width": "100%"}
                ),
                html.Div(id="spin-images", style={"marginTop": "20px"})
            ], style={"width": "50%", "display": "inline-block"}),

            html.Div(
                id="other-images",
                style={
                    "width": "48%",
                    "display": "inline-block",
                    "verticalAlign": "top",
                    "paddingLeft": "20px"
                }
            )
        ])
    ])

    # ---------------------------------------------------------
    # HOVER SETS INDEX
    # ---------------------------------------------------------
    @app.callback(
        Output("current-index", "data"),
        Input("shot-graph", "hoverData"),
        State("current-index", "data")
    )
    def hover_set_index(hoverData, current_index):
        if hoverData is None:
            return current_index
        try:
            return hoverData["points"][0]["pointIndex"]
        except:
            return current_index

    # ---------------------------------------------------------
    # KEYBOARD LEFT/RIGHT
    # ---------------------------------------------------------
    @app.callback(
        Output("current-index", "data", allow_duplicate=True),
        Input("keyboard", "event"),
        State("current-index", "data"),
        prevent_initial_call=True
    )
    def keyboard_nav(event, current_index):
        if event is None:
            return current_index

        key = event.get("key", "")

        if key == "ArrowLeft":
            return max(0, current_index - 1)

        if key == "ArrowRight":
            return min(len(df) - 1, current_index + 1)

        return current_index

    # ---------------------------------------------------------
    # IMAGE UPDATE
    # ---------------------------------------------------------
    @app.callback(
        Output("spin-images", "children"),
        Output("other-images", "children"),
        Input("current-index", "data")
    )
    def update_images(idx):
        df = app.server.df
        row = df.iloc[idx]
        images = row.get("images", [])

        SPECIAL = ["spin_ball_1", "spin_ball_2", "ball1_rotated_by_best_angle"]

        special = []
        other = []

        for img in images:
            fname = os.path.basename(img["image_path"])
            if any(k in fname for k in SPECIAL):
                special.append(img)
            else:
                other.append(img)

        # sort special
        def sk(img):
            fname = os.path.basename(img["image_path"])
            for i, k in enumerate(SPECIAL):
                if k in fname:
                    return i
            return 999

        special = sorted(special, key=sk)

        # sort other: final_found_ball last
        other = sorted(
            other,
            key=lambda img: "final_found_ball" in os.path.basename(img["image_path"])
        )

        project_root = Path(__file__).resolve().parent.parent

        # SPIN IMAGES (side by side)
        spin_divs = []
        for img in special:
            abs_path = str(project_root / img["image_path"])
            try:
                with open(abs_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
                spin_divs.append(
                    html.Div([
                        html.Div(os.path.basename(abs_path), style={"fontSize": "12px"}),
                        html.Img(src=f"data:image/png;base64,{encoded}",
                                 style={"width": "100%", "border": "1px solid #ccc"})
                    ], style={"width": "32%", "display": "inline-block", "paddingRight": "5px"})
                )
            except:
                spin_divs.append(html.Div(f"Error loading: {abs_path}"))

        # OTHER IMAGES (vertical)
        other_divs = []
        for img in other:
            abs_path = str(project_root / img["image_path"])
            try:
                with open(abs_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
                other_divs.append(
                    html.Div([
                        html.Div(os.path.basename(abs_path), style={"fontSize": "12px"}),
                        html.Img(src=f"data:image/png;base64,{encoded}",
                                 style={"width": "100%", "border": "1px solid #ccc"})
                    ])
                )
            except:
                other_divs.append(html.Div(f"Error loading: {abs_path}"))

        return html.Div(spin_divs), html.Div(other_divs)

    app.run(debug=True)