def test_import():
    import wickd


def test_using_boost_1024_int():
    import wickd

    result = wickd.using_boost_1024_int()
    assert isinstance(result, bool)


def test_orbital_space():
    import wickd

    wickd.reset_space()
    assert wickd.num_spaces() == 0


if __name__ == "__main__":
    test_import()
    test_orbital_space()
