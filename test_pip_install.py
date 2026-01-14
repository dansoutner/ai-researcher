#!/usr/bin/env python3
"""Quick test to verify pip install works with allow_network=True."""
import tempfile
from pathlib import Path
from ai_researcher.ai_researcher_tools.venv_tools import create_venv, run_in_venv

def test_pip_install():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir) / "test_repo"
        repo.mkdir()

        print("=" * 60)
        print("Creating venv...")
        print("=" * 60)
        out_create = create_venv.invoke({"repo_root": str(repo), "venv_dir": ".venv"})
        print(out_create)

        if not out_create.startswith("VENV_CREATED=true"):
            print("❌ FAILED: Could not create venv")
            return False

        print("\n" + "=" * 60)
        print("Testing pip install WITHOUT network (should fail)...")
        print("=" * 60)
        out_no_network = run_in_venv.invoke({
            "repo_root": str(repo),
            "cmd": "pip install requests",
            "allow_network": False,
            "timeout_s": 30,
        })
        print(out_no_network)

        print("\n" + "=" * 60)
        print("Testing pip install WITH network (should succeed)...")
        print("=" * 60)
        out_with_network = run_in_venv.invoke({
            "repo_root": str(repo),
            "cmd": "pip install requests",
            "allow_network": True,
            "timeout_s": 120,
        })
        print(out_with_network)

        if "(exit=0)" in out_with_network and ("Successfully installed" in out_with_network or "Requirement already satisfied" in out_with_network):
            print("\n✅ SUCCESS: pip install works with allow_network=True")
            return True
        else:
            print("\n❌ FAILED: pip install did not succeed with allow_network=True")
            return False

if __name__ == "__main__":
    success = test_pip_install()
    exit(0 if success else 1)

