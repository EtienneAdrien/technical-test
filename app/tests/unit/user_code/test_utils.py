from app.features.user_code import utils


def test_generate_code():
    code = utils.generate_code()
    assert len(code) == 4 and code.isdigit()
