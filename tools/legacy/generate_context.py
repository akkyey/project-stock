import glob
import os


def generate_context(output_file="project_context.md"):
    files_to_include = [
        # Documentation
        "docs/architecture_ja.md",
        "docs/manual_ja.md",
        "docs/manual_main_ja.md",
        "docs/manual_runner_ja.md",
        "docs/testing_manual_ja.md",
        # Config
        "config.yaml",
        "requirements.txt",
        # Root Scripts
        "analyze.py",
        "manual_runner.py",
        "self_diagnostic.py",
    ]

    # Add all src files
    src_files = glob.glob("src/*.py")
    files_to_include.extend(src_files)

    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write("# Project Context\n\n")
        outfile.write(
            "This document contains the consolidated source code and documentation for the Stock Analyzer project.\n\n"
        )
        outfile.write("---\n\n")

        for filepath in files_to_include:
            if os.path.exists(filepath):
                outfile.write(f"## File: {filepath}\n\n")

                # Determine language for code block
                ext = os.path.splitext(filepath)[1]
                lang = ""
                if ext == ".py":
                    lang = "python"
                elif ext in [".yaml", ".yml"]:
                    lang = "yaml"
                elif ext == ".md":
                    lang = "markdown"

                outfile.write(f"```{lang}\n")

                try:
                    with open(filepath, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"Error reading file: {e}")

                outfile.write("\n```\n\n")
                outfile.write("---\n\n")
            else:
                print(f"Warning: File not found: {filepath}")

    print(f"✅ Generated {output_file}")


if __name__ == "__main__":
    generate_context()
