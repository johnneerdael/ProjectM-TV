from pathlib import Path

from preset_lab.report import write_report
from preset_lab.models import MatchDecision,PresetRecord


def test_report_escapes_preset_text_and_distinguishes_predictions(tmp_path):
    record=PresetRecord('<script>alert("x")</script>.milk',"a"*64,0)
    rows=[MatchDecision(record,"ambient",.5,.7,.6,True,"predicted",{"music_test_count":0})]
    path=write_report([],rows,tmp_path)
    text=path.read_text()
    assert '<script>alert("x")</script>' not in text
    assert '&lt;script&gt;' in text
    assert "Predicted" in text
    assert "Music-tested" in text
    assert "Provisional" in text
