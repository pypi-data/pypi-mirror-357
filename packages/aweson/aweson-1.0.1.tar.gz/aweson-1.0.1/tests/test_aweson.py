import pytest

from aweson import JP, find_all


@pytest.mark.parametrize("jp,stringfied", [
    (JP, ""),

    (JP.hello, ".hello"),
    (JP.hello.world, ".hello.world"),

    (JP["hello"], ".hello"),
    (JP["hello"]["world"], ".hello.world"),

    (JP[0], "[0]"),
    (JP[42], "[42]"),
    (JP[-1], "[-1]"),
    (JP[5][42], "[5][42]"),

    (JP[:], "[:]"),
    (JP[::], "[:]"),
    (JP[1:], "[1:]"),
    (JP[1::], "[1:]"),
    (JP[:2], "[:2]"),
    (JP[:2:], "[:2]"),
    (JP[::-1], "[::-1]"),
    (JP[1:12:-1], "[1:12:-1]"),

    (JP[5].hello, "[5].hello"),
    (JP.hello[5], ".hello[5]"),
    (JP[5].hello[42].world, "[5].hello[42].world"),
    (JP.hello[5].world[42], ".hello[5].world[42]"),

    (JP["hello"][5]["world"][42], ".hello[5].world[42]"),

    (JP.hello(JP.world,JP.hi[0]), ".hello(.world, .hi[0])"),
])
def test_jp_stringification(jp, stringfied):
    assert str(jp) == stringfied


@pytest.mark.parametrize("content,jp,expected_items", [
    ("string", JP, ["string"]),
    (5, JP, [5]),
    (5.13, JP, [5.13]),
    (True, JP, [True]),
    ({"hello": 42}, JP, [{"hello": 42}]),
    ([5, 42], JP, [[5, 42]]),

    ({"hello": 42, "hi": "irrelevant"}, JP.hello, [42]),
    ({"hello": {"world": 42}, "hi": "irrelevant"}, JP.hello.world, [42]),

    ({"hello": 42, "hi": "irrelevant"}, JP["hello"], [42]),
    ({"hello": {"world": 42}, "hi": "irrelevant"}, JP["hello"]["world"], [42]),

    ([5, 42], JP[0], [5]),
    ([5, 42], JP[-1], [42]),

    ([5, 42, 137], JP[:], [5, 42, 137]),
    ([5, 42, 137], JP[1:], [42, 137]),
    ([5, 42, 137], JP[:1], [5]),
    ([5, 42, 137], JP[::-1], [137, 42, 5]),

    ({"hello": [5, 42]}, JP.hello[1], [42]),
    ([{"hello": 42}, {"hello": 5}], JP[1].hello, [5]),

    ([{"hello": 42}, {"hello": 5}], JP[1]["hello"], [5]),

    ([{"hello": "world", "hi": [5, 42, 137]}, {"hello": "mundo", "hi": [-5, -42, -137]}], JP[:](JP.hello, JP.hi[1]), [("world", 42), ("mundo", -42)])
])
def test_find_all(content, jp, expected_items):
    items = list(find_all(content, jp))
    assert items == expected_items


def test_find_all_demo_transformation():
    list_of_entities = [
        { "id": 5, "value": "five" },
        { "id": 42, "value": "life, universe and everything" },
        { "id": 137, "value": "137" },
    ]

    id_to_value_map = {id_: value for id_, value in find_all(list_of_entities, JP[:](JP.id, JP.value))}
    assert id_to_value_map == {
        5: "five",
        42: "life, universe and everything",
        137: "137"
    }


@pytest.mark.parametrize("content,jp,expected_paths_and_items", [
    ("string", JP, [(JP, "string")]),

    ({"hello": {"world": 42}, "hi": "irrelevant"}, JP.hello.world, [(JP.hello.world, 42)]),

    ([5, 42], JP[-1], [(JP[1], 42)]),

    ([5, 42, 137], JP[1:], [(JP[1], 42), (JP[2], 137)]),
    ([5, 42, 137], JP[::-1], [(JP[2], 137), (JP[1], 42), (JP[0], 5)]),

    ([{"hello": 42}, {"hello": 5}], JP[1:]["hello"], [(JP[1].hello, 5)]),
    ([{"hello": 42}, {"hello": 5}], JP[-1::-1]["hello"], [(JP[1].hello, 5), (JP[0].hello, 42)]),

    ([{"hello": "world", "hi": [5, 42, 137]}, {"hello": "mundo", "hi": [-5, -42, -137]}], JP[:](JP.hello, JP.hi[1]), [(JP[0](JP.hello, JP.hi[1]), ("world", 42)), (JP[1](JP.hello, JP.hi[1]), ("mundo", -42))]),
    ([{"hello": "world", "hi": [5, 42, 137]}, {"hello": "mundo", "hi": [-5, -42, -137]}], JP[1:0:-1](JP.hello, JP.hi[1]), [(JP[1](JP.hello, JP.hi[1]), ("mundo", -42))])

])
def test_find_all_enumerating_paths(content,jp,expected_paths_and_items):
    paths_and_items = list(find_all(content, jp, enumerate=True))
    assert len(paths_and_items) == len(expected_paths_and_items)
    for path_and_item, expected_path_and_item in zip(paths_and_items, expected_paths_and_items):

        path, item = path_and_item

        # The path yielded alongside the item points to the item itself ...
        assert item == next(find_all(content, path))

        # ... but let's check it against explicit expectations, too.
        expected_path, expected_item = expected_path_and_item
        assert item == expected_item
        assert path == expected_path



@pytest.mark.parametrize("content, jp",[
    ([], JP[0]),
    ([5, 42], JP[2]),
    ({"hello": [5, 42]}, JP.hello[2]),
    ({"hello": [5, 42]}, JP["hello"][2]),
])
def test_find_all_index_error(content, jp):
    with pytest.raises(IndexError):
        list(find_all(content, jp))


@pytest.mark.parametrize("content, jp", [
    ({}, JP.hello),
    ({"hello": {"world": 42}}, JP.hello.hi),
    ({"hello": {"world": 42}}, JP["hello"]["hi"]),
])
def test_find_all_key_error(content, jp):
    with pytest.raises(KeyError):
        list(find_all(content, jp))



def test_ad_hoc():
    content = {"hello": 42, "hi": "irrelevant"}
    results = list(find_all(content, JP["hello"]))
    assert results == [42]

    content = {"hello": {"world": 42}, "hi": "irrelevant"}
    results = list(find_all(content, JP.hello.world))
    assert results == [42]
