"""Every module under `implementations/` must import cleanly from the repository root.

This is the regression guard for the import layout: the package is `implementations.*`,
so intra-package imports have to be absolute (`from implementations.<pkg>.<mod> import ...`).
Bare imports such as `from table_lookup import ...` happen to work inside a notebook whose
kernel starts in that directory, and fail everywhere else — which is how several modules
ended up unimportable.
"""
import importlib
import pkgutil
import unittest

from tests.sim_utils import _REPO_ROOT  # noqa: F401  (inserts the repo root into sys.path)

import implementations


def _iter_module_names():
    """Yields the dotted name of every module under the `implementations` package."""
    for module_info in pkgutil.walk_packages(
        implementations.__path__, prefix="implementations."
    ):
        yield module_info.name


class TestImports(unittest.TestCase):

    def test_package_is_discoverable(self):
        names = list(_iter_module_names())
        self.assertGreater(len(names), 20, "package walk found suspiciously few modules")

    def test_every_module_imports(self):
        failures = []
        for name in _iter_module_names():
            try:
                importlib.import_module(name)
            except Exception as exc:  # noqa: BLE001 - we want to report every failure
                failures.append(f"{name}: {type(exc).__name__}: {exc}")
        self.assertEqual(failures, [], "modules failed to import:\n" + "\n".join(failures))

    def test_no_missing_init_files(self):
        """Every directory on the path down to a module needs __init__.py.

        A missing one still imports, as an implicit namespace package, but the directory
        becomes invisible to `pkgutil.walk_packages` and to packaging tools — which is how
        the whole `arithmetic_operations` subtree was silently skipped by this very test
        when it only checked the directories holding the .py files.
        """
        package_root = _REPO_ROOT / "implementations"
        missing = set()
        for path in package_root.rglob("*.py"):
            if path.name == "__init__.py" or "__pycache__" in path.parts:
                continue
            directory = path.parent
            while True:
                if not (directory / "__init__.py").exists():
                    missing.add(str(directory.relative_to(_REPO_ROOT)))
                if directory == package_root:
                    break
                directory = directory.parent
        self.assertEqual(sorted(missing), [], "directories missing __init__.py")


if __name__ == "__main__":
    unittest.main()
