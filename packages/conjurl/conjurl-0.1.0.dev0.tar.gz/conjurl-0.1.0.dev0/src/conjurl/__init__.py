import sys
import logging
import importlib.abc
import importlib.machinery
import importlib.util
import subprocess
import types
import tempfile

logger = logging.getLogger(__name__)


def _download_and_install(owner, repo):
    # N.B. Ensure `com` object has the `<owner>` attribute
    setattr(github.com, owner, (importlib.import_module("conjurl.github.com." + owner)))

    vcs_req = f"git+https://github.com/{owner}/{repo}"
    tmpdir = tempfile.mkdtemp(prefix=f"github_{owner}_{repo}_")

    # @TODO: Suppress stdout/stderr
    subprocess.check_call(
        [
            "uv",
            "pip",
            "install",
            vcs_req,
            "--target",
            tmpdir,
            "--python",
            sys.executable,
        ]
    )
    sys.path.append(tmpdir)


class _MPF(importlib.abc.MetaPathFinder):
    """MetaPathFinder that intercepts imports like 'import conjurl.github.com.<...> as <...>'"""

    def _make_namespace_package(self, fullname):
        """Create a namespace package spec for the given fullname."""
        return importlib.machinery.ModuleSpec(
            fullname,
            None,  # No loader for namespace packages
            origin="<synthetic conjurl namespace>",
            is_package=True,
        )

    def find_spec(self, fullname, path, target=None):
        logger.debug(f"_MPF: Looking for spec for {fullname}")

        if not fullname.startswith("conjurl."):
            return None

        try:
            owner, repo = fullname.split(".")[3:5]
        except ValueError:
            return self._make_namespace_package(fullname)

        _download_and_install(owner, repo)
        return importlib.util.find_spec(repo)


class GitHubDotCom(types.ModuleType):
    class GitHubOwner:
        def __init__(self, owner: str):
            self.owner = owner

        def __truediv__(self, repo: str):
            # @TODO: Download/install then import then return
            # @TODO: Maybe scrub from `sys.modules`?
            return object()

        # @TODO: See if we can add `@` for ref?

    def __truediv__(self, owner: str):
        return GitHubDotCom.GitHubOwner(owner)


sys.meta_path.insert(0, _MPF())

# Now we need to inject `.com` on the `github` module,
# so that it is both a module (E.g. `import conjurl.github.com.<...>.<...>`)
# and so that we can use it for ops (E.g. `github.com / <owner> / <repo>`).
import conjurl.github as github

# N.B. Force the import machinery to put `com` into the `github` namespace,
# so that we can overrride it (otherwise ours will get overriden on first import).
import conjurl.github.com

github.com = GitHubDotCom(name="com")
