from pathlib import Path

def detect_language_from_path(path: Path) -> str:
    """
    Heuristically detect the language or framework of a file or project path.

    Args:
        path (Path): A file path or root directory

    Returns:
        str: Detected language string (e.g., "python", "react", "java", "c", "cpp")
    """
    if path.is_file():
        suffix = path.suffix.lower()
        if suffix == ".py":
            return "python"
        elif suffix in {".js", ".jsx", ".tsx"}:
            return "react"
        elif suffix == ".java":
            return "java"
        elif suffix == ".c":
            return "c"
        elif suffix == ".cpp":
            return "cpp"

    
    elif path.is_dir():
        all_files = list(path.rglob("*"))
        file_names = {f.name.lower() for f in all_files if f.is_file()}
        suffixes = {f.suffix.lower() for f in all_files if f.is_file()}

        # React: presence of package.json or index.jsx/tsx/js
        if "package.json" in file_names:
            return "react"
        if any(name in file_names for name in {"index.js", "index.jsx", "app.jsx", "main.tsx"}):
            return "react"
        if any(s in suffixes for s in {".jsx", ".tsx", ".js"}):
            return "react"

        # Java
        if any(f.name.endswith(".java") for f in all_files):
            return "java"
        if any("Main.java" in f.name for f in all_files):
            return "java"

        # C/C++
        if ".cpp" in suffixes:
            return "cpp"
        if ".c" in suffixes:
            return "c"

        # Python
        if ".py" in suffixes:
            return "python"

    return "python"  

def infer_repo_language(repomap: dict[str, dict[str, str]]) -> str:
    """
    Infers the dominant programming language used in the repository based on repomap.

    Returns:
        str: Language with highest number of files.
    """
    lang_count: dict[str, int] = {}

    for _, data in repomap.items():
        lang = str(data.get("language", "plaintext")).lower()
        lang_count[lang] = lang_count.get(lang, 0) + 1

    if not lang_count:
        return "plaintext"

    # Return most common language
    return max(lang_count.items(), key=lambda x: x[1])[0]

