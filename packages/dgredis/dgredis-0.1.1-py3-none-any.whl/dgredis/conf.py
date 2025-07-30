import dataclasses


@dataclasses.dataclass
class RedisConfig:
    host: str
    port: int
    password: str
