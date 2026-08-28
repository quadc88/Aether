"""Bounded OAS package namespace.

The mutation-capable kernel remains an internal implementation module. Ordinary
runtime code must not obtain it through the public package namespace.
"""

__all__: tuple[str, ...] = ()
