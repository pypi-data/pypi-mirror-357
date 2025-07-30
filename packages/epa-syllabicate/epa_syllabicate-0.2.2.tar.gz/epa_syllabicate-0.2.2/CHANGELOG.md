# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


### Added
- Initial release of epa_syllabicate module
- Basic syllabification functionality
- Test suite with pytest
- Project configuration with pyproject.toml
## v0.2.2 (2025-06-24)

### Fix

- workflows fix

## v0.2.1 (2025-06-24)

### Fix

- **.github/workflows/release.yml**: fixes issues in release

## v0.2.0 (2025-06-24)

### Feat

- adds github workflow for publishing to pypi (#7)
- integrate klow-e syllabicate with corpus tests
- **Makefile**: adds a Makefile with installation and tests (#4)
- Implements a syllabifier using lark module
- create a python project boilerplate with python3.8 (#1)

### Fix

- empty case and Makefile improvements(#5)
- minors and black over the code
