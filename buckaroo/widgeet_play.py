import json
import warnings

from ipywidgets import DOMWidget
from traitlets import Unicode, List, Dict, observe


from pandas.io.json import dumps as pdumps


def split_operations(ops):
    machine_gen, user_entered = [],[]
    for command in ops:
        if command[0] == "machine":
            machine_gen.append(command)
        else:
            user_entered.append(command)
    return machine_gen, user_entered

def lists_match(l1, l2):
    #https://note.nkmk.me/en/python-list-compare/#checking-the-exact-match-of-lists
    if len(l1) != len(l2):
        return False
    return all(x == y and type(x) == type(y) for x, y in zip(l1, l2))

class PlayWidget(DOMWidget):
    operations = List().tag(sync=True)
    machine_gen_operations = List().tag(sync=True)
    user_entered_operations = List().tag(sync=True)
    operation_results = Dict({}).tag(sync=True)
    pre_formatted_text = Unicode("").tag(sync=True)

    def __init__(self, text):
        super().__init__()
        self.orig_setup(text)

    def orig_setup(self, t):
        self.orig_text = t
        self.operations = [["machine", "post_add"], ["machine", "post_add2"]]
        
    @observe('operations')
    def handle_operations(self, change):

        if lists_match(change['old'], change['new']):
            return
        else:
            new_ops = change['new']
            self.machine_gen_operations, self.user_entered_operations = split_operations(new_ops)

    @observe('user_entered_operations')
    def interpret_operations(self, change):
        if lists_match(change['old'], change['new']):
            return # nothing changed, do no computations
        print("interpret_operations")
        ops = change['new']
        new_text = self.pre_formatted_text
        for command in ops:
            new_text += command[1]
        print("final_text", new_text)


    @observe('machine_gen_operations')
    def interpret_machine_gen_ops(self, change):
        if lists_match(change['old'], change['new']):
            return # nothing changed, do no computations
        print("interpret_machine_gen_ops")
        ops = change['new']
        new_text = self.orig_text
        for command in ops:
            new_text += command[1]

        self.pre_formatted_text = new_text


    @observe('pre_formatted_text')
    def pre_text_stats(self, change):
        new_text = change['new']
        print("pre_text_stats", len(new_text))

