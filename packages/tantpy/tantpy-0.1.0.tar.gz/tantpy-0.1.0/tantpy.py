import functools


def tantpy(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Something went wrong: {e}")
            print("Tant pis. The code moves on, like a river past a fallen tree.")
            return None

    return wrapper


if __name__ == "__main__":
    @tantpy
    def risky_division(a, b):
        return a / b


    result = risky_division(10, 0)
    print("Result:", result)
