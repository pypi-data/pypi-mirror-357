# jupyterlog: Setup Logging in Jupyter Notebook

`jupyterlog` provides an easy way to setup logging in Jupyter Notebook.


## Installation

```bash
pip install jupyterlog
```

## Usage

```python
import jupyterlog
jupyterlog.setup()

import logging
logging.debug("Debug")
logging.info("Info")
logging.warning("Warning")
logging.error("Error")
logging.critical("Critical")
```

## API

`setup(level: Optional[int]=None, datetime: Optional[datetime.datetime]=None, datefmt: Optional[str]=None, **kwargs)`

Parameters:
- `level`: Logging level. If `None`, do not change current level. Can be set as `logging.DEBUG`, `logging.INFO`, etc.
- `datetime`: Datetime to use for logging. If `None`, use current datetime, usually the system datetime. Can be set as `datetime.datetime(2000, 1, 1)`.
- `datefmt`: Datetime format to use for logging. If `None`, use default format. Can be set as `"%Y-%m-%d %H:%M:%S"`.
- `kwargs`: Additional optional keyword arguments to pass to `logging.Formatter`.
