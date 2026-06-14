import argparse
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Run momo E2E tests")
    parser.add_argument(
        "-n",
        "--numprocesses",
        metavar="N",
        help='parallel workers: "auto", "logical", or a number (e.g. 4)',
    )
    parser.add_argument("--headed", action="store_true", help="run browser in headed mode")
    args, extra = parser.parse_known_args()

    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "-s"]
    if args.numprocesses is not None:
        cmd.extend(["-n", str(args.numprocesses)])
    if args.headed:
        cmd.append("--headed")
    cmd.extend(extra)

    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
