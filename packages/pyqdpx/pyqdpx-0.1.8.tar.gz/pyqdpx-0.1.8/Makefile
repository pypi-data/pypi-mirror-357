# Makefile for Release Automation

.PHONY: release-patch release-minor release-major check-clean build-package push-git upload-pypi clean-local help _release

# Define colors for better terminal output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Default action if just 'make' is run
all: help

# Display help information for the Makefile targets
help:
	@echo "$(YELLOW)Release Automation Help$(NC)"
	@echo "$(YELLOW)-----------------------------------$(NC)"
	@echo "  $(GREEN)make release-patch$(NC)   - Create and push a new patch release to PyPI."
	@echo "  $(GREEN)make release-minor$(NC)   - Create and push a new minor release to PyPI."
	@echo "  $(GREEN)make release-major$(NC)   - Create and push a new major release to PyPI."
	@echo ""
	@echo "  $(GREEN)make check-clean$(NC)   - Checks if the Git repository is clean."
	@echo "  $(GREEN)make build-package$(NC) - Cleans existing builds and builds the package."
	@echo "  $(GREEN)make push-git$(NC)      - Pushes commits and tags to origin."
	@echo "  $(GREEN)make upload-pypi$(NC)   - Uploads built packages to PyPI."
	@echo "  $(GREEN)make clean-local$(NC)   - Cleans local build artifacts (dist/, build/, _version.py)."
	@echo ""
	@echo "$(YELLOW)NOTE: Before running any release target:$(NC)"
	@echo "$(YELLOW)  1. Ensure you have configured Twine credentials (twine register / twine upload --repository testpypi).$(NC)"
	@echo "$(YELLOW)  2. Ensure you have 'setuptools_scm', 'build', 'twine', and 'bump2version' installed in your environment (pip install -r requirements-dev.txt).$(NC)"
	@echo "$(YELLOW)  3. Your '.bumpversion.cfg' must have 'current_version' set to your latest released version.$(NC)"
	@echo "$(YELLOW)  4. Ensure your default branch is 'main' or 'master' for 'push-git' to work as expected.$(NC)"


# Target for a patch release.
release-patch: test check-clean
	@echo "$(GREEN)>>> Initiating Patch Release <<<\n$(NC)"
	bump2version patch # This bumps the version, creates a commit, and tags it
	$(MAKE) _release

# Target for a minor release.
release-minor: test check-clean
	@echo "$(GREEN)>>> Initiating Minor Release <<<\n$(NC)"
	bump2version minor
	$(MAKE) _release

# Target for a major release.
release-major: test check-clean
	@echo "$(GREEN)>>> Initiating Major Release <<<\n$(NC)"
	bump2version major
	$(MAKE) _release

# Common steps executed after a version bump (by bump2version)
# and after it has been verified that unit test are passed and the repository is clean.
_release: clean-local build-package push-git upload-pypi
	@echo "$(GREEN)>>> Release process complete! <<<\n$(NC)"

# Checks if the Git repository is clean.
# Exits with an error message if there are uncommitted changes or untracked files.
check-clean:
	@echo "$(YELLOW)>>> Checking Git repository cleanliness...$(NC)"
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "$(RED)Error: Git repository is not clean. Please commit or stash your changes before releasing.$(NC)"; \
		git status; \
		exit 1; \
	fi
	@echo "$(GREEN)Git repository is clean.$(NC)"

build-package:
	@echo "$(YELLOW)>>> Building package...$(NC)"
	# This command creates the sdist (source distribution) and wheel (binary distribution) in the 'dist/' directory.
	python -m build
	@echo "$(GREEN)Package built successfully!$(NC)"

push-git:
	@echo "$(YELLOW)>>> Pushing commits and tags to remote Git repository...$(NC)"
	# Attempt to push to 'main', if it fails, try 'master'. This provides flexibility.
	git push origin main || echo "$(YELLOW)Warning: Could not push to 'main' branch.$(NC)"
	# Push all new tags. bump2version creates a tag for the new release.
	git push origin --tags
	@echo "$(GREEN)Pushed to Git successfully!$(NC)"

# Uploads the built packages from the 'dist/' directory to PyPI.
upload-pypi:
	@echo "$(YELLOW)>>> Uploading package to PyPI...$(NC)"
	# twine upload --repository testpypi dist/* # Use this for testing on TestPyPI
	twine upload dist/*
	@echo "$(GREEN)Package uploaded to PyPI successfully!$(NC)"

# Cleans up local build-related artifacts.
clean-local:
	@echo "$(YELLOW)>>> Cleaning local build artifacts...$(NC)"
	rm -rf dist/ build/ *.egg-info/
	rm -f pyqdpx/_version.py || true
	@echo "$(GREEN)Local artifacts cleaned.$(NC)"

# Runs all pytest unit tests.
# This ensures that the newly bumped version's code passes all tests before proceeding with the release.
test:
	@echo "$(YELLOW)>>> Running pytest unit tests...$(NC)"
	pytest
	@echo "$(GREEN)All tests passed!$(NC)"
