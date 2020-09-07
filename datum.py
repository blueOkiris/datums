#!/usr/bin/env python3

import sys
import parser.lexer as lex
import parser.parser as parser
import terp.codegen as codegen

def main():
    if len(sys.argv) < 2:
        print('No file name provided!')
    elif len(sys.argv) > 3:
        print('Too many arguments provided')
    else:
        debug = False
        direct = False

        if len(sys.argv) > 2:
            if sys.argv[2] == '--debug':
                debug = True
            else:
                print('Failed to parse ' + sys.argv[2] + ' - debug not on')

        try:
            programFile = open(sys.argv[1], 'r')
            code = programFile.read()
            programFile.close()

            tokens = lex.Lexer.lexTokens(code)
            if debug:
                counter = 0
                for tok in tokens:
                    print(str(counter) + ' : ' + str(tok))
                    counter += 1
                print('')

            ast = parser.Parser.buildProgramTree(tokens)
            if debug:
                print(parser.Parser.tokenTreeStr(ast))
            
            pythonCode = codegen.Translater.translate(ast, debug = debug)
            if debug:
                print(pythonCode)
            exec(pythonCode)
        except FileNotFoundError:
            print('Could not find file')

if __name__ == '__main__':
    main()