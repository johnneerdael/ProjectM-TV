from pytest import raises


def test_relative_scores_use_moving_endpoints_and_preserve_ties():
    from beta_collections import ranked_rows
    rows=ranked_rows([{'preset':'a','raw_activity':2.,'has_activity':True},
                      {'preset':'b','raw_activity':4.,'has_activity':True},
                      {'preset':'c','raw_activity':4.,'has_activity':True},
                      {'preset':'d','raw_activity':9.,'has_activity':True},
                      {'preset':'static','raw_activity':0.,'has_activity':False}])
    values={r['preset']:r for r in rows}
    assert values['a']['score']==1 and values['d']['score']==100
    assert values['b']['score']==values['c']['score']
    assert values['static']['score']==1 and not values['static']['group_eligible']


def test_requested_bands_overlap_exactly():
    from beta_collections import groups_for_score
    assert groups_for_score(1)==['chill']
    assert groups_for_score(25)==['chill','normal']
    assert groups_for_score(30)==['chill','normal']
    assert groups_for_score(31)==['normal']
    assert groups_for_score(70)==['normal','intense']
    assert groups_for_score(75)==['normal','intense']
    assert groups_for_score(100)==['intense']


def test_unknown_or_invalid_activity_cannot_be_exported_as_calm():
    from beta_collections import ranked_rows
    for value in [None,float('nan'),-1]:
        with raises(ValueError):ranked_rows([{'preset':'a','raw_activity':value,'has_activity':True}])


def test_unclipped_raw_activity_can_establish_relative_endpoints():
    from beta_collections import ranked_rows
    rows=ranked_rows([{'preset':'a','raw_activity':4.,'has_activity':True},
                      {'preset':'b','raw_activity':150.,'has_activity':True},
                      {'preset':'c','raw_activity':2000.,'has_activity':True}])
    assert [r['score'] for r in rows]==[1,50.5,100]


def test_missing_activity_state_is_not_an_inactive_result():
    from beta_collections import ranked_rows
    with raises(ValueError):
        ranked_rows([{'preset':'a','raw_activity':1.,'has_activity':True},
                     {'preset':'b','raw_activity':2.}])
