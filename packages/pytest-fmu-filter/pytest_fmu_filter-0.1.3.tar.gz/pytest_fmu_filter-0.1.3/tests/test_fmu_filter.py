from .utils import download_reference_fmus


def test_invalid_fmu_filter_key(pytester):
    pytester.makepyfile("""
        import pytest

        @pytest.mark.fmu_filter(dummy=True)
        def test_invalid_fmu_filter_key(fmu):
            pass
    """)

    result = pytester.runpytest("--fmus=tests/data/hello_world.fmu", "-v")
    assert result.ret == 2

    result = pytester.runpytest("-v")
    assert result.ret == 1


def test_fmu_filter_undefined(pytester):
    """Test that no fmu_filter marker results in no FMU being loaded."""
    pytester.makepyfile("""
        import pytest

        def test_fmu_filter_undefined(fmu):
            assert fmu is not None
    """)

    result = pytester.runpytest("--fmus", "tests/data/hello_world.fmu", "-v")
    assert result.ret == 1

    result = pytester.runpytest(
        "--fmus", "tests/data/hello_world.fmu", "tests/data/hello_world2.fmu", "-v"
    )
    assert result.ret == 1

    result = pytester.runpytest("-v")
    assert result.ret == 1


def test_fmu_unrelated(pytester):
    """Test that no fmu_filter marker results in no FMU being loaded."""
    pytester.makepyfile("""
        import pytest

        def test_fmu_unrelated():
            assert True
    """)

    result = pytester.runpytest("--fmus", "tests/data/hello_world.fmu", "-v")
    assert result.ret == 0
    result = pytester.runpytest(
        "--fmus", "tests/data/hello_world.fmu", "tests/data/hello_world2.fmu", "-v"
    )
    assert result.ret == 0
    result = pytester.runpytest("-v")
    assert result.ret == 0


# test_should_skip.py::test_should_skip[/tmp/pytest-of-coder/pytest-74/test_should_skip1/2.0/Stair.fmu] PASSED [  7%]
# test_should_skip.py::test_should_skip[/tmp/pytest-of-coder/pytest-74/test_should_skip1/2.0/Feedthrough.fmu] PASSED [ 14%]
# test_should_skip.py::test_should_skip[/tmp/pytest-of-coder/pytest-74/test_should_skip1/2.0/Resource.fmu] PASSED [ 21%]
# test_should_skip.py::test_should_skip[/tmp/pytest-of-coder/pytest-74/test_should_skip1/2.0/VanDerPol.fmu] PASSED [ 28%]
# test_should_skip.py::test_should_skip[/tmp/pytest-of-coder/pytest-74/test_should_skip1/2.0/BouncingBall.fmu] PASSED [ 35%]
# test_should_skip.py::test_should_skip[/tmp/pytest-of-coder/pytest-74/test_should_skip1/2.0/Dahlquist.fmu] PASSED [ 42%]
# test_should_skip.py::test_should_skip[/tmp/pytest-of-coder/pytest-74/test_should_skip1/3.0/Stair.fmu] PASSED [ 50%]
# test_should_skip.py::test_should_skip[/tmp/pytest-of-coder/pytest-74/test_should_skip1/3.0/Clocks.fmu] PASSED [ 57%]
# test_should_skip.py::test_should_skip[/tmp/pytest-of-coder/pytest-74/test_should_skip1/3.0/Feedthrough.fmu] PASSED [ 64%]
# test_should_skip.py::test_should_skip[/tmp/pytest-of-coder/pytest-74/test_should_skip1/3.0/Resource.fmu] PASSED [ 71%]
# test_should_skip.py::test_should_skip[/tmp/pytest-of-coder/pytest-74/test_should_skip1/3.0/VanDerPol.fmu] PASSED [ 78%]
# test_should_skip.py::test_should_skip[/tmp/pytest-of-coder/pytest-74/test_should_skip1/3.0/BouncingBall.fmu] PASSED [ 85%]
# test_should_skip.py::test_should_skip[/tmp/pytest-of-coder/pytest-74/test_should_skip1/3.0/StateSpace.fmu] PASSED [ 92%]
# test_should_skip.py::test_should_skip[/tmp/pytest-of-coder/pytest-74/test_should_skip1/3.0/Dahlquist.fmu] PASSED [100%]


def test_fmu_filter(pytester, tmpdir):
    """Test that fmu_filter marker works as expected."""
    # Download the reference FMU files
    fmus = download_reference_fmus(tmpdir, subdirs=["2.0", "3.0"])

    # Get absolute paths of downloaded FMUs as strings
    fmu_paths = [str(fmu) for fmu in fmus]

    pytester.makepyfile("""
        import pytest

        @pytest.mark.fmu_filter(name_matches="Stair")
        def test_name_matches(fmu):
            assert "Stair" in fmu

        @pytest.mark.fmu_filter(has_input=True, fmi_major_version=2)
        def test_is_me_and_has_input_and_fmi2(fmu):
            assert "2.0/Feedthrough" in fmu

        @pytest.mark.fmu_filter(has_input=True, fmi_major_version=3)
        def test_is_me_and_has_input_and_fmi3(fmu):
            expected = ["3.0/Feedthrough", "3.0/StateSpace", "3.0/Clock"]
            assert any(fmu_part in fmu for fmu_part in expected)

        @pytest.mark.fmu_filter(fmi_version="2.0")
        def test_fmi2(fmu):
            expected = ["2.0/BouncingBall", "2.0/Dahlquist", "2.0/Feedthrough", "2.0/Resource", "2.0/Stair", "2.0/VanDerPol"]
            assert any(fmu_part in fmu for fmu_part in expected)

        @pytest.mark.fmu_filter(fmi_version="3.0")
        def test_fmi3(fmu):
            expected = ["3.0/BouncingBall", "3.0/Clocks.fmu", "3.0/StateSpace.fmu", "3.0/Dahlquist", "3.0/Feedthrough", "3.0/Resource", "3.0/Stair", "3.0/VanDerPol"]
            assert any(fmu_part in fmu for fmu_part in expected)
    """)

    # Pass downloaded FMUs to runpytest
    result = pytester.runpytest("--fmus", *fmu_paths, "-v")
    assert result.ret == 0


def test_should_skip(pytester, tmpdir):
    """Test that fmu_filter marker works as expected."""
    # Download the reference FMU files
    fmus = download_reference_fmus(tmpdir, subdirs=["2.0", "3.0"])

    # Get absolute paths of downloaded FMUs as strings
    fmu_paths = [str(fmu) for fmu in fmus]

    pytester.makepyfile("""
        import pytest

        @pytest.mark.fmu_filter(is_me=True, is_cs=False)
        def test_should_skip(fmu):
            pass
    """)

    # Pass downloaded FMUs to runpytest
    result = pytester.runpytest("--fmus", *fmu_paths, "-v")
    assert result.ret == 5
