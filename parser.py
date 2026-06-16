def split_diff_by_file(diff_text: str):
    files = {}
    current_file = None
    buffer = []

    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            if current_file:
                files[current_file] = "\n".join(buffer)
                buffer = []

            parts = line.split(" ")
            current_file = parts[2][2:]  # a/filename
        else:
            buffer.append(line)

    if current_file:
        files[current_file] = "\n".join(buffer)

    return files