from frostbound.monads.either import Either
from frostbound.monads.maybe import Maybe


# Example for Either monad
def divide(a: int, b: int) -> Either[float, str]:
    """
    Safely divide two numbers.

    Parameters
    ----------
    a : int
        The dividend
    b : int
        The divisor

    Returns
    -------
    Either[float, str]
        A success with the result or a failure with an error message
    """
    if b == 0:
        return Either.failure("Division by zero")
    return Either.success(a / b)

# Example for Maybe monad
def get_user_setting(user_id: str, setting: str) -> Maybe[str]:
    """
    Get a user setting if it exists.

    Parameters
    ----------
    user_id : str
        The ID of the user
    setting : str
        The setting name

    Returns
    -------
    Maybe[str]
        The setting value or none if it doesn't exist
    """
    # Simulating a database lookup
    user_settings = {
        "user1": {"theme": "dark", "notifications": "enabled"},
        "user2": {"theme": "light"}
    }

    if user_id not in user_settings:
        return Maybe.none()

    user = user_settings[user_id]
    if setting not in user:
        return Maybe.none()

    return Maybe.some(user[setting])

if __name__ == "__main__":
    # Example usage of Either monad
    result = divide(10, 2)
    print(result)

    # Example usage of Maybe monad
    setting = get_user_setting("user1", "theme")
    print(setting)
