from colorama import init, Fore, Style
import html

# Initialize colorama
init(autoreset=True)

# Ask user for input
text1 = input("Enter Text1:\n")
text2 = input("Enter Text2:\n")

# HTML report content
html_rows = []

max_length = max(len(text1), len(text2))

print("\n=== DIFFERENCES ===\n")

difference_found = False

for i in range(max_length):

    char1 = text1[i] if i < len(text1) else ""
    char2 = text2[i] if i < len(text2) else ""

    if char1 != char2:
        difference_found = True

        # Unicode codes
        code1 = f"U+{ord(char1):04X}" if char1 else "NONE"
        code2 = f"U+{ord(char2):04X}" if char2 else "NONE"

        # Character names for invisible symbols
        visible1 = repr(char1)[1:-1] if char1 else "(missing)"
        visible2 = repr(char2)[1:-1] if char2 else "(missing)"

        print(Fore.RED + f"Position {i}")
        print(Fore.YELLOW + f"Text1: '{visible1}'   {code1}")
        print(Fore.CYAN + f"Text2: '{visible2}'   {code2}")
        print("-" * 50)

        # Add to HTML
        html_rows.append(f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(visible1)}</td>
            <td>{code1}</td>
            <td>{html.escape(visible2)}</td>
            <td>{code2}</td>
        </tr>
        """)

if not difference_found:
    print(Fore.GREEN + "The texts are identical.")

    html_content = """
    <html>
    <body>
        <h2>The texts are identical.</h2>
    </body>
    </html>
    """
else:
    html_content = f"""
    <html>
    <head>
        <title>Text Comparison Report</title>
        <style>
            body {{
                font-family: Arial;
                margin: 20px;
            }}

            table {{
                border-collapse: collapse;
                width: 100%;
            }}

            th, td {{
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }}

            th {{
                background-color: #dddddd;
            }}

            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
        </style>
    </head>
    <body>

    <h2>Text Comparison Report</h2>

    <table>
        <tr>
            <th>Position</th>
            <th>Text1 Symbol</th>
            <th>Unicode</th>
            <th>Text2 Symbol</th>
            <th>Unicode</th>
        </tr>

        {''.join(html_rows)}

    </table>

    </body>
    </html>
    """

# Save HTML report
report_file = "Reports/comparison_report.html"

with open(report_file, "w", encoding="utf-8") as file:
    file.write(html_content)

print(Fore.GREEN + f"\nHTML report saved as: {report_file}")
