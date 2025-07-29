Translate normal text into Cartinese.

# Usage

```python
import cartinese

text = "Hello, what is your name?"

configuration = cartinese.Configuration()
translated = cartinese.translate(text, configuration)

print(translated)
```

# Configuration

```python
import cartinese

text = "Hello, what is your name?"

# you can use
configuration = cartinese.Configuration()
configuration.swap_letter_p = 0.9
# or
configuration = cartinese.Configuration(swap_letter_p = 0.9)

translated = cartinese.translate(text)
print(translated)
```
