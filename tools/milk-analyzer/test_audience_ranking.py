import pytest

from audience_ranking import relative_activity_ranks


def test_scores_are_spread_by_order_without_changing_intensity():
    assert relative_activity_ranks([10,11,90]) == [1,50.5,100]


def test_equal_scores_remain_tied_including_endpoints():
    assert relative_activity_ranks([10,10,20,30,30]) == [1,1,50.5,100,100]


def test_input_order_and_unknowns_are_preserved():
    assert relative_activity_ranks([90,None,10,11]) == [100,None,1,50.5]
    assert relative_activity_ranks([None,None]) == [None,None]


def test_no_spread_is_invented_for_a_single_value_or_all_ties():
    assert relative_activity_ranks([20]) == [50.5]
    assert relative_activity_ranks([20,20,20]) == [50.5]*3


@pytest.mark.parametrize('value',[True,float('nan'),float('inf'),-1,101,'50'])
def test_invalid_measured_scores_are_rejected(value):
    with pytest.raises(ValueError):relative_activity_ranks([value])
