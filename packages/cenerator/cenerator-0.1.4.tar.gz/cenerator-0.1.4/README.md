# Cenerator

A Minecraft data pack creation utility

## Features

* Procedurally generate Minecraft data packs with Python
* As this is just a fancy way of writing to files, it is fully customizable, for example with functions
* Some convenient shorthand features
* Outputs everything in a data pack, ready to go

## Installation

Installed with pip, something like

```
pip3 install -U cenerator
```

Or perhaps on Windows

```
py -m pip install -U cenerator
```

## Example usage

See `examples/` directory for more examples.

### Hello, world!

```py
import cenerator

p = cenerator.Pack('hello_world',
    default_namespace='hello_world',
    description='A hello world datapack made with cenerator',
    pack_format=71,
)


@p.func(tags = ['minecraft:load'])
def hello_world(c):
    c('say Hello, world!')
```

This outputs a data pack which executes the command `say Hello, world!` on load.

### Macros

The power of `cenerator` becomes more evident in more complex programs that need branching logic and complicated `/execute` chains.

The following example showcases use of functions that take `c` and use it to output commands (referred to as "macros")

```py
def say_with_all(c, format_str, values):
    for v in values:
        c(f'say {format_str.format(v)}')


@p.func(tags = ['minecraft:load'])
def macro(c):
    values = ['John', 'Joe', 'Jane', 'Jill']
    say_with_all(c, 'Hello, {}!', values)
    say_with_all(c, 'Goodbye, {}!', values)
```

This results in a `mcfunction` file with some otherwise tedious-to-write code:

```mcfunction
say Hello, John!
say Hello, Joe!
say Hello, Jane!
say Hello, Jill!
say Goodbye, John!
say Goodbye, Joe!
say Goodbye, Jane!
say Goodbye, Jill!
```

This is extremely useful for situations where a lot of code must be repeated with different but constant parameters.
