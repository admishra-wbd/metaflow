import types

import pytest

from metaflow.plugins.pypi.conda_environment import CondaEnvironment


@pytest.fixture
def conda_environment():
    flow = []
    env = CondaEnvironment(flow)
    env.datastore_type = "local"
    env.datastore = types.SimpleNamespace(
        TYPE="local",
        get_datastore_root_from_config=lambda _echo: "/tmp/metaflow",
    )
    env.logger = lambda *args, **kwargs: None
    return env


@pytest.fixture
def make_step():
    class _Step:
        def __init__(self, decorators):
            self.name = "start"
            self.decorators = decorators

    def _make(pypi_packages, conda_packages=None, include_pypi=True):
        conda_decorator = types.SimpleNamespace(
            name="conda",
            attributes={
                "packages": conda_packages or {},
                "python": "3.10.9",
                "disabled": False,
            },
            supports_conda_environment=False,
        )
        decorators = [conda_decorator]
        if include_pypi:
            decorators.append(
                types.SimpleNamespace(
                    name="pypi",
                    attributes={
                        "packages": pypi_packages,
                        "python": None,
                        "disabled": False,
                    },
                    supports_conda_environment=False,
                )
            )
        return _Step(decorators)

    return _make


def test_gcp_keyring_is_channel_pinned_for_conda_resolve(
    conda_environment,
    make_step,
    mocker,
):
    mocker.patch(
        "metaflow.plugins.pypi.conda_environment.os.getenv",
        return_value="/tmp/fake-google-credentials.json",
    )
    step = make_step({"demo": "1.0.0"})

    environment = conda_environment.get_environment(step)

    assert (
        environment["conda"]["packages"][
            "conda-forge::keyrings.google-artifactregistry-auth"
        ]
        == ">=1.1.1"
    )


def test_gcp_keyring_not_injected_without_google_credentials(
    conda_environment,
    make_step,
    mocker,
):
    mocker.patch("metaflow.plugins.pypi.conda_environment.os.getenv", return_value=None)
    step = make_step({"demo": "1.0.0"})

    environment = conda_environment.get_environment(step)

    assert (
        "conda-forge::keyrings.google-artifactregistry-auth"
        not in environment["conda"]["packages"]
    )


@pytest.mark.parametrize(
    "package_name, expected_name",
    [
        ("keyrings.google-artifactregistry", "keyrings.google-artifactregistry-auth"),
        (
            "conda-forge::keyrings.google-artifactregistry",
            "conda-forge::keyrings.google-artifactregistry-auth",
        ),
    ],
)
def test_keyring_alias_is_normalized_for_conda_packages(
    conda_environment,
    make_step,
    mocker,
    package_name,
    expected_name,
):
    mocker.patch("metaflow.plugins.pypi.conda_environment.os.getenv", return_value=None)
    step = make_step(
        {},
        conda_packages={package_name: ">=1.1.1"},
        include_pypi=False,
    )

    environment = conda_environment.get_environment(step)

    assert expected_name in environment["conda"]["packages"]
    assert package_name not in environment["conda"]["packages"]
