import re

FORMATS = {
    "standard": (":", 2, False),
    "hyphen": ("-", 2, False),
    "space": (" ", 2, False),
    "lowercase": (":", 2, True),
    "no_separator": ("", 12, False),
    "cisco": (".", 4, True),
}


def convert_mac(mac_address, format_type):
    """
    Converts a MAC address to the specified format.

    Args:
        mac_address (str): MAC address in any format (e.g., '00:1A:2B:3C:4D:5E', '001A2B3C4D5E').
        format_type (str): Output format.

    Returns:
        str: Converted MAC address in the specified format.

    Raises:
        ValueError: If the MAC address is invalid or the format is unsupported.
    """
    mac = re.sub(r"[^A-F0-9]", "", mac_address.upper())

    if len(mac) != 12 or not all(c in "0123456789ABCDEF" for c in mac):
        raise ValueError("Invalid MAC address")

    if format_type not in FORMATS:
        raise ValueError("Unsupported format")

    separator, chunk_size, lowercase = FORMATS[format_type]
    result = separator.join([mac[i : i + chunk_size] for i in range(0, 12, chunk_size)])
    return result.lower() if lowercase else result


def main():
    """
    Prompts for a MAC address and displays it in all available formats.
    """
    while True:
        try:
            mac_address = input("Enter MAC address (or 'exit' to quit): ").strip()
            if mac_address.lower() == "exit":
                print("Program terminated.")
                break

            print("\nResults:")
            for format_type in FORMATS:
                result = convert_mac(mac_address, format_type)
                print(result)
            print()

        except ValueError as e:
            print(f"Error: {e}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nProgram terminated.")
            break


if __name__ == "__main__":
    main()
