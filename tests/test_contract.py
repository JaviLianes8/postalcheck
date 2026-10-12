import importlib.resources

import postalcheck

PUBLIC_API: list[str] = [
    "InvalidPostalCodeError",
    "UnknownCountryError",
    "example",
    "is_valid",
    "normalize",
    "supported_countries",
]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(postalcheck.__all__) == sorted(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in postalcheck.__all__:
        assert hasattr(postalcheck, name)


def test_version_is_a_three_part_string() -> None:
    parts = postalcheck.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("postalcheck").joinpath("py.typed").is_file()
