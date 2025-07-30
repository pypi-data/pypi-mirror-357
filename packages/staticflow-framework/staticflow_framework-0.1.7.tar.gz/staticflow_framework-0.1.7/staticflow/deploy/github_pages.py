"""
GitHub Pages Deployment Module for StaticFlow

This module provides functionality to deploy StaticFlow sites to GitHub Pages.
"""

import os
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import base64
from cryptography.fernet import Fernet
import datetime

from ..utils.logging import get_logger

# Получение логгера для данного модуля из централизованного модуля
logger = get_logger("deploy.github_pages")

class GitHubPagesDeployer:
    """
    Deployer class for GitHub Pages integration
    """
    
    def __init__(self, site_path: str = "output"):
        """
        Initialize the GitHub Pages deployer
        
        Args:
            site_path: Path to the built site (defaults to "public")
        """
        self.site_path = Path(site_path)
        self.config_path = Path("deploy/github_pages.json")
        self.config = self._load_config()
    
    def _get_encryption_key(self) -> bytes:
        """
        Get or generate encryption key for token encryption
        
        Returns:
            Bytes encryption key
        """
        key_file = Path("deploy/.key")
        
        # Check for environment variable first
        env_key = os.environ.get("STATICFLOW_ENCRYPTION_KEY")
        if env_key:
            try:
                return base64.urlsafe_b64decode(env_key)
            except Exception:
                pass
                
        # Use existing key file if available
        if key_file.exists():
            try:
                with open(key_file, 'rb') as f:
                    return base64.urlsafe_b64decode(f.read())
            except Exception:
                pass
        
        # Generate new key
        key = Fernet.generate_key()
        
        # Ensure directory exists
        key_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save key to file
        with open(key_file, 'wb') as f:
            f.write(base64.urlsafe_b64encode(key))
        
        # Set permissions to owner-only read/write
        try:
            import stat
            key_file.chmod(stat.S_IRUSR | stat.S_IWUSR)
        except Exception:
            pass
            
        return key
    
    def _encrypt_token(self, token: str) -> str:
        """
        Encrypt GitHub token
        
        Args:
            token: Plain token string
            
        Returns:
            Encrypted token string
        """
        if not token:
            return ""
            
        key = self._get_encryption_key()
        fernet = Fernet(key)
        return fernet.encrypt(token.encode()).decode()
    
    def _decrypt_token(self, encrypted_token: str) -> str:
        """
        Decrypt GitHub token
        
        Args:
            encrypted_token: Encrypted token string
            
        Returns:
            Plain token string
        """
        if not encrypted_token:
            return ""
            
        # Check for token in environment variables first
        env_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("STATICFLOW_GITHUB_TOKEN")
        if env_token:
            return env_token
            
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            return fernet.decrypt(encrypted_token.encode()).decode()
        except Exception:
            # If decryption fails, return empty string
            return ""
            
    def _load_config(self) -> Dict[str, Any]:
        """
        Load deployment configuration from file
        
        Returns:
            Dictionary with deployment configuration
        """
        if not self.config_path.exists():
            # Create default config
            default_config = {
                "repo_url": "",
                "branch": "gh-pages",
                "cname": "",
                "username": "",
                "email": "",
                "token": "",
                "token_encrypted": False,
                "last_deployment": None,
                "history": []
            }
            
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save default config
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
                
            return default_config
        
        # Load existing config
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
                # Handle token encryption if not already encrypted
                if config.get("token") and not config.get("token_encrypted", False):
                    config["token"] = self._encrypt_token(config["token"])
                    config["token_encrypted"] = True
                    
                return config
        except json.JSONDecodeError:
            logger.error(f"Error parsing config file {self.config_path}, using defaults")
            return {
                "repo_url": "",
                "branch": "gh-pages",
                "cname": "",
                "username": "",
                "email": "",
                "token": "",
                "token_encrypted": False,
                "last_deployment": None,
                "history": []
            }
    
    def save_config(self, config: Dict[str, Any] = None) -> None:
        """
        Save deployment configuration to file
        
        Args:
            config: Configuration to save (uses self.config if None)
        """
        if config is not None:
            self.config = config
            
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Encrypt token if it's not encrypted
        if self.config.get("token") and not self.config.get("token_encrypted", False):
            self.config["token"] = self._encrypt_token(self.config["token"])
            self.config["token_encrypted"] = True
            
        # Save configuration
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def update_config(self, **kwargs) -> None:
        """
        Update deployment configuration
        
        Args:
            **kwargs: Key-value pairs to update in the configuration
        """
        # Handle token specifically for encryption
        if "token" in kwargs and kwargs["token"]:
            # Encrypt the token
            kwargs["token"] = self._encrypt_token(kwargs["token"])
            kwargs["token_encrypted"] = True
            
        self.config.update(kwargs)
        self.save_config()
    
    def validate_config(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate the deployment configuration
        
        Returns:
            Tuple of (is_valid, error_messages, warning_messages)
        """
        errors = []
        warnings = []
        
        # Check required fields
        if not self.config.get("repo_url"):
            errors.append("Repository URL is required")
            
        if not self.config.get("username"):
            errors.append("GitHub username is required")
            
        if not self.config.get("email"):
            errors.append("Git email is required")
            
        # Validate repository URL format
        repo_url = self.config.get("repo_url", "")
        if repo_url and not (repo_url.startswith("https://github.com/") or
                              repo_url.startswith("git@github.com:")):
            errors.append("Repository URL must be a valid GitHub URL")
            
        return (len(errors) == 0, errors, warnings)
    
    def _run_command(self, command: List[str], cwd: Optional[str] = None,
                     env: Optional[Dict[str, str]] = None) -> Tuple[int, str, str]:
        """
        Run a shell command and return results
        
        Args:
            command: Command parts as list
            cwd: Working directory
            env: Environment variables
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    
    def deploy(self, commit_message: str = None) -> Tuple[bool, str]:
        """
        Deploy the site to GitHub Pages
        
        Args:
            commit_message: Optional custom commit message
            
        Returns:
            Tuple of (success, message)
        """
        logger.info("Starting GitHub Pages deployment process")
        # Validate configuration
        is_valid, errors, warnings = self.validate_config()
        if not is_valid:
            logger.error(f"Deployment aborted: Invalid configuration - {errors}")
            return False, f"Invalid configuration: {', '.join(errors)}"
        
        # Check if site exists
        if not self.site_path.exists() or not self.site_path.is_dir():
            logger.error(f"Deployment aborted: Site directory not found at {self.site_path}")
            return False, f"Site directory not found at {self.site_path}"
        
        # Extract config values
        repo_url = self.config["repo_url"]
        branch = self.config["branch"]
        username = self.config["username"]
        email = self.config["email"]
        cname = self.config.get("cname", "")
        
        logger.info(f"Deploying to repository: {repo_url} (branch: {branch})")
        logger.info(f"Using git identity: {username} <{email}>")
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            logger.info(f"Created temporary directory for deployment: {temp_dir}")
            
            # Set up git environment
            git_env = os.environ.copy()
            git_env["GIT_AUTHOR_NAME"] = username
            git_env["GIT_AUTHOR_EMAIL"] = email
            git_env["GIT_COMMITTER_NAME"] = username
            git_env["GIT_COMMITTER_EMAIL"] = email
            
            # If we have a token, use HTTPS with credentials
            has_token = False
            if self.config.get("token"):
                logger.info("Found GitHub token, will use for authentication")
                has_token = True
                # Decrypt the token if it's encrypted
                token = self.config["token"]
                if self.config.get("token_encrypted", False):
                    token = self._decrypt_token(token)
                
                # Convert SSH URL to HTTPS with token if needed
                if repo_url.startswith("git@github.com:"):
                    repo_path = repo_url.split("git@github.com:")[1]
                    repo_url = f"https://{username}:{token}@github.com/{repo_path}"
                elif repo_url.startswith("https://github.com/"):
                    repo_path = repo_url.split("https://github.com/")[1]
                    repo_url = f"https://{username}:{token}@github.com/{repo_path}"
            else:
                logger.info("No GitHub token provided, using standard authentication")
            
            # Initialize git repo
            logger.info("Initializing git repository")
            code, out, err = self._run_command(
                ["git", "init"],
                cwd=temp_dir,
                env=git_env
            )
            if code != 0:
                logger.error(f"Failed to initialize git repository: {err}")
                return False, f"Failed to initialize git repository: {err}"
            
            # Set remote
            log_url = repo_url.replace(token, '***') if has_token else repo_url
            logger.info(f"Setting remote origin to: {log_url}")
            code, out, err = self._run_command(
                ["git", "remote", "add", "origin", repo_url],
                cwd=temp_dir,
                env=git_env
            )
            if code != 0:
                logger.error(f"Failed to set git remote: {err}")
                return False, f"Failed to set git remote: {err}"
                
            # Configure git
            logger.info("Configuring git identity")
            self._run_command(
                ["git", "config", "user.name", username],
                cwd=temp_dir,
                env=git_env
            )
            
            self._run_command(
                ["git", "config", "user.email", email],
                cwd=temp_dir,
                env=git_env
            )
            
            # Try to fetch the branch if it exists
            logger.info(f"Checking if branch '{branch}' exists")
            branch_exists = False
            code, out, err = self._run_command(
                ["git", "fetch", "origin", branch],
                cwd=temp_dir,
                env=git_env
            )
            if code == 0:
                # Branch exists, check it out
                logger.info(f"Branch '{branch}' exists, checking it out")
                code, out, err = self._run_command(
                    ["git", "checkout", "-b", branch, f"origin/{branch}"],
                    cwd=temp_dir,
                    env=git_env
                )
                if code == 0:
                    branch_exists = True
            
            if not branch_exists:
                # Create a new branch
                logger.info(f"Creating new branch '{branch}'")
                self._run_command(
                    ["git", "checkout", "--orphan", branch],
                    cwd=temp_dir,
                    env=git_env
                )
            
            # Clean the working directory
            logger.info("Cleaning working directory")
            for item in temp_path.iterdir():
                if item.name == ".git":
                    continue
                    
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

            logger.info(f"Copying site content from {self.site_path} to the repository")
            repo_name = None
            if self.config.get("repo_url"):
                repo_name = self.config["repo_url"].rstrip("/").split("/")[-1]
                if repo_name.endswith('.git'):
                    repo_name = repo_name[:-4]
            output_items = list(self.site_path.iterdir())

            def should_copy(item):
                return item.name != "admin"
            if repo_name and len(output_items) == 1 and output_items[0].is_dir() and output_items[0].name == repo_name:
                # Если output содержит только папку с именем репозитория, копируем её содержимое (кроме admin)
                for item in output_items[0].iterdir():
                    if not should_copy(item):
                        continue
                    if item.is_dir():
                        shutil.copytree(
                            item,
                            temp_path / item.name,
                            dirs_exist_ok=True
                        )
                    else:
                        shutil.copy2(item, temp_path / item.name)
            else:
                for item in output_items:
                    if not should_copy(item):
                        continue
                    if item.is_dir():
                        shutil.copytree(
                            item,
                            temp_path / item.name,
                            dirs_exist_ok=True
                        )
                    else:
                        shutil.copy2(item, temp_path / item.name)
            # --- END PATCH ---
            
            # Create CNAME file if specified
            if cname:
                logger.info(f"Creating CNAME file with domain: {cname}")
                cname_path = temp_path / "CNAME"
                with open(cname_path, "w") as f:
                    f.write(cname)
            
            # Add all files
            logger.info("Adding files to git")
            code, out, err = self._run_command(
                ["git", "add", "."],
                cwd=temp_dir,
                env=git_env
            )
            if code != 0:
                logger.error(f"Failed to add files to git: {err}")
                return False, f"Failed to add files to git: {err}"
            
            # Check if there are changes
            logger.info("Checking for changes")
            code, out, err = self._run_command(
                ["git", "status", "--porcelain"],
                cwd=temp_dir,
                env=git_env
            )
            
            if not out.strip():
                # No changes to commit
                logger.info("No changes to deploy, skipping")
                return True, "No changes to deploy"
            
            # Commit changes
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Use custom commit message if provided, otherwise use default
            if not commit_message:
                commit_message = f"Deployed at {timestamp}"
                
            logger.info(f"Committing changes with message: '{commit_message}'")
            code, out, err = self._run_command(
                ["git", "commit", "-m", commit_message],
                cwd=temp_dir,
                env=git_env
            )
            if code != 0:
                logger.error(f"Failed to commit changes: {err}")
                return False, f"Failed to commit changes: {err}"
            
            # Push to remote
            logger.info(f"Pushing to GitHub (branch: {branch})")
            code, out, err = self._run_command(
                ["git", "push", "-u", "origin", branch],
                cwd=temp_dir,
                env=git_env
            )
            if code != 0:
                logger.error(f"Failed to push to GitHub: {err}")
                return False, f"Failed to push to GitHub: {err}"
            
            # Update deployment history
            logger.info("Updating deployment history")
            self.config.setdefault("history", [])
            self.config["history"].insert(0, {
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "success"
            })
            
            # Limit history to 10 entries
            if len(self.config["history"]) > 10:
                self.config["history"] = self.config["history"][:10]
                
            self.config["last_deployment"] = datetime.datetime.now().isoformat()
            self.save_config()
            
            logger.info("GitHub Pages deployment completed successfully")
            return True, "Successfully deployed to GitHub Pages"
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """
        Get the current deployment status
        
        Returns:
            Dictionary with deployment status
        """
        return {
            "configured": bool(self.config.get("repo_url")),
            "last_deployment": self.config.get("last_deployment"),
            "history": self.config.get("history", []),
            "config": {
                "repo_url": self.config.get("repo_url", ""),
                "branch": self.config.get("branch", "gh-pages"),
                "cname": self.config.get("cname", ""),
                "username": self.config.get("username", ""),
                "email": self.config.get("email", ""),
                # Don't expose the token
                "has_token": bool(self.config.get("token"))
            }
        } 