from Populate_Test_Column import main as populate_test
from Build_Options_Column import main as build_options


def main():

    processed_count = 0

    while True:

        try:

            print("\n" + "=" * 60)
            print(
                f"Iteration {processed_count + 1}"
            )
            print("=" * 60)

            populate_test()

            build_options()

            processed_count += 1

        except Exception as ex:

            message = str(ex)

            if "No source file found" in message:

                print("\n")
                print("=" * 60)
                print(
                    "Processing complete."
                )
                print(
                    f"{processed_count} file(s) "
                    f"processed."
                )
                print("=" * 60)

                return

            print("\n")
            print("=" * 60)
            print("ERROR")
            print("=" * 60)
            print(message)

            raise


if __name__ == "__main__":
    main()