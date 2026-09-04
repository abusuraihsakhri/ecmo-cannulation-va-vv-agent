"""Allow running the package as a module: python -m ecmo_cannulation_va_vv_agent"""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
