# Link Sweep

Link Sweep is a tool for checking and cleaning dead links specifically within Markdown files for use with static site generators like Zola, Hugo, and Jekyll. Dead links have a negative impact on SEO, security and user experience.
This tool was inspired by [DeadFinder](https://github.com/hahwul/deadfinder) and designed to be more lightweight, tailored to my specific needs.

This tool is vastly more limited in scope, being designed specifically for recursively targeting markdown files within a given directory. For broader use cases, I recommend [DeadFinder](https://github.com/hahwul/deadfinder)

## Installation

### From PyPI (Recommended)

```bash
pip install link-sweep
```

### From Source

```bash
git clone https://github.com/yourusername/link-sweep.git
cd link-sweep
pip install -e .
```

## Usage

```bash
# Check links in your content directory
link-sweep check-links content/

# Check with verbose output
link-sweep check-links --verbose content/

# Check and automatically remove dead links (no back-up)
link-sweep check-links --remove-dead content/
```
When using `--remove-dead`, dead links like `[Example](https://dead-link.com)` become just `Example`.

## GitHub Actions Integration

This script was designed with the intention of running as part of GitHub Actions, however, it can be run manually. A generic workflow might look something like this:
```yaml
name: Weekly Link Cleanup

on:
  schedule:
    - cron: '0 6 * * 1'  # Monday 6 AM

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Fix dead links
      run: link-sweep check-links --remove-dead content/
    
    - name: Create PR if changes
      uses: peter-evans/create-pull-request@v5
      with:
        commit-message: "fix: automated dead link cleanup"
        title: "🔧 Weekly dead link cleanup"
```
The above runs weekly to create a pull request if there are any changes captured within the runner's local files.

## License
MIT License - see LICENSE file for details.

## Changelog

### v0.1.1
- Basic link checking functionality
- Dead link removal option
- CLI interface with Click
- Concurrency for improved perforamance
- Link timeouts