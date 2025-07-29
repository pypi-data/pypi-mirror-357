from ultracalc import calc

def test_addition():
    assert str(calc("1 + 1")) == "2"

def test_precision():
    result = str(calc("1.0000000000000001 + 1e-20"))
    assert result.startswith("1.0000000000000001")
