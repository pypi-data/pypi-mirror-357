import math
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add(*args):
    result = sum(args)
    logger.info(f"add{args} = {result}")
    return result

def subtract(a, *args):
    result = a
    for num in args:
        result -= num
    logger.info(f"subtract{(a, *args)} = {result}")
    return result

def multiply(*args):
    result = 1
    for num in args:
        result *= num
    logger.info(f"multiply{args} = {result}")
    return result

def divide(a, *args):
    result = a
    for num in args:
        if num == 0:
            logger.error("Division by zero attempt.")
            raise ValueError("Cannot divide by zero")
        result /= num
    logger.info(f"divide{(a, *args)} = {result}")
    return result

def power(base, exponent):
    result = base ** exponent
    logger.info(f"power({base}, {exponent}) = {result}")
    return result

def modulus(a, b):
    result = a % b
    logger.info(f"modulus({a}, {b}) = {result}")
    return result

def square_root(a):
    if a < 0:
        logger.error("Tried to take square root of negative number.")
        raise ValueError("Cannot take square root of negative number")
    result = math.sqrt(a)
    logger.info(f"square_root({a}) = {result}")
    return result
