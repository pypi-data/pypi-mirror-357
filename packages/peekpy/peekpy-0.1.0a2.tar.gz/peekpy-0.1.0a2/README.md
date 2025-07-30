# PeekPy

![PyPI - Version](https://img.shields.io/pypi/v/peekpy)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/peekpy)


**PeekPy** is a lightweight Python library for collecting runtime statistics and profiling function calls.

- ✅ Easy to integrate using decorators  
- ⏱️ Built-in analyzers like call counter and execution timer  
- 🧩 Extensible via custom analyzers  
- 📦 Production ready and configurable  

---

## Installation

```bash
pip install peekpy
```

## Quick Start
```python
from peekpy.core.analyzers.call_counter import CallCounter
from peekpy.core.analyzers.timer import TimerCount
from peekpy.storage import save_stats_to_file


enable()  # Enable PeekPy globally

@analyze(analyzers=[CallCounter(), Timer()])
def my_function(x, y):
    return x + y

my_function(3, 4)
my_function(1, 2)

print(manager.get_stats())  # Print collected stats
save_stats_to_file("stats.json")

```

## Features
- CallCounter → tracks how many times a function is called
- Timer → measures execution time per call
- StatsManager → central place to store and export stats
- @analyze() → flexible and customizable decorator

## Usage
### @analyze Decorator
```python
@analyze(analyzers=[CallCounter(), Timer()])
def your_function(): ...

```
Each analyzer must implement a .before() and .after() method, and inherits from BaseAnalyzer.

### Enable or Disable Analysis Globally
```python
from peekpy.config import enable, disable, is_enabled

enable()
# or
disable()
```

### Exporting Statistics
All statistics are collected by the StatsManager singleton:

```python
import peekpy
from peekpy.storage import save_stats_to_file


print(json.dumps(peekpy.get_stats(), indent=4))

save_stats_to_file("stats.json")
```
