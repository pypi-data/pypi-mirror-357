import re
from typing import Dict, List, Optional
from adapters.adapter import LanguageModelAdapter
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern
from schemas import FileChangeSummary, ChangeSummary


class CommitMessageGenerator:
    def __init__(self, adapter: LanguageModelAdapter):
        self.adapter = adapter

    def _format_key_changes(self, key_changes: Dict[str, List[str]]) -> str:
        return '\n'.join(
            f"{filename}:\n" + "\n".join(f"- {change}" for change in changes[:3])
            for filename, changes in key_changes.items()
        )

    def summarize_diff(self, diff: str) -> Dict[str, FileChangeSummary]:
        files_changed: Dict[str, FileChangeSummary] = {}
        current_file = None

        for line in diff.splitlines():
            if line.startswith('diff --git'):
                parts = line.split()
                if len(parts) >= 4:
                    current_file = parts[-1].lstrip('b/')
                    files_changed[current_file] = FileChangeSummary(
                        additions=0,
                        deletions=0,
                        file_type=current_file.split('.')[-1] if '.' in current_file else 'unknown',
                        important_changes=[]
                    )
            elif current_file:
                if line.startswith('+') and not line.startswith('+++'):
                    files_changed[current_file]['additions'] += 1
                    if re.match(r'^\+\s*(def|class|import|from|function|const|let|var|type|interface)', line):
                        clean = line.lstrip('+').strip()
                        files_changed[current_file]['important_changes'].append(clean)
                elif line.startswith('-') and not line.startswith('---'):
                    files_changed[current_file]['deletions'] += 1

        return files_changed

    def get_gitignore_spec(self, gitignore_content: str) -> PathSpec:
        return PathSpec.from_lines(GitWildMatchPattern, gitignore_content.splitlines())

    def is_important_file(self, filename: str, gitignore_spec: Optional[PathSpec]) -> bool:
        if gitignore_spec and gitignore_spec.match_file(filename):
            return False

        ignore_patterns = [
            r'\.lock$', r'\.log$', r'\.map$', r'\.min\.',
            r'package-lock\.json$', r'yarn\.lock$',
            r'\.git/', r'node_modules/', r'vendor/',
        ]

        return not any(re.search(pattern, filename) for pattern in ignore_patterns)

    def clean_diff(self, diff: str, max_lines: int = 100) -> str:
        diff = re.sub(r'diff --git.*\nBinary files.*\n', '', diff)
        lines = diff.splitlines()
        return '\n'.join(lines[:max_lines]) + ("\n... (truncated)" if len(lines) > max_lines else '')

    def generate_commit_message(
        self,
        diff: str,
        branch_name: Optional[str] = None,
        ticket_number: Optional[str] = None,
        gitignore_content: Optional[str] = None
    ) -> str:
        cleaned_diff = self.clean_diff(diff)
        changes = self.summarize_diff(cleaned_diff)
        gitignore_spec = self.get_gitignore_spec(gitignore_content) if gitignore_content else None

        important_changes = {
            filename: info
            for filename, info in changes.items()
            if self.is_important_file(filename, gitignore_spec)
        }

        summary = ChangeSummary(
            total_files=len(changes),
            total_additions=sum(f['additions'] for f in changes.values()),
            total_deletions=sum(f['deletions'] for f in changes.values()),
            file_types=set(f['file_type'] for f in changes.values()),
            important_files=list(important_changes.keys()),
            key_changes={
                filename: info['important_changes']
                for filename, info in important_changes.items()
                if info['important_changes']
            }
        )

        formatted_changes = self._format_key_changes(summary['key_changes'])

        prompt = f"""
Analyze the following code changes and respond with a single-line commit message using the Conventional Commits format.

Only respond with one line. Do not include body or footer. Focus on the main purpose of the change.

Allowed types: feat, fix, chore, docs, style, refactor, perf, test

Examples:
- feat(api): add user auth middleware
- fix(ui): resolve null crash on load
- refactor: simplify route handling

Changes:
{formatted_changes or 'No key changes detected.'}
"""

        return self.adapter.send_message(prompt.strip())
