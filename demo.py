from asyncio import Queue
from dataclasses import dataclass
from datetime import datetime
import json

from client import Client, Payload

import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

with open("secrets.json", "r") as f:
    secrets = json.load(f)


class App:
    dash: Dash
    queue: Queue[Payload]
    data: dict[str, Payload] = {}

    def __init__(self):
        with open("data.json", "r") as f:
            data = json.load(f)
            self.data = {
                k: Payload(
                    device_id=k,
                    location=v["location"],
                    received=datetime.fromisoformat(v["received"]),
                    data=v["data"],
                )
                for k, v in data.items()
            }

        self.dash = Dash(title="LoRaWAN Map", update_title=None)  # type:ignore
        self.dash.layout = html.Div(
            [
                dcc.Graph(
                    id="live-map",
                    style={
                        "height": "100vh",
                        "width": "100vw",
                        "padding": 0,
                        "margin": 0,
                    },
                    config={"displayModeBar": False},
                ),
                dcc.Interval(id="interval", interval=2000, n_intervals=0),
            ],
            style={
                "padding": 0,
                "margin": 0,
                "overflow": "hidden",
                "height": "100vh",
                "width": "100vw",
            },
        )
        self.dash.callback(
            Output("live-map", "figure"),
            [Input("interval", "n_intervals")],
        )(self.poll)

        self.queue = Queue()
        for conn in secrets["connections"]:
            QueueClient(
                conn["username"],
                conn["password"],
                conn["url"],
                conn["port"],
                conn["topics"],
                self.queue,
            )

        self.dash.run(debug=True, use_reloader=True)

    def poll(self, n: int):
        save = not self.queue.empty()

        while not self.queue.empty():
            payload = self.queue.get_nowait()
            self.data[payload.device_id] = payload

        if save:
            with open("data.json", "w") as f:
                json.dump({k: p.dump() for k, p in self.data.items()}, f, indent=4)

        df = pd.DataFrame.from_records(
            [
                {
                    "id": payload.device_id,
                    "lat": payload.location[0] if payload.location else None,
                    "lon": payload.location[1] if payload.location else None,
                    "fmt": "".join(
                        f"<b>{k}</b>: {v}<br>" for k, v in payload.data.items()
                    ),
                    "color": str(hash(tuple(payload.data.keys()))),
                }
                for payload in self.data.values()
            ],
        )

        fig = px.scatter_map(
            df,
            lat="lat",
            lon="lon",
            hover_name="id",
            size_max=15,
            custom_data="fmt",
            color="color",
            color_discrete_sequence=px.colors.qualitative.Prism,
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            autosize=True,
            uirevision="keep",
            showlegend=False,
        )
        fig.update_traces(hovertemplate="%{customdata}", marker={"size": 12}, name="")
        return fig


@dataclass
class QueueClient(Client):
    queue: Queue[Payload]

    def on_message(self, payload: Payload):
        self.queue.put_nowait(payload)


App()
