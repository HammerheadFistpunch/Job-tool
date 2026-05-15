from backend.profile.loader import load_profile


def main():
    profile = load_profile()

    print("\n=== PROFILE LOADED SUCCESSFULLY ===\n")
    print(profile[:1000])


if __name__ == "__main__":
    main()
