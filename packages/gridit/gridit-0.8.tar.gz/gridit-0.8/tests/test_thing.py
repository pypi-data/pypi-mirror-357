import pytest


@pytest.mark.parametrize("common_arg1", [0, 1])
@pytest.mark.parametrize("common_arg2", [2, 3])
class TestParametrized:
    @pytest.mark.parametrize("a", [0, 1])
    def test_1(self, common_arg1, common_arg2, a):
        pass

    @pytest.mark.parametrize("b", [0, 1])
    def test_2(self, common_arg1, common_arg2, b):
        pass

    @pytest.mark.parametrize("x", [0, 1])
    def test_100(self, common_arg1, common_arg2, x):
        pass


common_params = {
    "one": {
        "common_arg1": 0,
        "common_arg2": 2,
        "a": 0,
        "b": 0,
        "x": 0,
    },
    "two": {
        "common_arg1": 1,
        "common_arg2": 3,
        "a": 1,
        "b": 1,
        "x": 1,
    },
}


@pytest.mark.parametrize(
    "common_arg1, common_arg2, a",
    [
        pytest.param(val["common_arg1"], val["common_arg2"], val["a"], id=key)
        for key, val in common_params.items()
    ],
)
def test_1(common_arg1, common_arg2, a):
    pass


@pytest.mark.parametrize(
    "common_arg1, common_arg2, b",
    [
        pytest.param(val["common_arg1"], val["common_arg2"], val["b"], id=key)
        for key, val in common_params.items()
    ],
)
def test_2(common_arg1, common_arg2, b):
    pass


@pytest.mark.parametrize(
    "common_arg1, common_arg2, x",
    [
        pytest.param(val["common_arg1"], val["common_arg2"], val["x"], id=key)
        for key, val in common_params.items()
    ],
)
def test_100(common_arg1, common_arg2, x):
    pass
