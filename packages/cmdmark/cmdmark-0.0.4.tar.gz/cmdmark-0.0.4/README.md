# cmdmark

A CLI tool for managing commands like bookmarks. This Python script provides a simple way to manage and execute frequently used commands via YAML configuration files. Think of it like a bookmark manager, but for your terminal commands.

## Features

*   **Categorized Commands:** Organize your commands into categories stored in subfolders.
*   **YAML Configuration:** Define commands and their descriptions in easy-to-read YAML files.
*   **Interactive Selection:** Choose categories, files, and commands interactively from the terminal.
*   **Direct Execution:** Execute selected commands directly within the script.
*   **Git-Aware:** Git metadata files (e.g., `.git` folders) are ignored when listing categories and YAML files.


## Setup

1.  **Installation:**

    The preferred way to install `cmdmark` is via pipx (recommended) or pip:
    ```bash
    pipx install cmdmark # recommended way.
    # OR
    pip install cmdmark
    ```
    This will install `cmdmark` and its dependency, `PyYAML`. This project requires Python 3.12 or higher.

2.  **Configuration Directory:** The script uses a configuration directory located at `~/.command_bookmarks`. Make sure that the directory exists. You may create some sub-directories in `~/.command_bookmarks` to categorize your commands, and create yml files to store the relative commands.

3.  **YAML Files:** Create YAML files within the configuration directory (or its subdirectories) to define your commands.  The structure of the YAML file is as follows:

    ```yaml
    commands:
      alias1:
        command: "your_command_here"
        description: "A short description of the command"
      alias2:
        command: "another_command"
        description: "Another description"
    ```

    *   `commands`: The top-level key.
    *   `alias1`, `alias2`, etc.:  Short, user-friendly aliases for your commands.  These are displayed in the selection menu.
    *   `command`: The actual command to be executed.
    *   `description`:  (Optional) A brief description of the command.

## Usage

1.  **Run the script:**

    ```bash
    cmdmark
    ```

2.  **Interactive Navigation:**

    *   The script will first list the available categories (subfolders) within `~/.command_bookmarks`.
    *   Select a category by entering its number.
    *   The script will then list the YAML files within the selected category.
    *   Select a YAML file by entering its number.
    *   Finally, the script will list the commands defined in the selected YAML file, displaying the alias, the full command and short description.
    *   Select a command by entering its number.

3.  **Command Execution:** The selected command will be executed in your terminal.

## Example

Let's say you have the following structure (see tests/samples).