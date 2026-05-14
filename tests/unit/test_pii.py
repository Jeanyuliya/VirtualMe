from virtualme.interview.pii import detect_pii


def test_email():
    assert "email" in detect_pii("Reach me at maki@example.com")


def test_phone():
    assert "phone" in detect_pii("My number is 0912-345-678")


def test_taiwan_id():
    assert "taiwan_id" in detect_pii("A123456789")


def test_english_name():
    assert "name_like_pattern" in detect_pii("I met John Smith yesterday")
