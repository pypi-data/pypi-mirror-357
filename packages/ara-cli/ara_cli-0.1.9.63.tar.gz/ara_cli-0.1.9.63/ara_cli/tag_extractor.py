import os
from ara_cli.artefact_models.artefact_load import artefact_from_content


class TagExtractor:
    def __init__(self, file_system=None):
        self.file_system = file_system or os

    def extract_tags(self, navigate_to_target=False, include_classifier=None, filtered_extra_column=False):
        from ara_cli.template_manager import DirectoryNavigator
        from ara_cli.artefact_reader import ArtefactReader

        navigator = DirectoryNavigator()
        if navigate_to_target:
            navigator.navigate_to_target()

        artefacts = ArtefactReader.read_artefacts()

        if include_classifier:
            artefacts = {include_classifier: artefacts[include_classifier]}

        unique_tags = set()

        if filtered_extra_column:
            status_tags = {"to-do", "in-progress", "review", "done", "closed"}
            filtered_artefacts = []

            for artefact_list in artefacts.values():
                for artefact in artefact_list:
                    tags = artefact.tags + \
                        [artefact.status] if artefact.status else artefact.tags
                    tag_set = set(tag for tag in tags if tag is not None)
                    if not tag_set & status_tags:
                        filtered_artefacts.append(artefact)

            for artefact in filtered_artefacts:
                tags = [tag for tag in (
                    artefact.tags + [artefact.status]) if tag is not None]
                for tag in tags:
                    if (
                        tag in status_tags
                        or tag.startswith("priority_")
                        or tag.startswith("user_")
                    ):
                        continue
                    unique_tags.add(tag)

        else:
            for artefact_list in artefacts.values():
                for artefact in artefact_list:
                    user_tags = [f"user_{tag}" for tag in artefact.users]
                    tags = [tag for tag in (artefact.tags + [artefact.status] + user_tags) if tag is not None]
                    unique_tags.update(tags)

        sorted_tags = sorted(unique_tags)
        return sorted_tags
