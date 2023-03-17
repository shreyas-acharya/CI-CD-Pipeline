import json
import sys


def analyze():
    with open(sys.argv[0]) as file:
        data = json.load(file)
        files_scanned = len(data["paths"]["scanned"])
        errors = len(data["errors"])
        warnings = len(data["results"]) - errors
        print("SAST Analysis:")
        print(f"Number of files scanned : {files_scanned}")
        print(f"Number of errors : {errors}")
        print(f"Number of warnings : {warnings}")

    if errors != 0:
        sys.exit(2)
    elif warnings != 0:
        "Warnings found!!!"
    sys.exit(0)


analyze()
