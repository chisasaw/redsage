import os
import git
from typing import Optional, List


class GitManager:
    """
    Manage Git operations for RedSage, such as branching, committing, and change tracking. 
    """
    def __init__(self, config):
        """
        Initialize GitManager with configuration settings.

        :param config: Configuration object with repository path and branch prefix.
        """
        self.base_path = config.get('repo_path', '.')
        self.branch_prefix = config.get('branch_prefix', 'redsage/')
        
        try:
            self.repo = git.Repo(self.base_path, search_parent_directories=True)
        except git.exc.InvalidGitRepositoryError:
            raise ValueError(f"Not a valid Git repository at {self.base_path}")

    def create_branch(self, branch_name: Optional[str] = None) -> str:
        """
        Create a new branch with a name based on the configuration or input.

        :param branch_name: Optional branch name to create.
        :return: The name of the newly created branch.
        """
        if not branch_name:
            from datetime import datetime
            branch_name = f"{self.branch_prefix}{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not branch_name.startswith(self.branch_prefix):
            branch_name = f"{self.branch_prefix}{branch_name}"
        
        new_branch = self.repo.create_head(branch_name)
        new_branch.checkout()
        return branch_name

    def commit_changes(self, message: str = "RedSage: Auto-generated changes") -> bool:
        """
        Commit all staged changes in the repository.

        :param message: Commit message to use.
        :return: True if commit succeeded, False if no changes to commit.
        """
        self.repo.git.add(update=True)
        if not self.repo.index.diff(self.repo.head.commit):
            return False
        
        self.repo.index.commit(message)
        return True

    def get_branch_changes(self) -> List[str]:
        """
        Get the list of files changed in the current branch.

        :return: List of file paths.
        """
        try:
            diff = self.repo.git.diff('--name-only')
            return diff.split('\n') if diff else []
        except Exception:
            return []

    def checkout_branch(self, branch_name: str) -> bool:
        """
        Checkout a specific branch.

        :param branch_name: Name of the branch to switch to.
        :return: True if successful, False otherwise.
        """
        try:
            branch = self.repo.branches[branch_name]
            branch.checkout()
            return True
        except (IndexError, TypeError):
            return False

    def list_redsage_branches(self) -> List[str]:
        """
        List all branches created by RedSage.

        :return: List of branch names.
        """
        return [branch.name for branch in self.repo.branches if branch.name.startswith(self.branch_prefix)]

    def undo_last_change(self) -> bool:
        """
        Undo the last commit in the repository.

        :return: True if successful, False otherwise.
        """
        try:
            self.repo.git.reset('HEAD~1', mixed=True)
            return True
        except Exception:
            return False
