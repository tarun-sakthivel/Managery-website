import os, bcrypt, passlib
print("PASSLIB_BUILTIN_BCRYPT:", os.environ.get("PASSLIB_BUILTIN_BCRYPT"))
print("bcrypt.__version__:", getattr(bcrypt, "__version__", None))
print("bcrypt.__about__:", getattr(bcrypt, "__about__", None))
print("bcrypt attrs sample:", [a for a in dir(bcrypt) if not a.startswith("_")][:20])
print("passlib version:", getattr(passlib, "__version__", None))