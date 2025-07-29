import random
import string
import os


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


class Configuration:
    """
    Cartinese translation configuration.
    """

    DEFAULT_DOUBLE_SPACE_P = 0.3
    DEFAULT_SWAP_LETTER_P = 0.4
    DEFAULT_UPPER_P = 0.6

    def __init__(
        self,
        double_space_p: float = DEFAULT_DOUBLE_SPACE_P,
        swap_letter_p: float = DEFAULT_SWAP_LETTER_P,
        upper_p: float = DEFAULT_UPPER_P,
    ):
        self.double_space_p = double_space_p
        self.swap_letter_p = swap_letter_p
        self.upper_p = upper_p


def translate(text: str, configuration: Configuration) -> str:
    """
    Translate normal text into Cartinese.

    # Example

    ```python
    import cartinese

    text = "Hello, what is your name?"

    configuration = cartinese.Configuration()
    translated = cartinese.translate(text, configuration)

    print(translated)
    ```
    """
    for sign in PUNCTUATION:
        if random.random() <= 0.7 and sign in text:
            text = text.replace(sign, " " + sign + " ")
    text = text.lower()
    output = ""
    for c in text:
        if c == " " and random.random() <= DOUBLE_SPACE_P:
            c = "  "
        elif random.random() <= SWAP_LETTER_P and c in LETTER_MAP:
            c = LETTER_MAP[c]
        elif random.random() <= UPPER_P:
            c = c.upper()
        output += c
    output = output.strip()
    return output


def seeyuh():
    if os.getenv("SEEYUH"):
        print("seeyuh")


def main():
    seeyuh()


if __name__ == "__main__":
    main()
