# LoRaWAN Sensor Visualiser

A demo application to receive sensor data from LoRaWAN devices from an MQTT broker and visualise it on a realtime interactive map.

<p align="center">
        <img src="https://raw.githubusercontent.com/i-DAT/lorawan-map/main/demo.png?raw=true">
</p>

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
