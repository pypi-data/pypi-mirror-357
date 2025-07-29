import subprocess

def test_cli_help():
    result = subprocess.run(
        ["simple-fastapi-backend-server", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5
    )
    output = result.stdout.decode()
    assert "Usage:" in output
