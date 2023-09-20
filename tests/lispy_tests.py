

"""
It would be awesome to have cleaning and verification commands that add new columns with related names

The new columns are null accept for errored values.

Could use this to show original values that were removed/cleaned.  Combined with conditional styling in the UI

sick.  And still ahve high perfromance properly typed columns



"""

def is_symbol(obj):
    return isinstance(obj, dict) and obj.has_key("symbol")

def is_generated_symbol(obj):
    return is_symbol(obj) and obj.get("meta", False)

def split_operations(full_operations):
    """
    utitlity to split a combined set of operations with machine generated commands and user entered commands into two lists, machine_generated and user_generated

    machine_generated commands have function calls with the symbol token also having a meta key with a value of {"precleaning":True}
    """

    machine_generated, user_entered = [], []
    for command in full_operations:
        assert isinstance(command, list)
        sym_atom = command[0]
        if is_symbol(sym_atom):
            if is_generated_symbol(sym_atom):
                machine_generated.append(command)
            else:
                user_entered.append(command)
            continue
        raise Exception("Unexpected token %r" % command)
    return machine_generated, user_entered
            

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
