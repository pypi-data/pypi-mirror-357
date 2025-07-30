# ita-logger
---
### Requires
Python >= 3.12
---
### Installation
```
uv add ita_logger
```
---
### Usage
config.yaml
```
logging:
  name: "core.general"
  handlers: []
  filepath: "logs/general.log"
  console: True
  loglevel: "logging.DEBUG"
```
python
```
from ita_logger import logger
...
log.info("Hello from logger")
```
