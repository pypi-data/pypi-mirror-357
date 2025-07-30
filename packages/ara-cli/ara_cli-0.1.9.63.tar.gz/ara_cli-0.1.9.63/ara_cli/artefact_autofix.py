def read_report_file():
    file_path = "incompatible_artefacts_report.md"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        print('Artefact scan results file not found. Did you run the "ara scan" command?')
        return

    return content


def parse_report(content: str) -> dict:
    """
    Parses the incompatible artefacts report and returns structured data.
    Returns a dictionary where keys are artefact classifiers, and values are lists of (file_path, reason) tuples.
    """
    lines = content.splitlines()
    issues = {}
    current_classifier = None

    if not lines or lines[0] != "# Artefact Check Report":
        return issues  # Geçersiz rapor formatı

    if len(lines) >= 3 and lines[2] == "No problems found.":
        return issues  # Hiç sorun bulunamadı

    for line in lines[1:]:  # Başlıktan sonraki satırları işle
        line = line.strip()
        if not line:
            continue

        # Classifier başlığı tespiti (## ile başlayan)
        if line.startswith("## "):
            current_classifier = line[3:].strip()
            issues[current_classifier] = []

        # Dosya listesi tespiti (- ile başlayan)
        elif line.startswith("- ") and current_classifier is not None:
            # Format: "- `file_path`: reason"
            parts = line.split("`", 2)
            if len(parts) < 3:
                continue  # Geçersiz format

            file_path = parts[1]
            reason = parts[2].split(
                ":", 1)[1].strip() if ":" in parts[2] else ""
            issues[current_classifier].append((file_path, reason))

    return issues


def read_artefact(file_path):
    """Reads the artefact text from the given file path."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None


def determine_artefact_type_and_class(classifier):
    from ara_cli.artefact_models.artefact_mapping import artefact_type_mapping
    from ara_cli.artefact_models.artefact_model import ArtefactType

    try:
        artefact_type = ArtefactType(classifier)
    except ValueError:
        print(f"Invalid classifier: {classifier}")
        return None, None

    artefact_class = artefact_type_mapping.get(artefact_type)
    if not artefact_class:
        print(f"No artefact class found for {artefact_type}")
        return None, None

    return artefact_type, artefact_class


def construct_prompt(artefact_type, reason, file_path, artefact_text):
    from ara_cli.artefact_models.artefact_model import ArtefactType

    prompt = (
        f"Correct the following {artefact_type} artefact to fix the issue: {reason}. "
        "Provide the complete, corrected artefact. Do not reformulate the artefact, "
        "just fix the pydantic model errors, use correct grammar. "
        "Do not remove comments. "
        "You should follow the name of the file "
        f"from its path {file_path} for naming the arteafact's title. "
        "You are not allowed to use file extention in the artefact title. "
        "You are not allowed to modify, delete or add tags. "
        "User tag should be '@user_<username>'. The pydantic model already provides the '@user_' prefix. "
        "So you should be careful to not make it @user_user_<username>. "
    )

    if artefact_type == ArtefactType.task:
        prompt += (
            "For task artefacts, if the action items looks like template or empty "
            "then just delete those action items."
        )

    prompt += (
        "\nThe current artefact is:\n"
        "```\n"
        f"{artefact_text}\n"
        "```"
    )

    return prompt


def run_agent(prompt, artefact_class):
    from pydantic_ai import Agent
    # gpt-4o
    # anthropic:claude-3-7-sonnet-20250219
    agent = Agent(model="gpt-4o",
                  result_type=artefact_class, instrument=True)
    result = agent.run_sync(prompt)
    return result.data


def write_corrected_artefact(file_path, corrected_text):
    with open(file_path, 'w') as file:
        file.write(corrected_text)
    print(f"Fixed artefact at {file_path}")


def apply_autofix(file_path, classifier, reason):
    artefact_text = read_artefact(file_path)
    if artefact_text is None:
        return

    artefact_type, artefact_class = determine_artefact_type_and_class(
        classifier)
    if artefact_type is None or artefact_class is None:
        return

    prompt = construct_prompt(artefact_type, reason, file_path, artefact_text)

    try:
        corrected_artefact = run_agent(prompt, artefact_class)
        corrected_text = corrected_artefact.serialize()
        write_corrected_artefact(file_path, corrected_text)
    except Exception as e:
        print(f"Failed to fix artefact at {file_path}: {e}")
