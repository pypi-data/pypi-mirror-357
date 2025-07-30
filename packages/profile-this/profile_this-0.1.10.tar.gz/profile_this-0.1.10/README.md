<div align="center">
  <img src="https://raw.githubusercontent.com/michaelthomasletts/profile-this/refs/heads/main/docs/profile-this.png" />
</div>

</br>

![PyPI - Version](https://img.shields.io/pypi/v/profile-this?logo=pypi)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/profile-this?logo=python)

Sometimes you need sophisticated line-by-line profiling for optimizing your Python code. Other times, you just want a quick and basic memory profile chart.

There are plenty of tools for the former use-case, e.g. `py-spy` or `vprof`. But not many (or any) tools for the latter use-case.

`profile-this` is a stupid simple memory profiler for people who just want a basic memory profiling plot without writing one from scratch.

### Links

[Source Code](https://github.com/michaelthomasletts/profile-this)

[PyPI](https://pypi.org/project/profile-this/)

### Example

Install it like this:

```bash
pip install profile-this
```

Do this:

```python
from random import randint
from profile_this import ProfileThis

def func(n=10_000_000):
    return sum([randint(0, i + 1) for i in range(n)])

profiler = ProfileThis()
profiler.start()
func()
profiler.stop()
profiler.plot(
    title="Profile for func", path="docs/func.png"
)
```

Or this:

```python
with ProfileThis() as profiler:
    func()

profiler.plot(
    title="Profile for func",
    path="docs/func.png",
)
```

Or this:

```python
from profile_this import profilethis

@profilethis(title="Profile for func", path="docs/func.png")
def func(n=10_000_000):
    return sum([randint(0, i + 1) for i in range(n)])

func()
```

To get this:

![func image](https://raw.githubusercontent.com/michaelthomasletts/profile-this/refs/heads/main/docs/func.png)