import random
import string
from typing import Optional


class Configuration:
    """
    Cartinese translation configuration.
    """

    DEFAULT_DOUBLE_SPACE_P = 0.3
    DEFAULT_SWAP_LETTER_P = 0.4
    DEFAULT_UPPER_P = 0.6
    DEFAULT_SEPARATE_PUNCTUATION_P = 0.7

    def __init__(
        self,
        double_space_p: Optional[float] = DEFAULT_DOUBLE_SPACE_P,
        swap_letter_p: Optional[float] = DEFAULT_SWAP_LETTER_P,
        upper_p: Optional[float] = DEFAULT_UPPER_P,
        separate_punctuation_p: Optional[float] = DEFAULT_SEPARATE_PUNCTUATION_P,
    ):
        self.double_space_p = double_space_p
        self.swap_letter_p = swap_letter_p
        self.upper_p = upper_p
        self.separate_punctuation_p = separate_punctuation_p


LETTER_MAP = {
    "e": "3",
    "g": "9",
    "i": "1",
    "l": "1",
    "o": "0",
    "s": "5",
    "t": "+",
    "z": "2",
}

PUNCTUATION = list(string.punctuation)

DEFAULT_CONFIGURATION = Configuration()


def translate(
    text: str, configuration: Optional[Configuration] = DEFAULT_CONFIGURATION
) -> str:
    """
    Translate normal text into Cartinese.

    # Example

    ```python
    import cartinese

    text = "Hello, what is your name?"
    translated = cartinese.translate(text)
    print(translated)
    ```

    # Configure


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
    """
    for sign in PUNCTUATION:
        if random.random() <= configuration.separate_punctuation_p and sign in text:
            text = text.replace(sign, " " + sign + " ")
    text = text.lower()
    output = ""
    for c in text:
        if c == " " and random.random() <= configuration.double_space_p:
            c = "  "
        elif random.random() <= configuration.swap_letter_p and c in LETTER_MAP:
            c = LETTER_MAP[c]
        elif random.random() <= configuration.upper_p:
            c = c.upper()
        output += c
    output = output.strip()
    return output


def seeyuh():
    print(translate("seeyuh"))
