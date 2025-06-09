from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import json
from datetime import datetime

from paho.mqtt.client import Client as _Client, MQTTMessage
from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt.reasoncodes import ReasonCode


@dataclass
class Payload:
    """
    MQTT payload received from a LoRaWAN device.
    A payload contains a UUID, location, timestamp, and a dictionary of arbitrary
    sensor data.
    """

    device_id: str
    location: tuple[float, float] | None
    received: datetime
    data: dict[str, float]

    def dump(self) -> dict:
        return {
            "device_id": self.device_id,
            "location": self.location,
            "received": self.received.isoformat(),
            "data": self.data,
        }


@dataclass
class Client(ABC):
    """
    Base class for MQTT clients that receive LoRaWAN payloads.
    The only required method is `on_message`, which is called when a new
    payload is received.
    """

    username: str
    password: str
    url: str
    port: int
    topics: dict[str, str]

    _client: _Client = field(init=False, repr=False)

    def __post_init__(self):
        # Initialise a client
        # TLS is required by most MQTT brokers
        self._client = _Client(CallbackAPIVersion.VERSION2)
        self._client.username_pw_set(self.username, self.password)
        self._client.tls_set()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.connect(self.url, self.port)
        # Start in a separate thread
        self._client.loop_start()

    def _on_connect(self, client, userdata, flags, code: ReasonCode, properties):
        # On connection, subscribe to all listed topics
        # This could be called multiple times on reconnect
        self.on_connect(code)
        self._client.subscribe([(t, 0) for t in self.topics.values()])

    def _on_message(self, client, userdata, msg: MQTTMessage):
        # Construct a payload object from the JSON message
        data = json.loads(msg.payload)
        if "locations" in data["uplink_message"]:
            location = (
                data["uplink_message"]["locations"]["user"]["latitude"],
                data["uplink_message"]["locations"]["user"]["longitude"],
            )
        else:
            location = None
        payload = Payload(
            device_id=data["end_device_ids"]["device_id"],
            location=location,
            received=datetime.fromisoformat(data["received_at"]),
            data=data["uplink_message"]["decoded_payload"],
        )
        self.on_message(payload)

    def on_connect(self, code: ReasonCode):
        if code.is_failure:
            raise RuntimeError(f"Failed to connect to MQTT broker: {code}")

    @abstractmethod
    def on_message(self, payload: Payload): ...
