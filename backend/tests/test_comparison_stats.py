from app.services.comparison_service import two_proportion_z_test

def test_identical_proportions_not_significant():
    res = two_proportion_z_test(x1=8, n1=10, x2=8, n2=10)
    assert res["is_significant"] is False
    assert res["z_score"] == 0.0
    assert res["p_value"] == 1.0
    assert res["difference"] == 0.0

def test_large_difference_is_significant():
    # Agent 1: 95/100 (95%), Agent 2: 60/100 (60%)
    res = two_proportion_z_test(x1=95, n1=100, x2=60, n2=100)
    assert res["is_significant"] is True
    assert res["z_score"] > 5.0
    assert res["p_value"] < 0.001
    assert res["difference"] == 0.35

def test_small_sample_bounds():
    # 5 runs vs 5 runs
    res = two_proportion_z_test(x1=5, n1=5, x2=3, n2=5)
    assert len(res["ci_95"]) == 2
    assert res["ci_95"][0] <= res["ci_95"][1]
