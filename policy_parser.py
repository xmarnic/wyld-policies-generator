POLICIES_FILE = "/software/WYLD/Unicorn/Config/policies"
IGNORE_FILE = "ignore_libraries.txt"


def load_ignore_list(ignore_path):
    try:
        with open(ignore_path) as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        return set()


def parse_libraries(policies_path, ignore_path=IGNORE_FILE):
    ignore = load_ignore_list(ignore_path)
    libraries = []
    with open(policies_path) as f:
        for line in f:
            if not line.startswith("LIBR|"):
                continue
            parts = line.strip().split("|")
            libcode = parts[1]
            lib = parts[2]
            library = parts[21]
            if lib in ignore:
                continue
            libraries.append({
                "libcode": libcode,
                "lib": lib,
                "library": library,
            })
    return libraries


if __name__ == "__main__":
    libraries = parse_libraries(POLICIES_FILE)
    for lib in libraries:
        print(lib)
