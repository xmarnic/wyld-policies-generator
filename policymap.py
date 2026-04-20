from policy_parser import parse_libraries, POLICIES_FILE


def main():
    libraries = parse_libraries(POLICIES_FILE)
    for lib in libraries:
        print(lib)


if __name__ == "__main__":
    main()
