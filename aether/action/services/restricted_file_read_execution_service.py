"""Thin service boundary for explicit governed restricted-read attempts."""


def handle_restricted_file_read_execution(request):
    from aether.core.coordination import execute_approved_restricted_read
    return execute_approved_restricted_read(request)
