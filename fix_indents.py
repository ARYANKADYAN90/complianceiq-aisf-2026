import re

with open("tests/test_risk_scorer.py", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("        res = await scorer.score", "    res = await scorer.score")

with open("tests/test_risk_scorer.py", "w", encoding="utf-8") as f:
    f.write(text)

with open("tests/test_scanner_agent.py", "r", encoding="utf-8") as f:
    text2 = f.read()

text2 = text2.replace("        with pytest.raises", "    with pytest.raises")
text2 = text2.replace("scanner.mock_mode = False\n    with", "    scanner.mock_mode = False\n    with")

with open("tests/test_scanner_agent.py", "w", encoding="utf-8") as f:
    f.write(text2)
