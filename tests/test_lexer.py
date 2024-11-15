from svdep.svpp_lexer import mk_lexer

def test_smoke():
    input = """
    `include "abc"
    /** comment */
    // abc
    a
    b
    c
    d
    /** */
    """
    lexer = mk_lexer(debug=True)
    lexer.input(input)

    while tok:=lexer.token():
        print("tok: %s" % str(tok))
