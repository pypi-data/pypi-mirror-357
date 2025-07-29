# argon2_hasher

A **minimal-surface** Python extension that exposes an optimised, memory-hard
[Argon2id](https://password-hashing.net/argon2-specs.pdf) password hasher implemented in Rust 

---

## Installation

<details>
<summary><strong>Quick-start (debug)</strong></summary>

```bash
pip install maturin            # one-time
maturin develop                # builds & installs in debug mode
````

</details>

<details>
<summary><strong>Production wheel (recommended)</strong></summary>

```bash
# 1. Build an optimised, CPU-tuned wheel…
RUSTFLAGS="-C target-cpu=native" \
  maturin build --release --strip

# 2. Install it
pip install target/wheels/argon2_hasher-*.whl
```

</details>

> **Why two commands?**
> `maturin develop` is great for dev loops but compiles *without*
> optimisations.  For benchmarks or production you’ll want the `--release`
> wheel (20-50 × faster).

---

## Usage

```python
from argon2_hasher import Argon2Hasher

plain_pw = "correct horse battery staple"

# ① Hash ----------------------------------------------------------------
phc = Argon2Hasher.hash(plain_pw)     # '$argon2id$v=19$m=8192,t=2,p=4$…'

# ② Verify --------------------------------------------------------------
assert Argon2Hasher.verify(phc, plain_pw)          # ✅ True
assert not Argon2Hasher.verify(phc, "wrong pass")  # ❌ False
```

That’s it – no knobs exposed to Python; all tuning happens inside the Rust
crate.

---

## API

| Function              | Signature                                       | Description                                                                                                     |
| --------------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `Argon2Hasher.hash`   | `(plain: str, salt: str \| None = None) -> str` | Returns a PHC-encoded Argon2id hash. If `salt` is `None`, a cryptographically-secure 16-byte salt is generated. |
| `Argon2Hasher.verify` | `(hash: str, plain: str) -> bool`               | Constant-time verification. Returns **`True`** if `plain` matches `hash`.                                       |

All errors are raised as `ValueError` (malformed hash / salt) or
`RuntimeError` (internal hashing error).

---

## Tests

```python
# tests/test_argon2_hasher.py
from argon2_hasher import Argon2Hasher

def test_match():
    pw  = "my_secure_password"
    phc = Argon2Hasher.hash(pw)
    assert Argon2Hasher.verify(phc, pw)

def test_mismatch():
    phc = Argon2Hasher.hash("secret")
    assert not Argon2Hasher.verify(phc, "bad")

def test_speed():
    import time, bcrypt
    pw = "pw"
    t0 = time.perf_counter()
    Argon2Hasher.verify(Argon2Hasher.hash(pw), pw)
    argon_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    bcrypt.checkpw(pw.encode(),
                   bcrypt.hashpw(pw.encode(),
                                 bcrypt.gensalt(rounds=12)))
    bcrypt_time = time.perf_counter() - t0

    print(f"argon2 {argon_time:.3f}s  / bcrypt {bcrypt_time:.3f}s")
```

---

## License

`argon2_hasher` is released under the MIT License.  See [`LICENSE`](LICENSE)
for the full text.


