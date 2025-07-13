class NATSConnector:
    def __init__(self, host=None, port=None, **kwargs):
        self.host = host
        self.port = port

    def connect(self):
        # Simulate a connection to NATS
        print(f"Connected to NATS servers: {self.host}:{self.port}")

    def publish(self, subject, message):
        # Simulate publishing a message to a NATS subject
        print(f"Published message to {subject}: {message}")

    def subscribe(self, subject, callback):
        # Simulate subscribing to a NATS subject
        print(f"Subscribed to {subject}")
        # Simulate receiving a message
        callback("Test message")
