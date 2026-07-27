# PyGrahpQ
A GUI Pygame Wrapper

When I was learning to program, I used two libraries that wrapped a larger environment.
1. [cmu_graphics](https://github.com/cmu-cs-academy/desktop-cmu-graphics), for CMU CS Academy 
2. [graphics](https://mcsp.wartburg.edu/zelle/python/graphics/graphics.pdf), by John Zelle for “Python Programming: An Introduction to Computer
Science” (Franklin, Beedle & Associates)

These environments were really great for learning the basics of object oriented programming in Python. That being said, using either for work beyond the classroom becomes cumbersome quickly. CMU's package includes a wide variety of safety nets which make it difficult to build complex projects, and Zelle's package wraps TKInter, and I prefer pygame. Also, the original pygame died and is being carried on by [pygame-ce](). 
So I decided I would build my own pygame-ce wrapper without guardrails so that I could break Python on my own.

## Depndencies
1. Python (3.13.0+)
2. pygame-ce (2.5.7+)

## Minimal implementation
```python
from pygraphq import *
app = App()

## Your code here

if __name__ == '__main__':
    app.start()
```

That's how easy it is.