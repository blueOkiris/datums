import parser.lexer as lexer

class TokenTree:
    def __init__(self, root, children):
        self.root = root
        self.children = children

# <program> ::= { <structure> | <pause> | <res-op> | <assign> }
class Parser:
    @staticmethod
    def tokenTreeStr(tree, tabInd = -1):
        treeStr = ''

        if tree.root.tokenType == lexer.TokenType.Program:
            treeStr += 'Program:'
        else:
            for i in range(tabInd):
                treeStr += '|--'
            treeStr += str(tree.root)
        treeStr += '\n'
        for child in tree.children:
            treeStr += Parser.tokenTreeStr(child, tabInd + 1)

        if tabInd == 0:
            treeStr += '\n'
        
        return treeStr

    # <typedef> ::= <type-def-op> <ident> <int>
    @staticmethod
    def __parseTypeDef(tokens, tokInd):
        index = tokInd

        newTree = TokenTree(
            lexer.Token('Type Def', lexer.TokenType.TypeDef),
            [ TokenTree(tokens[index], []) ]
        )

        index += 1
        assert index < len(tokens), 'Unexpected EOF in typedef after \'#\''
        assert \
            tokens[index].tokenType == lexer.TokenType.Ident, \
            'Expected new type name after \'#\' in typedef'
        newTree.children.append(TokenTree(tokens[index], []))

        index += 1
        assert index < len(tokens), 'Unexpected EOF in typedef after type name'
        assert \
            tokens[index].tokenType == lexer.TokenType.Int, \
            'Expected number after type name in typedef'
        newTree.children.append(TokenTree(tokens[index], []))
        return (index, newTree)

    # <addr>        ::= <l-par> <int> <type-op> <ident> <r-par> 
    #                   { <memb-op> <ident> } <r-par>
    # <doub-addr>   ::= <l-brack> <int> <type-op> <ident> <r-par> 
    #                   { <memb-op> <ident> } <r-brack>
    # <var>         ::= <int> | <addr> | <doub-addr>
    @staticmethod
    def __parseVar(tokens, tokInd):
        index = tokInd

        newTree = TokenTree(lexer.Token('Var', lexer.TokenType.Var), [])
        
        if tokens[index].tokenType == lexer.TokenType.Int:
            newTree.children.append(TokenTree(tokens[index], []))
        elif tokens[index].tokenType == lexer.TokenType.LBrack:
            index += 1
            assert \
                index < len(tokens), \
                'Unexpected EOF in var' \
                    + ' at token index ' + str(index)

            addrTree = TokenTree(
                lexer.Token('Double Addr', lexer.TokenType.DoubleAddr),
                [
                    TokenTree(tokens[index - 1], []),
                    TokenTree(tokens[index], []),
                ]
            )

            index += 1
            assert \
                index < len(tokens), \
                'Unexpected EOF in var before \':\'' \
                    + ' at token index ' + str(index)
            assert \
                tokens[index].tokenType == lexer.TokenType.TypeOp, \
                'Expected \':\' or \')\' in var declaration' \
                    + ' at token index ' + str(index)
            
            index += 1
            assert \
                index < len(tokens), \
                'Unexpected EOF in var after \':\'' \
                    + ' at token index ' + str(index)
            assert \
                tokens[index].tokenType == lexer.TokenType.Ident, \
                'Expected type after \':\' in var declaration' \
                    + ' at token index ' + str(index)
            
            index += 1
            assert \
                index < len(tokens), \
                'Unexpected EOF in var after type' \
                    + ' at token index ' + str(index)
            assert \
                tokens[index].tokenType == lexer.TokenType.RBrack, \
                'Expected \')\' after type in var declaration'
            
            addrTree.children.append(TokenTree(tokens[index - 2], []))
            addrTree.children.append(TokenTree(tokens[index - 1], []))
            addrTree.children.append(TokenTree(tokens[index], []))
            
            newTree.children.append(addrTree)
        elif tokens[index].tokenType == lexer.TokenType.LPar:
            index += 1
            assert \
                index < len(tokens), \
                'Unexpected EOF in var' \
                    + ' at token index ' + str(index)

            addrTree = TokenTree(
                lexer.Token('Addr', lexer.TokenType.Addr),
                [
                    TokenTree(tokens[index - 1], []),
                    TokenTree(tokens[index], [])
                ]
            )

            index += 1
            assert \
                index < len(tokens), \
                'Unexpected EOF in var before \':\'' \
                    + ' at token index ' + str(index)
            assert \
                tokens[index].tokenType == lexer.TokenType.TypeOp, \
                'Expected \':\' or \')\' in var declaration' \
                    + ' at token index ' + str(index)
            
            index += 1
            assert \
                index < len(tokens), \
                'Unexpected EOF in var after \':\'' \
                    + ' at token index ' + str(index)
            assert \
                tokens[index].tokenType == lexer.TokenType.Ident, \
                'Expected type after \':\' in var declaration' \
                    + ' at token index ' + str(index)
            
            index += 1
            assert \
                index < len(tokens), \
                'Unexpected EOF in var after type' \
                    + ' at token index ' + str(index)
            assert \
                tokens[index].tokenType == lexer.TokenType.RPar, \
                'Expected \')\' after type in var declaration'
            
            addrTree.children.append(TokenTree(tokens[index - 2], []))
            addrTree.children.append(TokenTree(tokens[index - 1], []))
            addrTree.children.append(TokenTree(tokens[index], []))

            newTree.children.append(addrTree)
        else:
            assert False, 'Failed to parse var'

        return (index, newTree)

    # <pause> ::= <pause-op> <var>
    @staticmethod
    def __parsePause(tokens, tokInd):
        index = tokInd

        newTree = TokenTree(lexer.Token('Pause', lexer.TokenType.Pause), [])
        opTree = TokenTree(tokens[tokInd], [])
        
        index += 1
        assert \
            index < len(tokens), \
            'Unexpected EOF after pause operator' \
                + ' at token index ' + str(index)
        (index, varTree) = Parser.__parseVar(tokens, index)

        newTree.children.append(opTree)
        newTree.children.append(varTree)        
        return (index, newTree)

    # <assign> ::= <var> <asgn-op> <var> { <var> } <semi>
    @staticmethod
    def __parseAssignment(tokens, tokInd):
        index = tokInd
        newTree = TokenTree(
            lexer.Token('Assignment', lexer.TokenType.Assign), []
        )
        
        (index, varTree) = Parser.__parseVar(tokens, index)
        newTree.children.append(varTree)

        #print(Parser.tokenTreeStr(varTree, 0))

        index += 1
        assert \
            index < len(tokens), \
            'Unexpected EOF after var in assignment' \
                + ' at token index ' + str(index)
        assert \
            tokens[index].tokenType == lexer.TokenType.AssignOp, \
            'Expected \'=,\' \'+=,\' \'-=,\' \'*=,\' \'%=,\' or \'/=\'' \
            + ' in assignment declaration at token #' + str(index)
        newTree.children.append(TokenTree(tokens[index], []))

        index += 1
        assert \
            index < len(tokens), \
            'Unexpected EOF after \'=\'' \
                + ' at token index ' + str(index)
        while tokens[index].tokenType != lexer.TokenType.Semi:
            (index, varTree) = Parser.__parseVar(tokens, index)
            newTree.children.append(varTree)
            index += 1
            assert index < len(tokens), 'Unexpected EOF before \';\''
        newTree.children.append(TokenTree(tokens[index], []))

        return (index, newTree)

    @staticmethod
    def buildProgramTree(tokens):
        program = TokenTree(lexer.Token('Program', lexer.TokenType.Program), [])

        tokInd = 0
        while tokInd < len(tokens):
            if tokens[tokInd].tokenType == lexer.TokenType.TypeDefOp:
                (tokInd, structure) = Parser.__parseTypeDef(tokens, tokInd)
                program.children.append(structure)
            elif tokens[tokInd].tokenType == lexer.TokenType.PauseOp:
                (tokInd, pause) = Parser.__parsePause(tokens, tokInd)
                program.children.append(pause)
            elif tokens[tokInd].tokenType == lexer.TokenType.Resume:
                program.children.append(TokenTree(tokens[tokInd], []))
            else:
                (tokInd, assignment) = Parser.__parseAssignment(tokens, tokInd)
                program.children.append(assignment)
            tokInd += 1

        return program
