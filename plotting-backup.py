import base64
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State
import os
from pathlib import Path
from dash_extensions import EventListener


"""def interactive_plot(df: pd.DataFrame):

    fig = px.scatter(
        df,
        x="timestamp_ball_hit_csv",
        y="ball_speed",
        custom_data=["ShotNo"],
        title="Ball Speed with Image-Hover"
    )"""

def interactive_plot(df: pd.DataFrame, y_columns=None):

    if y_columns is None:
        y_columns = ["ball_speed"]

    import plotly.graph_objects as go
    fig = go.Figure()

    for col in y_columns:
        fig.add_trace(go.Scatter(
            x=df["timestamp_ball_hit_csv"],
            y=df[col],
            mode="markers",
            name=col,
            customdata=df[["ShotNo"]],
            hovertemplate=(
                "Zeit: %{x}<br>"
                f"{col}: "+"%{y}<br>"
                "Shot: %{customdata[0]}<extra></extra>"
            )
        ))

    fig.update_layout(title="Shot Data", xaxis_title="Timestamp")

    fig.update_traces(
        hovertemplate=(
            "Zeit: %{x}<br>"
            "Ball Speed: %{y}<br>"
            "Shot: %{customdata[0]}<extra></extra>"
        )
    )

    app = Dash(__name__)
    app.server.df = df

    app.layout = html.Div([
        dcc.Store(id="current-index", data=0),

        # Keyboard listener MUST have tabIndex to receive events
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