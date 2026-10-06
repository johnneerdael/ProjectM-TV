"""Editable, owner-chosen starter profiles, not inferred demographic tastes."""
import copy

from mood_scoring import CHILL_CONSTRAINTS


def _preference(feature,target,scale,weight):
    return {'feature':feature,'target':list(target),'scale':scale,'weight':weight}


def _genre(name,activity,smooth,bass,style=('structure.symmetry',(.5,1)),trails=(.3,1.5)):
    return {'id':name,'origin':'initial research assumptions; not calibrated',
        'preferences':[
            _preference('score.intensity',activity,15,.25),
            _preference('score.smoothness',(smooth,100),20,.20),
            _preference('audio.bass_peak_rgb_effect',bass,.04,.20),
            _preference(style[0],style[1],.25,.20),
            _preference('feedback.half_life_s',trails,1,.05)],
        'constraints':[],'minimum_preference_coverage':.9,'maximum_suitability_interval_width':10}


PROFILES={
    'ambient-v1':_genre('ambient-v1',(5,25),90,(0,.02),('structure.organic',(.5,1)),(.8,3)),
    'chillout-v1':_genre('chillout-v1',(10,35),85,(.01,.04),('structure.organic',(.4,1))),
    'trance-v1':_genre('trance-v1',(45,85),75,(.03,.10)),
    'melodic-techno-v1':_genre('melodic-techno-v1',(35,75),85,(.02,.08),('structure.symmetry',(.75,1))),
    'techno-v1':_genre('techno-v1',(60,95),70,(.04,.15)),
    'hardstyle-v1':_genre('hardstyle-v1',(75,100),50,(.05,.20)),
    'pop-v1':_genre('pop-v1',(25,65),75,(.01,.07),('structure.geometric',(.3,1))),
    'hip-hop-v1':_genre('hip-hop-v1',(25,75),75,(.02,.10)),
    'jazz-v1':_genre('jazz-v1',(10,60),80,(0,.07),('structure.organic',(.3,1))),
    'classical-v1':_genre('classical-v1',(5,65),85,(0,.05),('structure.organic',(.3,1))),
}
PROFILES['gentle-home-tv-v1']={
    'id':'gentle-home-tv-v1','origin':'owner-chosen gentle viewing default, any age',
    'preferences':[_preference('score.intensity',(5,30),15,.25),
                   _preference('score.smoothness',(90,100),20,.35),
                   _preference('palette.mean_saturation',(.25,.70),.25,.20),
                   _preference('feedback.half_life_s',(.3,1.5),1,.20)],
    'constraints':copy.deepcopy(CHILL_CONSTRAINTS)+[
        {'feature':'palette.hue_rate_p95_cycles_s','maximum':.08,'require_bound':True},
        {'feature':'motion.discontinuities_hz','maximum':0,'require_bound':True}],
    'minimum_preference_coverage':.9,'maximum_suitability_interval_width':10}
PROFILES['focus-v1']=copy.deepcopy(PROFILES['gentle-home-tv-v1'])
PROFILES['focus-v1'].update(id='focus-v1',origin='initial focus/background assumptions')
PROFILES['focus-v1']['preferences'][0]['target']=[5,25]
PROFILES['focus-v1']['constraints'][0]['maximum']=.08
PROFILES['neutral-v1']={
    'id':'neutral-v1','origin':'neutral default for any age; explicit tastes override',
    'preferences':[_preference('score.intensity',(25,55),15,.6),
                   _preference('score.smoothness',(80,100),20,.4)],'constraints':[],
    'minimum_preference_coverage':.9,'maximum_suitability_interval_width':10}
PROFILES['psychedelic-v1']={
    'id':'psychedelic-v1','origin':'explicit psychedelic taste; speed/flash permission independent',
    'preferences':[_preference('score.psychedelic',(75,100),20,.6),
                   _preference('score.intensity',(20,80),20,.4)],'constraints':[],
    'minimum_preference_coverage':.9,'maximum_suitability_interval_width':10}
PROFILES['party-v1']={
    'id':'party-v1','origin':'initial energetic preference; no default flash exclusion',
    'preferences':[_preference('score.intensity',(70,100),15,.6),
                   _preference('audio.bass_peak_rgb_effect',(.05,.20),.04,.4)],'constraints':[],
    'minimum_preference_coverage':.9,'maximum_suitability_interval_width':10}


def get_profile(name=None, *, age_band=None):
    """Age selects only the owner's optional first-use default.

    A non-neutral explicit choice fully overrides that default. All younger
    age bands use the same neutral profile; no age score is inferred.
    """
    if name is None:name='gentle-home-tv-v1' if age_band=='70+' else 'neutral-v1'
    if name not in PROFILES:raise ValueError('unknown starter profile: '+name)
    return copy.deepcopy(PROFILES[name])
