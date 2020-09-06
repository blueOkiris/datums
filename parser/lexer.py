import enum

class TokenType(enum.Enum):
    Semi = 0
    LPar = 1
    RPar = 2
    LBrack = 18
    RBrack = 19
    PauseOp = 3
    AssignOp = 4
    TypeOp = 5
    #MemberOp = 6
    TypeDefOp = 7
    Resume = 8
    Int = 9
    Ident = 10

    DoubleAddr = 20
    Addr = 11
    Var = 12
    Assign = 13
    Pause = 14
    TypeDef = 15
    MemberDef = 16
    Program = 17
    NoTok = 21

class Token:
    def __init__(self, source, tokenType):
        self.source = source
        self.tokenType = tokenType
    
    def __str__(self) -> str:
        return 'Token: { \'' + self.source + '\', ' + str(self.tokenType) + ' }'

class Lexer:
    @staticmethod
    def __isDigit(char):
        return char in '0123456789'
    
    @staticmethod
    def __isAlpha(char):
        return char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    
    @staticmethod
    def __isWhiteSpace(char):
        return char in ' \r\n\t'

    @staticmethod
    def __lexInteger(code, charInd):
        index = charInd
        integerString = ''

        while index < len(code) and Lexer.__isDigit(code[index]):
            integerString += code[index]
            index += 1
        
        return (index - 1, Token(integerString, TokenType.Int))

    @staticmethod
    def __lexIdentifier(code, charInd):
        index = charInd
        integerString = ''

        while index < len(code) and (
            Lexer.__isDigit(code[index]) or Lexer.__isAlpha(code[index])
            or code[index] == '_'
        ):
            integerString += code[index]
            index += 1
        
        return (index - 1, Token(integerString, TokenType.Ident))

    # Basic tokens (others used in parser):
    # <semi>        ::= ';'
    # <l-par>       ::= '('
    # <r-par>       ::= ')'
    # <l-brack>     ::= '['
    # <r-brack>     ::= ']'
    # <pause-op>    ::= '!'
    # <asgn-op>     ::= '=' | '+=' | '-=' | '*=' | '/=' | '%='
    # <type-op>     ::= ':'
    # //<memb-op>     ::= '.'
    # <type-def-op> ::= '#'
    # <resume>      ::= '>'
    # <int>         ::= /[0-9]+/
    # <ident>       ::= /[_A-Za-z][_A-Za-z0-9]*/
    @staticmethod
    def lexTokens(code):
        tokens = []
        charInd = 0
        while charInd < len(code):
            if Lexer.__isWhiteSpace(code[charInd]):
                charInd += 1
                continue
            elif code[charInd] == ';':
                tokens.append(Token(code[charInd], TokenType.Semi))
            elif code[charInd] == '(':
                tokens.append(Token(code[charInd], TokenType.LPar))
            elif code[charInd] == ')':
                tokens.append(Token(code[charInd], TokenType.RPar))
            elif code[charInd] == '[':
                tokens.append(Token(code[charInd], TokenType.LBrack))
            elif code[charInd] == ']':
                tokens.append(Token(code[charInd], TokenType.RBrack))
            elif code[charInd] == '!':
                tokens.append(Token(code[charInd], TokenType.PauseOp))
            elif code[charInd] == '=':
                tokens.append(Token(code[charInd], TokenType.AssignOp))
            elif charInd + 1 < len(code) and code[charInd + 1] == '=' \
            and (
                code[charInd] == '+' or code[charInd] == '-'
                or code[charInd] == '*' or code[charInd] == '/'
                or code[charInd] == '%'
            ):
                tokens.append(
                    Token(code[charInd:charInd + 2], TokenType.AssignOp)
                )
                charInd += 1
            elif code[charInd] == ':':
                tokens.append(Token(code[charInd], TokenType.TypeOp))
            #elif code[charInd] == '.':
            #    tokens.append(Token(code[charInd], TokenType.MemberOp))
            elif code[charInd] == '#':
                tokens.append(Token(code[charInd], TokenType.TypeDefOp))
            elif code[charInd] == '>':
                tokens.append(Token(code[charInd], TokenType.Resume))
            elif code[charInd] == '=':
                tokens.append(Token(code[charInd], TokenType.AssignOp))
            elif Lexer.__isDigit(code[charInd]):
                (charInd, newInt) = Lexer.__lexInteger(code, charInd)
                tokens.append(newInt)
            elif Lexer.__isAlpha(code[charInd]) or code[charInd] == '_':
                (charInd, newIdent) = Lexer.__lexIdentifier(code, charInd)
                tokens.append(newIdent)
            charInd += 1
        return tokens
