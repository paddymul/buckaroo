from buckaroo.jlisp.lisp_utils import (
    merge_ops, format_ops, lists_match, split_operations
                                       )


def test_split_operations():

    full_ops = [
        [{"symbol":"dropcol", "meta":{"precleaning":True}},{"symbol":"df"},"starttime"],
        [{"symbol":"dropcol"},{"symbol":"df"},"starttime"],
    ]

    EXPECTED_cleaning_ops = [
        [{"symbol":"dropcol", "meta":{"precleaning":True}},{"symbol":"df"},"starttime"]]
    
    EXPECTED_user_gen_ops = [
        [{"symbol":"dropcol"},{"symbol":"df"},"starttime"]]

    cleaning_ops, user_gen_ops = split_operations(full_ops)

    assert EXPECTED_cleaning_ops == cleaning_ops
    assert EXPECTED_user_gen_ops == user_gen_ops

def test_lists_match():

    assert lists_match(["a", "b"], ["a", "b"])
    assert lists_match([["a", "b"]], [["a", "b"]])
    assert not lists_match(["a", "b"], ["a", "b", "c"])
    assert not lists_match([["a", "b"]], [["a", "b", "c"]])

    
SAFE_INT_TOKEN = [{'symbol': 'safe_int', 'meta':{'auto_clean': True}}, {'symbol': 'df'}]


def test_format_ops():
    """
    make sure that format_ops joins the correct column names to ops
    """
    column_meta = {
        'a': {'cleaning_ops':SAFE_INT_TOKEN },
        'b': {'cleaning_ops': [
            {'symbol': 'replace_dirty', 'meta':{'auto_clean': True}},
            {'symbol': 'df'}, '\n', None]}}

    expected_ops = [
        [{'symbol': 'safe_int', 'meta':{'auto_clean': True}}, {'symbol': 'df'}, 'a'],
        [{'symbol': 'replace_dirty', 'meta':{'auto_clean': True}}, {'symbol': 'df'}, 'b', '\n', None]]
    assert format_ops(column_meta) == expected_ops



def test_merge_ops():
    existing_ops = [
        [{'symbol': 'safe_int', 'meta':{'auto_clean': True}}, 'a'],
        [{'symbol': 'usergen'}, 'foo_column']
    ]

    cleaning_ops = [
        [{'symbol': 'new_cleaning', 'meta':{'auto_clean': True}}, 'a']]

    expected_merged = [
        [{'symbol': 'new_cleaning', 'meta':{'auto_clean': True}}, 'a'],
        [{'symbol': 'usergen'}, 'foo_column']
    ]
    print( merge_ops(existing_ops, cleaning_ops))
    print("@"*80)
    assert merge_ops(existing_ops, cleaning_ops) == expected_merged
