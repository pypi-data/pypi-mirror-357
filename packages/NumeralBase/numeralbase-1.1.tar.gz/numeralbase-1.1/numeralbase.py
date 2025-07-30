"""
Python library for working with different number systems
"""

import math

__version__ = '1.0'


expanded_alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψωАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя'


def convert_base(number, base_from, base_to, alphabet=expanded_alphabet):
    """
    Converts a number between numeral systems.

    Args:
        number: Input number > 0 (string/int)
        base_from: Source numeral system base (from 1 to len(alphabet))
        base_to: Target numeral system base (from 1 to len(alphabet))
        alphabet: Digit characters in ascending order (default: digits, latin, greece and cyrillic alphabet)

    Returns:
        Number represented in target numeral system (string)

    Example:
        '10A', 16, 10 -> '266'
    """

    decimal = 0
    number = str(number) # Just in case if input is integer
    max_base = len(alphabet)


    if base_from < 1 or base_from > max_base or base_to < 1 or base_to > max_base:
        raise ValueError(f"The base of the number should be from 1 to {max_base}") #ERR

    # Special variation for a 1-system (base=1)
    if base_from == 1 or base_to == 1:
        # Finding symbol for ONE (the second character of the alphabet)
        unit_char = alphabet[1] if len(alphabet) > 1 else '1'

        # Conversion from a 1-system
        if base_from == 1:
            if number == "":
                decimal = 0

            else:
                # Check all characters
                if any(char != unit_char for char in str(number)):
                    raise ValueError(f"For a system with base 1, only the {unit_char} character is allowed") #ERR
                decimal = len(str(number))

        # Conversion to a 1-system
        if base_to == 1:
            if base_from == 1:
                return number

            # To 10-system
            decimal = convert_base(number, base_from, 10, alphabet)
            decimal = int(decimal)

            if decimal == 0:
                return ""
            return unit_char * decimal

        # Convert from base_from = 1 to base_to > 1
        if base_from == 1:
            # To convert to decimal, using a recursive call:
            return convert_base(str(decimal), 10, base_to, alphabet)

    # Create dictionary for character lookup
    char_value = {char: i for i, char in enumerate(alphabet)}

    # Convert to decimal (for base_from != 1)
    number_str = str(number)
    for char in number_str:
        if char not in char_value:
            raise ValueError(f"Invalid character '{char}' in input") #ERR
        digit_value = char_value[char]

        if digit_value >= base_from:
            raise ValueError(f"Digit '{char}' invalid for base {base_from}") #ERR
        decimal = decimal * base_from + digit_value

    # Handle zero value
    if decimal == 0:
        return alphabet[0]

    # Convert to target base (for base_to != 1)
    result = []
    num = decimal
    while num > 0:
        num, remainder = divmod(num, base_to)
        result.append(alphabet[remainder])

    return ''.join(result[::-1])


class NumeralNumber:
    def __init__(self, value: str, base: int, alphabet: str = expanded_alphabet):
        """
        Represents a number in a custom numeral system

        Args:
            value: String representation of the number
            base: Base of the numeral system (1 to len(alphabet))
            alphabet: Digit characters in ascending order
        """


        self.value = value
        self.base = base
        self.alphabet = alphabet
        self._validate()



    def _validate(self):
        """Validate number against its base and alphabet"""
        valid_chars = set(self.alphabet[:self.base])
        for char in self.value:
            if char not in valid_chars:
                raise ValueError(f"Character '{char}' not in valid characters for base {self.base}")

    def to_decimal(self) -> int:
        """Convert to decimal integer"""
        return int(convert_base(self.value, self.base, 10, self.alphabet))



    @classmethod
    def from_decimal(cls, num: int, base: int, alphabet: str = expanded_alphabet):
        """Create from integer"""
        value = convert_base(str(num), 10, base, alphabet)
        return cls(value, base, alphabet)

    def convert_to(self, new_base: int) -> 'NumeralNumber':
        """Convert to another numeral system"""
        value = convert_base(self.value, self.base, new_base, self.alphabet)
        return NumeralNumber(value, new_base, self.alphabet)



    # --------------- Core Arithmetic Operations ---------------
    def _arithmetic_op(self, other, operation):
        """For arithmetic operations"""
        if not isinstance(other, NumeralNumber):
            other = NumeralNumber(str(other), 10)

        a = self.to_decimal()
        b = other.to_decimal()
        result = operation(a, b)
        return NumeralNumber.from_decimal(result, self.base, self.alphabet)

    def __add__(self, other) -> 'NumeralNumber':
        return self._arithmetic_op(other, lambda a, b: a + b)

    def __sub__(self, other) -> 'NumeralNumber':
        return self._arithmetic_op(other, lambda a, b: a - b)

    def __mul__(self, other) -> 'NumeralNumber':
        return self._arithmetic_op(other, lambda a, b: a * b)

    def __floordiv__(self, other) -> 'NumeralNumber':
        return self._arithmetic_op(other, lambda a, b: a // b)

    def __mod__(self, other) -> 'NumeralNumber':
        return self._arithmetic_op(other, lambda a, b: a % b)

    def __pow__(self, other) -> 'NumeralNumber':
        return self._arithmetic_op(other, lambda a, b: a ** b)



    # --------------- Advanced Math Operations ---------------
    def log(self, base=10) -> float:
        """Calculate logarithm in specified base"""
        return math.log(self.to_decimal(), base)

    def sqrt(self) -> 'NumeralNumber':
        """Calculate integer square root"""
        result = math.isqrt(self.to_decimal())
        return NumeralNumber.from_decimal(result, self.base, self.alphabet)

    def factorial(self) -> 'NumeralNumber':
        """Calculate factorial"""
        n = self.to_decimal()
        if n < 0:
            raise ValueError("Factorial not defined for negative numbers")
        result = math.factorial(n)
        return NumeralNumber.from_decimal(result, self.base, self.alphabet)



    # --------------- Comparison Operations ---------------
    def __eq__(self, other) -> bool:
        return self.to_decimal() == other.to_decimal()

    def __lt__(self, other) -> bool:
        return self.to_decimal() < other.to_decimal()

    def __le__(self, other) -> bool:
        return self.to_decimal() <= other.to_decimal()

    def __gt__(self, other) -> bool:
        return self.to_decimal() > other.to_decimal()

    def __ge__(self, other) -> bool:
        return self.to_decimal() >= other.to_decimal()



    # --------------- Type Conversions ---------------
    def __int__(self):
        return self.to_decimal()

    def __float__(self):
        return float(self.to_decimal())



    # --------------- String Representation ---------------
    def __str__(self):
        return self.value

    def __repr__(self):
        return f"NumeralNumber('{self.value}', base={self.base})"
