"""Collection-relative beta audience groups; perceptual accuracy remains provisional."""
import math
from audience_ranking import relative_activity_ranks

BANDS={'chill':(1,30),'normal':(25,75),'intense':(70,100)}


def groups_for_score(score):
    if isinstance(score,bool) or not isinstance(score,(int,float)) or not math.isfinite(score) or not 1<=score<=100:
        raise ValueError('Finite1–100score required')
    return [name for name,(low,high) in BANDS.items() if low<=score<=high]


def ranked_rows(records):
    if not records:raise ValueError('Complete nonempty score collection required')
    for row in records:
        if not isinstance(row.get('has_activity'),bool):
            raise ValueError('Explicit activity state required')
        value=row.get('raw_activity')
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
            raise ValueError('Unresolved/invalid activity is not calmness')
    active=[r for r in records if r.get('has_activity') is True]
    if not active:raise ValueError('No moving/activity-bearing presets to establish endpoints')
    ranks=relative_activity_ranks([r['raw_activity'] for r in active])
    by_name={r['preset']:score for r,score in zip(active,ranks)}
    if len({r['preset'] for r in records})!=len(records):raise ValueError('Duplicate preset identity')
    return [{**r,'score':by_name.get(r['preset'],1),
             'group_eligible':r.get('has_activity') is True,
             'groups':groups_for_score(by_name[r['preset']]) if r['preset'] in by_name else []}
            for r in records]
