"""Match nonzero file flags while retaining native integer-prefix defaults."""
import pytest

from source_context import scalar


@pytest.mark.parametrize('text, expected', [
    ('-2147483648', 1), ('-2', 1), ('-1', 1), ('0', 0),
    ('1', 1), ('2147483647', 1), ('-1suffix', 1), ('-1.5', 1),
    ('-.5', 0), ('0.5', 0),
])
def test_nonzero_boolean_integer_prefix(text, expected):
    assert scalar({'btexwrap': text}, 'bTeXwRaP', 0, 'bool') == expected


@pytest.mark.parametrize('text', [
    'invalid', 'nan', 'inf', '2147483648', '-2147483649',
])
@pytest.mark.parametrize('default', [0, 1])
def test_invalid_boolean_retains_default(text, default):
    assert scalar({'btexwrap': text}, 'bTexWrap', default, 'bool') == default


def test_missing_boolean_retains_default():
    for default in (0, 1):
        assert scalar({}, 'bTexWrap', default, 'bool') == default
