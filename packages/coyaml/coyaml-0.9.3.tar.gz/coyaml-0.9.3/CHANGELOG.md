# Changelog

## [v0.9.3] - 2025-06-22

### Added
- Powerful template engine with `${{ action:param }}` syntax supporting `env`, `file`, `config` and `yaml` actions
- `YSettings.resolve_templates()` for recursive template evaluation
- Thread-safe `YRegistry` with URI-based factory helpers (`create_from_uri`, `create_from_uri_list`)
- Decorator `@coyaml` and metadata `YResource` for zero-boilerplate dependency injection with `typing.Annotated` support and automatic conversion to Pydantic models
- New sources: `YamlFileSource`, `EnvFileSource` (binary-safe I/O)
- Extended `YNode` API: `items()`, `values()`, rich equality and iterator support
- Almost 100 % test coverage, over 70 new tests covering edge cases and error paths

### Changed
- All file operations switched to binary mode with explicit UTF-8 decoding for robust Unicode handling
- Deep-merge logic extracted to `coyaml.utils.merge.deep_merge`
- Documentation polished and translated, quick-start rewritten
- `pyproject.toml` updated: project version, dependency bumps, stricter type-checking and lint rules

### Removed
- Legacy `_internal.deps` module (functionality superseded by `@coyaml` injection utilities)

### Fixed
- Nested and recursive template resolution edge cases
- Graceful errors for missing environment variables, files and YAML decoding problems
- Numerous minor bug fixes discovered via exhaustive test suite

## [v0.9.2] - 2025-06-14

### Added
- Added CI/CD and code coverage badges
- Added Coveralls integration

### Changed
- Improved test coverage to 100%
- Improved documentation

## [v0.9.1] - 2025-06-12

### Added
- Added documentation using MkDocs Material
- Added pymdown-extensions
- Added ReadTheDocs configuration

### Changed
- Changed documentation theme to Material
- Code refactoring
- Translated documentation to English

### Fixed
- Fixed test issues
- Fixed documentation

## [v0.1.0] - 2025-06-07

### Added
- Initial project version
- Basic project structure
- Initial documentation 