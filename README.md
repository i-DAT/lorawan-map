# LoRaWAN Sensor Visualiser

A demo application to receive sensor data from LoRaWAN devices from an MQTT broker and visualise it on a realtime interactive map.

<div style="text-align: center;">
    ![LoRaWAN Sensor Visualiser](./demo.png?raw=true)
</div>

## Usage

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `secrets.json` file with the following structure:

```json
{
    "connections": [
        {
            "username": "...",
            "password": "...",
            "url": "...",
            "port": 1234,
            "topics": {
                "topic-name-1": "...",
                ...
            }
        },
        ...
    ]
}
```

Create an empty data file:

```bash
echo {} > data.json
```

Run the app:

```bash
python3 main.py
```

Then visit `http://127.0.0.1:8050/` in a web browser.
