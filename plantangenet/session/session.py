class Session:
    def __init__(self, id: str, name: str, identity: str, policy: str, metadata: dict, spec: dict, description: str = '', **kwargs):
        self.id = id
        self.name = name
        self.identity = identity
        self.policy = policy
        self.metadata = metadata
        self.spec = spec
        self.description = description

# metadata:
#   phase: setup
#   name: tictactoe
#   displayName: *session_name
#   labels:
#     session: tictactoe
# spec:
#   arenas:
#     selector:
#       matchLabels:
#         session: tictactoe
#         squad: arena
#   referees:
#     selector:
#       matchLabels:
#         session: tictactoe
#         squad: referee
#   players:
#     selector:
#       matchLabels:
#         session: tictactoe
#         squad: player
