# PyPI Release Checklist

## Pre-release

- [ ] All tests passing (`./verify.sh`)
- [ ] Coverage ≥ 90%
- [ ] Documentation updated (README.md, USAGE.md)
- [ ] CHANGELOG.md updated
- [ ] Version bumped in `pyproject.toml`
- [ ] Git tag created: `git tag v0.1.0`

## Release Process

1. **Test Build Locally**

   ```bash
   uv build
   ```

2. **Test Upload to TestPyPI** (optional)

   ```bash
   uv publish --tag-index  https://test.pypi.org/simple/
   ```

3. **Create GitHub Release**

   ```bash
   git push origin v0.1.0
   ```

4. GitHub Actions will automatically:
   - Run all tests
   - Build the package
   - Publish to PyPI (if tests pass)

## Post-release

- [ ] Verify package on PyPI: https://pypi.org/project/radie-jsonui/
- [ ] Test installation: `pip install radie-jsonui`
- [ ] Update documentation if needed

## Manual Publishing (if needed)

```bash
# Build
uv build

# Publish (requires PyPI API token)
uv publish
```

## Version Numbering

Follow Semantic Versioning (https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality
- **PATCH** version for backwards-compatible bug fixes
