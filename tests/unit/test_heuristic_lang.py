from buckaroo.jlisp.lisp_utils import s
from buckaroo.jlisp.lispy import make_interpreter
from functools import cache
# noqa: E712

@cache
def get_rule_interpreter():
    """eval a string as scheme, a list as jlisp"""
    jlisp_eval, sc_eval = make_interpreter()
    sc_eval(MACROS)

    def multi_eval(code, env=None):
        if isinstance(code, list):
            return jlisp_eval(code, env)
        assert isinstance(code, str)
        return sc_eval(code, env)
    return multi_eval




MACROS = """
(begin
   (define-macro and (lambda args 
       (if (null? args) #t
           (if (= (length args) 1) (car args)
               `(if ,(car args) (and ,@(cdr args)) #f)))))

;; More macros can go here

    ;; Rule basically lets us define a lambda with less syntax
    (define-macro rule (lambda args
        `(lambda unused ,@args)))

    ;; convience for defining a conditional that will be evaulated with measure passed n
    (define-macro rule-measure (lambda args
        `(lambda (measure) ,@args)))


    (define-macro m< (lambda operand
        `(< measure ,@operand)))
    (define primary
        (lambda (other-cond)
            (if other-cond
                (* other-cond 100)
                other-cond)))

    (define-macro m> (lambda operand
        `(if (> measure ,@operand)
             measure #f)))

    (define-macro return-measure (lambda operand
        `(if #t
             measure 9)))
)"""

def eval_heuristic_rule(rule, measure):
    _eval = get_rule_interpreter()
    return _eval(rule, {'measure': measure})


def get_top_score(rules, score_dict):
    scores = {}
    for rule_name, rule in rules.items():
        scores[rule_name] = eval_heuristic_rule(rule, score_dict[rule_name])
    return max(scores, key=scores.get)
                                                

def eval_heuristics(rules, col_scores):
    chosen_fixes = {}
    for col, scores in col_scores.items():
        chosen_fixes[col] = get_top_score(rules, scores)
    return chosen_fixes


l_rules = {
    't_str_bool':         [s('m>'), .7],
    'regular_int_parse':  [s('m>'), .9],
    'strip_int_parse':    [s('m>'), .7],
    't_us_dates':         [s('primary'), [s('m>'), .7]]}

def test_get_top_score():
    probably_bool= {
        't_str_bool': .8, 'regular_int_parse': .2, 'strip_int_parse': .3, 't_us_dates': 0}
    
    get_top_score(l_rules, probably_bool)

def test_eval_heuristics():
    col_scores = dict(
        probably_bool= {
            't_str_bool': .8, 'regular_int_parse': .2, 'strip_int_parse': .3, 't_us_dates': 0},
        # no_changes = {
        #     't_str_bool': 0, 'regular_int_parse': 0, 'strip_int_parse': 0, 't_us_dates': 0},
        probably_dates = {
            't_str_bool': .8, 'regular_int_parse': .95, 'strip_int_parse': 0, 't_us_dates': .71})
    res = eval_heuristics(l_rules, col_scores)
    assert res== dict(probably_bool='t_str_bool', probably_dates='t_us_dates')
    
    

def test_macro_behaviour_rule():
    #verify that macros work from scheme and jlisp
    assert eval_heuristic_rule([s('m>'), .7], .6) == False
    assert eval_heuristic_rule('(m> .7)', .6) == False

    

    assert eval_heuristic_rule([s('if'), 4, s('measure'), 9], 3) == 3
    assert eval_heuristic_rule([s('m>'), .7], .8) == .8


    
def test_none_null():
    assert eval_heuristic_rule([s('null?'), s('measure')], []) == True
    assert eval_heuristic_rule([s('null?'), [s('m>'), .7]], .9) == False
    assert eval_heuristic_rule([s('none?'), s('measure')], None) == True


def test_heuristic_rule():
    assert eval_heuristic_rule([s('begin'),
                                [s('display'), s('measure')],
                                s('measure')],
                                .7) == .7
    assert eval_heuristic_rule('(m> .7)', .8)  == .8
    assert eval_heuristic_rule('(m> .7)', .5)  == False
    assert eval_heuristic_rule([s('m>'), .7], .8) == .8
    assert eval_heuristic_rule([s('m>'), .7], .6) == False
    assert eval_heuristic_rule([s('primary'), [s('m>'), .7]], .6) == False
    assert eval_heuristic_rule([s('primary'), [s('m>'), .7]], .8) == 80


def test_timing(): # noqa: E712
    import time
    start_time = time.perf_counter()
    for i in range(100):
        assert eval_heuristic_rule([s('m>'), .7], .6) == False
        assert eval_heuristic_rule([s('primary'), [s('m>'), .7]], .6) == False
        assert eval_heuristic_rule([s('primary'), [s('m>'), .7]], .8) == 80
        assert eval_heuristic_rule([s('primary'), [s('m>'), .7]], .6) == False  
        assert eval_heuristic_rule([s('m>'), .7], .6) == False  # noqa: E712
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"Function execution time: {execution_time:.4f} seconds")
    # 20 columns, 5 rules = 100
    # 5 strategies (sets of rules)
    # less than 10ms on my machine, this is fast enough
