from argon2_hasher import Argon2Hasher

import time

import bcrypt


class PythonHasher:
    @staticmethod
    def hash_bcrypt(plain: str) -> bytes:
        salt = bcrypt.gensalt(rounds=12, prefix=b"2a")
        plain_bytes = str(plain).encode("utf8")
        return bcrypt.hashpw(plain_bytes, salt)

    @staticmethod
    def verify_bcrypt(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(
            str(plain).encode("utf8"),
            hashed,
        )


def test_match_password():  # Test matching passwords
    plain_text = "my_secure_password"
    hashed = Argon2Hasher.hash(plain_text)

    assert (
        Argon2Hasher.verify(hashed, plain_text) is True
    ), "Password verification failed"

    print("****", Argon2Hasher.verify(hashed, plain_text))
    print("Password match test passed!")


def test_mismatch_password():
    plain_text = "my_secure_password"
    hashed = Argon2Hasher.hash(plain_text)

    assert (
        Argon2Hasher.verify(hashed, "wrong_password") is False
    ), "Password verification should have failed"

    print("****", Argon2Hasher.verify(hashed, "wrong_password"))
    print("Password mismatch test passed!")


def compare_execution_times():
    plain_text = "123456"
    # Measure execution time for Argon2Hasher
    start = time.perf_counter()
    hashed = Argon2Hasher.hash(plain_text)
    result = Argon2Hasher.verify(hashed, plain_text)
    argon2_time = time.perf_counter() - start

    print(f"Argon2Hasher execution time: {argon2_time}")
    assert result is True, "Argon2Hasher verification failed"

    print("Argon2Hasher execution time test passed!")
    # Measure execution time for Python Hasher
    python_start = time.perf_counter()
    python_hashed = PythonHasher.hash_bcrypt(plain_text)
    result = PythonHasher.verify_bcrypt(plain_text, python_hashed)
    python_time = time.perf_counter() - python_start
    assert result is True, "Python Hasher verification failed"
    print("Python Hasher execution time test passed!")
    print(f"Python Hasher execution time: {python_time}")

    # Compare execution times
    if argon2_time < python_time:
        print("Argon2Hasher is faster than Python Hasher")
    elif argon2_time > python_time:
        print("Python Hasher is faster than Argon2Hasher")
    else:
        print("Both hashers have the same execution time")


if __name__ == "__main__":
    test_match_password()
    test_mismatch_password()
    compare_execution_times()
    print("All tests passed!")
