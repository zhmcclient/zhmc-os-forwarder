Dev: Automatically update AUTHORS.md when building the distribution archives.
The update is tolerant when 'git shortlog' does not show any authors - it then
issues a warning and leaves the existing file unchanged.
