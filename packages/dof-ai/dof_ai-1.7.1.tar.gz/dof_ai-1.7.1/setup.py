"""Setup script with custom install command to show ASCII art."""

import os
import platform
import subprocess
from pathlib import Path
from setuptools import setup
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def create_alias(self):
        """Create dof-run alias for Linux and macOS."""
        system = platform.system().lower()
        
        # Define the alias command
        alias_command = 'alias dof-run="code --folder-uri vscode-remote://ssh-remote+isaac-ec2/home/ubuntu/docker/isaac-sim/documents"'
        
        if system == "linux":
            # For Linux, add to ~/.bashrc
            bashrc_path = Path.home() / ".bashrc"
            self._add_alias_to_file(bashrc_path, alias_command, "Linux")
            
        elif system == "darwin":  # macOS
            # For macOS, check for different shell configs
            shell_configs = [
                Path.home() / ".bash_profile",
                Path.home() / ".zshrc",
                Path.home() / ".bashrc"
            ]
            
            # Find the first existing config file
            config_file = None
            for config in shell_configs:
                if config.exists():
                    config_file = config
                    break
            
            if config_file:
                self._add_alias_to_file(config_file, alias_command, "macOS")
            else:
                # If no config file exists, create .zshrc (default for modern macOS)
                self._add_alias_to_file(Path.home() / ".zshrc", alias_command, "macOS")
    
    def _add_alias_to_file(self, config_file: Path, alias_command: str, system_name: str):
        """Add alias to shell configuration file."""
        try:
            # Check if alias already exists
            if config_file.exists():
                with open(config_file, 'r') as f:
                    content = f.read()
                    if 'alias dof-run=' in content:
                        print(f"✅ dof-run alias already exists in {config_file}")
                        return
            
            # Add alias to config file
            with open(config_file, 'a') as f:
                f.write(f"\n# DOF AI alias\n{alias_command}\n")
            
            print(f"✅ dof-run alias added to {config_file}")
            
            # Automatically source the config file to make alias available immediately
            try:
                # Use bash to source the file and then execute a command to verify
                result = subprocess.run(
                    ['bash', '-c', f'source {config_file} && alias dof-run'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                if 'dof-run' in result.stdout:
                    print(f"🚀 Alias is now active! You can use 'dof-run' immediately.")
                else:
                    print(f"📝 Please restart your terminal or run 'source {config_file}' to use the alias")
            except subprocess.CalledProcessError:
                print(f"📝 Please restart your terminal or run 'source {config_file}' to use the alias")
            
        except Exception as e:
            print(f"⚠️  Could not add alias to {config_file}: {e}")
            print(f"📝 Please manually add this line to your shell config:")
            print(f"   {alias_command}")

    def run(self):
        install.run(self)
        
        # Create alias
        self.create_alias()
        
        # Print ASCII art after installation
        print("""
██████╗  ██████╗ ███████╗
██╔══██╗██╔═══██╗██╔════╝
██║  ██║██║   ██║█████╗  
██║  ██║██║   ██║██╔══╝  
██████╔╝╚██████╔╝██║     
╚═════╝  ╚═════╝ ╚═╝     
LangChain for Robotics 🤖

🎉 dof-ai has been successfully installed! 🎉
""")
        print("🚀 You can now use 'dof-run' to quickly open the Isaac Sim environment!")


if __name__ == "__main__":
    setup(
        cmdclass={
            "install": PostInstallCommand,
        },
    )
