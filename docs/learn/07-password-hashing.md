# Password hashing

1. **One-line definition**
Password hashing turns a password into a one-way string that can be checked later but cannot be reversed into the original password.

2. **Why it exists** (the problem it solves)
If the database stores real passwords, anyone who copies the `users` table can log in as those people and reuse the passwords on other sites. A hash lets the server check “did this person type the right password?” without keeping the password.

3. **Analogy**
It is like a wax seal. You can press the same stamp and see that the new impression matches the old one. You cannot pull the stamp back out of the wax.

4. **How it works** (step by step)
- **Step 1:** On register, bcrypt mixes the password with a random salt and runs a slow hash. The result (salt included) is stored in `users.password_hash`.
- **Step 2:** On login, bcrypt hashes the typed password with the salt inside the stored hash.
- **Step 3:** If the two hashes match, the password was correct. The plain password is never written to the database or the API response.
- **Step 4:** bcrypt only accepts 72 bytes. Register rejects anything longer before hashing.

5. **Where it is in FinScope** (file + function)
- File: [backend/app/core/security.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/core/security.py)
- `hash_password` and `verify_password`
- Called from `register_user` and `authenticate_user` in [backend/app/services/auth_service.py](file:///c:/Users/Sayli/Downloads/RAG/backend/app/services/auth_service.py)

6. **Common mistakes**
- Storing the password, or storing a fast hash such as plain SHA-256 with no salt. Those are easy to guess with a word list.
- Returning `password_hash` from an API schema. `UserPublic` leaves it out on purpose.
- Comparing hashes with `==` in Python in a way that stops at the first different character. `bcrypt.checkpw` compares them in constant time.

7. **Check yourself**
1. *Why is the stored value different every time for the same password?*
2. *What does login compare, the typed password or a new hash?*
3. *Why is a short password rejected with 422 before it reaches bcrypt?*

---
**Answers:**
1. bcrypt generates a new random salt for each hash, and the salt is stored inside the hash string.
2. Login hashes the typed password with the stored salt and checks whether that hash matches. It never decrypts the stored value.
3. The register schema requires at least 8 characters so weak passwords never get stored. bcrypt itself does not enforce that rule.
