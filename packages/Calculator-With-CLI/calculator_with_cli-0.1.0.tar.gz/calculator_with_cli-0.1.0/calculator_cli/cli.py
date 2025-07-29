import argparse
from .calculator import (
    add, subtract, multiply, divide,
    power, modulus, square_root
)

def main():
    parser = argparse.ArgumentParser(description="CLI Calculator")
    parser.add_argument("operation", choices=["add", "subtract", "multiply", "divide", "power", "modulus", "sqrt"])
    parser.add_argument("numbers", nargs="+", type=float)
    args = parser.parse_args()

    try:
        match args.operation:
            case "add":
                print(add(*args.numbers))
            case "subtract":
                print(subtract(*args.numbers))
            case "multiply":
                print(multiply(*args.numbers))
            case "divide":
                print(divide(*args.numbers))
            case "power":
                if len(args.numbers) != 2:
                    raise ValueError("Power requires exactly 2 arguments")
                print(power(*args.numbers))
            case "modulus":
                if len(args.numbers) != 2:
                    raise ValueError("Modulus requires exactly 2 arguments")
                print(modulus(*args.numbers))
            case "sqrt":
                if len(args.numbers) != 1:
                    raise ValueError("Square root requires 1 argument")
                print(square_root(args.numbers[0]))
    except Exception as e:
        print(f"Error: {e}")
