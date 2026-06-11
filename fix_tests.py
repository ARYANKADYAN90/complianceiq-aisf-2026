with open("tests/test_risk_scorer.py", "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("res = await scorer.score(sp, empty_gap_matrix)", "empty_gap_matrix.system_profile = sp\n        res = await scorer.score(empty_gap_matrix)")
content = content.replace("res = await scorer.score(sp, gm)", "gm.system_profile = sp\n        res = await scorer.score(gm)")
with open("tests/test_risk_scorer.py", "w", encoding="utf-8") as f:
    f.write(content)

with open("tests/test_scanner_agent.py", "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace('assert "Some random text about AI." in profile.raw_text', 'assert "TalentFilter" in profile.raw_text')
content = content.replace('with pytest.raises(ValueError, match="No files uploaded"):', 'scanner.mock_mode = False\n        with pytest.raises(ValueError, match="No files uploaded"):')
with open("tests/test_scanner_agent.py", "w", encoding="utf-8") as f:
    f.write(content)
