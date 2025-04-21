import pytest
from buckaroo.jlisp.lisp_utils import split_operations, lists_match, s
from buckaroo.jlisp.lispy import make_interpreter, Symbol, isa
from functools import cache

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

    (define-macro m> (lambda operand
        `(> measure ,@operand)))

    (define-macro m< (lambda operand
        `(< measure ,@operand)))
)"""

@cache
def get_rule_interpreter():
    """eval a string as scheme, a list as jlisp"""
    jlisp_eval, sc_eval = make_interpreter()
    sc_eval(MACROS)

    def multi_eval(code, env=None):
        if isinstance(code, list):
            return jlisp_eval(code, env)
        assert isinstance(code, str)
        return sc_eval(code, None)
    return multi_eval


l_rules2 = {
    't_str_bool':         [s('lambda'), [s('measure')], [s('>'), s('measure'), .7]],
    'regular_int_parse':  [s('lambda'), [s('measure')], [s('>'), s('measure'), .9]],
    'strip_int_parse':    [s('lambda'), [s('measure')], [s('>'), s('measure'), .7]],
    't_us_dates':         [s('lambda'), [s('measure')], [s('and'), [s('>'), s('measure'), .7], 100]]}

l_rules3 = {
    't_str_bool':         [s('m>'), .7],
    'regular_int_parse':  [s('m>'), .9],
    'strip_int_parse':    [s('m>'), .7],
    't_us_dates':         [s('only'), [s('m>'), .7]]}


def eval_heuristic_rule(rule, measure):
    _eval = get_rule_interpreter()
    return _eval(rule, {'measure': measure})
    
def test_heuristic_rule():
    assert eval_heuristic_rule([s('m>'), .7], .8) == .8


def xtest_other():    
    with pytest.raises(LookupError) as excinfo:
        sc_eval("""(and 4 3)""")
    sc_eval()
    """(let ((a 1) (b 2)) (+ a b)n)"""
    assert sc_eval("""(let ((a (rule (> 3 5))) (b 2)) (a 8))""") == False
    assert sc_eval("""(let ((a (rule (< 3 5))) (b 2)) (a 8))""") == True

    
    assert sc_eval("""(let ((measure 2)) (> measure 8))""") == False
    # test a simple form of the m> macro
    assert sc_eval("""(let ((measure 2)) (m> 8))""") == False
    #make sure m> doesn't always return False
    assert sc_eval("""(let ((measure 2)) (m> 1))""") == True

    # can we pass an expression into m>
    assert sc_eval("""(let ((measure 2)) (m> (- 5 9)))""") == True

    #rule must be evaluated at a place where measure is defined
    assert sc_eval("""(let ((measure 2))
                           (let ((a (rule (m> 8))))  (a 'unused)))""") == False


    assert sc_eval("""(let ((a (rule-measure (m> 8))))  (a 2))""") == False


def xtest_lambda_arg_handling():
    jlisp_eval, sc_eval = make_interpreter()
    #try to define a lambda that takes no arguments

    # you must specify an argument that the lambda takes, but it isn't
    # necessary to pass that argument when you call the lambda
    assert sc_eval("""(let ((a (lambda foo (> 3 5)))) (a))""") == False
    assert sc_eval("""(let ((a (lambda foo (< 3 5)))) (a))""") == True

    # you can even pass args that the lambda doesn't have arguments for
    assert sc_eval("""(let ((a (lambda foo (< 3 5)))) (a 3))""") == True
    assert sc_eval("""(let ((a (lambda foo (< 3 5)))) (a 3 9))""") == True

def xtest_define_lambda():

    jlisp_eval, sc_eval = make_interpreter()
    # we made a change to define, lets test that it works
    assert sc_eval(
        """(begin
               (define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))
               (fact 3))""") == 6
    assert sc_eval(
        """(begin
               (define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))
               (fact 5))""") == 120

def xtest_define_macro_separate_invocations():
    jlisp_eval, sc_eval = make_interpreter()
    # show how gensym works in a macro
    res = sc_eval(
        """
        (begin
            (define-macro gs-lambda (lambda args
                (let ((w (gensym)))
                    `(begin
                         (display ',w)
                         (let ((,w 20)) (list ',w ,w))))))
        (gs-lambda))""")
    assert res == [Symbol("GENSYM-0"), 20]
    res = sc_eval(
        """
        (begin
        (gs-lambda))""")
    assert res == [Symbol("GENSYM-1"), 20]
    
