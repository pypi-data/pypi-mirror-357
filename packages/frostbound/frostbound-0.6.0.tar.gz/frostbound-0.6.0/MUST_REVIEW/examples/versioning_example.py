from pathlib import Path

from frostbound.versioning import GitInfo, get_git_info
from frostbound.versioning.git_info import GitInfoConfig, GitFieldSpec, GitField


def main():
    print("=== Default configuration ===")
    default_info = get_git_info()
    print(default_info.json(indent=2))
    
    print("\n=== Minimal configuration (just branch and dirty status) ===")
    minimal_config = GitInfoConfig(
        fields=[
            GitFieldSpec(
                field=GitField.BRANCH,
                command=["rev-parse", "--abbrev-ref", "HEAD"]
            ),
            GitFieldSpec(
                field=GitField.IS_DIRTY,
                command=["status", "--porcelain"],
                processor=lambda x: bool(x)
            ),
        ]
    )
    minimal_info = get_git_info(config=minimal_config)
    print(minimal_info.json(indent=2))
    
    print("\n=== Extended configuration with custom short hash length ===")
    extended_config = GitInfoConfig(
        fields=[
            GitFieldSpec(
                field=GitField.COMMIT,
                command=["rev-parse", "HEAD"]
            ),
            GitFieldSpec(
                field=GitField.SHORT_COMMIT,
                command=["rev-parse", "--short=10", "HEAD"]  # 10 chars instead of 7
            ),
            GitFieldSpec(
                field=GitField.BRANCH,
                command=["rev-parse", "--abbrev-ref", "HEAD"]
            ),
            GitFieldSpec(
                field=GitField.IS_DIRTY,
                command=["status", "--porcelain"],
                processor=lambda x: bool(x)
            ),
        ]
    )
    extended_info = get_git_info(config=extended_config)
    print(extended_info.json(indent=2))


if __name__ == "__main__":
    main()