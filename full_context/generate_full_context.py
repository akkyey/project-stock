import datetime
import glob
import os
import shutil
import subprocess


def is_git_tracked(filepath):
    """Check if file is tracked by git, handling nested repositories."""
    try:
        # 1. Find the closest .git directory
        current_dir = os.path.dirname(os.path.abspath(filepath))
        git_root = None
        while current_dir != os.path.dirname(current_dir):  # Stop at root
            if os.path.isdir(os.path.join(current_dir, ".git")):
                git_root = current_dir
                break
            current_dir = os.path.dirname(current_dir)
        
        if not git_root:
            # Fallback to current script's project root if no specific git root found
            # (Though if we are not in a git repo at all, likely not tracked)
            return False

        # 2. Check strict with git ls-files from that root
        rel_path = os.path.relpath(filepath, git_root)
        res = subprocess.run(
            ["git", "ls-files", rel_path],
            capture_output=True,
            text=True,
            cwd=git_root
        )
        return bool(res.stdout.strip())
    except Exception:
        return False


def generate_full_context():
    # Define root path (parent of this script's directory)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    # Generate timestamped filename
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    output_filename = f"{today}_project_full_context.md"
    output_path = os.path.join(current_dir, output_filename)

    content_list = []

    # 1. Header & Project Structure
    content_list.append("# Project Full Context Report\n\n")
    content_list.append(
        f"Generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    )

    # Define file patterns relative to project root
    def get_files(pattern):
        # Allow recursive glob if needed, but strict groups preferred
        return sorted(glob.glob(os.path.join(project_root, pattern)))

    file_groups = [
        ("Documentation", ["README.md", "GEMINI.md"] + get_files("docs/*.md")),
        ("Proposals (Active)", get_files("docs/proposal/*.md")),
        (
            "Configuration",
            [
                os.path.join(project_root, "stock-analyzer4/config/config.yaml"),
                os.path.join(project_root, "stock-analyzer4/config/ai_prompts.yaml"),
                os.path.join(project_root, "stock-analyzer4/requirements.txt"),
            ],
        ),
        ("Root Scripts", get_files("*.py")),
        ("Stock Analyzer Scripts", get_files("stock-analyzer4/*.py")),
        (
            "Source Code (src)",
            get_files("stock-analyzer4/src/*.py") + get_files("stock-analyzer4/src/**/*.py"),
        ),  # Recursive for src submodules
        # [v2.2] Slimming & Critical Context
        ("History (Latest 3)", sorted(get_files("history/*.md"), reverse=True)[:3]),
        (
            "Trouble Reports (Latest 1)",
            sorted(get_files("trouble/*.md"), reverse=True)[:1],
        ),
    ]

    # [v2.1] Broad Exclusion for Slimming
    exclude_filenames = {
        "generate_full_context.py",
        "self_diagnostic.py",
        "antigravity_runner.py",
        "manual_runner.md",
        "manual_runner_ja.md",
        "code_review_report.md",
        "refactoring_plan.md",
        "verification_report_20251221.md",
        "full_workflow_verification_report.md",
        "full_workflow_verification_report_v61.md",
        "full_workflow_verification_report_v71.md",
        "equity_auditor_verification_report.md",
        "prompt_enhancement_report.md",
        "refactoring_completion_report.md",
        "manual.md",  # manual_ja.md があるため英語版を除外
        "architecture.md",  # architecture_ja.md があるため英語版を除外
    }

    # Explicit exclusions for tests and temporary files
    def is_redundant_file(fpath):
        fname = os.path.basename(fpath)
        fpath_norm = fpath.replace(os.sep, "/")
        # Tests
        if fname.startswith("test_") or fname.endswith("_test.py"):
            return True
        if "/tests/" in fpath_norm:
            return True
        # Temporary DBs
        if "test_provider" in fname and fname.endswith(".db"):
            return True
        if "test_stock_" in fname and fname.endswith(".db"):
            return True
        # Coverage
        if "/htmlcov/" in fpath_norm:
            return True
        # Tools (Legacy/Archive)
        if "/tools/" in fpath_norm:
            return True
        # Archives
        if "/archive/" in fpath_norm:
            return True
        return False

    for group_name, files in file_groups:
        content_list.append(f"## {group_name}\n\n")

        filtered_files = []
        for f in files:
            # 1. Exist Check
            if not os.path.exists(f):
                continue

            # 2. Filename Exclusion
            if os.path.basename(f) in exclude_filenames:
                continue

            # 3. Redundant/Test Exclusion
            if is_redundant_file(f):
                continue

            # 4. Git Tracked Check
            if not is_git_tracked(f):
                # print(f"Skipping untracked file: {os.path.basename(f)}")
                continue

            filtered_files.append(f)

        # Uniquify list (glob overlap protection)
        filtered_files = sorted(list(set(filtered_files)))

        if not filtered_files:
            content_list.append("_No files found in this group._\n\n")
            continue

        for filepath in filtered_files:
            rel_display_path = os.path.relpath(filepath, project_root)
            content_list.append(f"### {rel_display_path}\n\n")

            ext = os.path.splitext(filepath)[1]
            lang = "text"
            if ext == ".py":
                lang = "python"
            elif ext in [".yaml", ".yml"]:
                lang = "yaml"
            elif ext == ".md":
                lang = "markdown"
            elif ext == ".sh":
                lang = "bash"

            content_list.append(f"```{lang}\n")
            try:
                with open(filepath, "r", encoding="utf-8") as infile:
                    content_list.append(infile.read())
            except Exception as e:
                content_list.append(f"Error reading file: {e}")
            content_list.append("\n```\n\n")
            content_list.append("---\n\n")

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.writelines(content_list)

    print(f"✅ Full Context Generated: {output_path}")

    # Validation
    validate_generated_file(output_path)

    # Archive old context files
    archive_dir = os.path.join(current_dir, "archive")
    os.makedirs(archive_dir, exist_ok=True)

    old_files = glob.glob(os.path.join(current_dir, "*_project_full_context.md"))
    for f in old_files:
        if os.path.basename(f) != output_filename:
            try:
                shutil.move(f, os.path.join(archive_dir, os.path.basename(f)))
                print(f"📦 Archived: {os.path.basename(f)}")
            except Exception as e:
                print(f"⚠️ Failed to archive {os.path.basename(f)}: {e}")


def validate_generated_file(filepath):
    """Verify that the generated context file is valid."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ Validation Failed: File not found: {filepath}")

    # 1. Size Check
    size = os.path.getsize(filepath)
    if size < 1024:
        raise ValueError(f"❌ Validation Failed: File too small ({size} bytes)")

    # 2. Content Check
    required_headers = [
        "# Project Full Context Report",
        "## Documentation",
        "## Source Code (src)",
    ]

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    missing = [h for h in required_headers if h not in content]
    if missing:
        raise ValueError(f"❌ Validation Failed: Missing required headers: {missing}")

    print(f"✨ Validation Passed: Size={size/1024:.1f}KB, Headers=OK")


if __name__ == "__main__":
    generate_full_context()
