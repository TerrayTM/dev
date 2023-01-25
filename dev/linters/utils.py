from dev.output import output


def validate_character_limit(
    file: str, line: str, line_number: int, line_length: int,
) -> bool:
    if len(line) > line_length:
        output(
            f"File '{file}' on line {line_number} exceeds the "
            f"width limit of {line_length} characters."
        )
        return False

    return True
