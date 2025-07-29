# hexrgb/tests/test_main.py

import subprocess

def run_command(args):
    result = subprocess.run(
        ["python3", "main.py"] + args,
        capture_output=True,
        text=True
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def test_valid_hex_to_rgb():
    out, err, code = run_command(["--hex-to-rgb", "#AABBCC"])
    assert code == 0
    assert "RGB: 170,187,204" in out

def test_valid_hex_to_rgb_no_hash():
    out, err, code = run_command(["--hex-to-rgb", "00FF00"])
    assert code == 0
    assert "RGB: 0,255,0" in out

def test_invalid_hex_format():
    out, err, code = run_command(["--hex-to-rgb", "#XYZ123"])
    assert code == 1
    assert "Invalid HEX format" in out

def test_missing_hex_argument():
    out, err, code = run_command([])
    assert code == 1
    assert "You must provide a HEX value" in out