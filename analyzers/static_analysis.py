def check_long_lines(code):
    warnings = []

    for i, line in enumerate(code.splitlines(), start=1):
        if len(line) > 80:
            warnings.append(f"Line {i} exceeds 80 characters.")

    return warnings