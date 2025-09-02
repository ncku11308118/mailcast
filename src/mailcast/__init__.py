from structlog import configure
from structlog.processors import (
    JSONRenderer,
    TimeStamper,
)

configure(
    processors=[
        TimeStamper("iso", utc=False),
        JSONRenderer(),
    ],
)
