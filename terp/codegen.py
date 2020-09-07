import parser.lexer as lexer

class Translater:
    @staticmethod
    def translate(ast, instIndex = 0, debug = False):
        progStr = ''

        if ast.root.tokenType == lexer.TokenType.Program:
            progStr += 'class VirtualMachine:\n'
            progStr += '    def __init__(self):\n'
            progStr += '        self.programCounter = 0\n'
            progStr += '        self.instructions = []\n'
            progStr += '        self.memory = []\n'
            progStr += '        for i in range(256):\n'
            progStr += '            self.memory.append(0)\n'
            progStr += '        self.paused = False\n'
            progStr += '        self.unPauseAmount = 0\n'
            progStr += '        self.types = {\n'
            progStr += '            \'long\' : 8,\n'
            progStr += '            \'int\' : 4,\n'
            progStr += '            \'short\' : 2,\n'
            progStr += '            \'char\' : 1\n'
            progStr += '        }\n'
            progStr += '    def getMemory(self, ind, size):\n'
            progStr += '        newVal = 0\n'
            progStr += '        for i in range(size):\n'
            progStr += '            newVal += self.memory[ind + i] << ' \
                + '(size - i - 1) * 8\n'
            progStr += '        return newVal\n'
            progStr += '    def setMemory(self, ind, size, val):\n'
            progStr += '        if ind == 0:\n'
            progStr += '            return\n'
            progStr += '        elif ind == 1:\n'
            progStr += '            print(chr(val), end = \'\')\n'
            progStr += '            return\n'
            progStr += '        for i in range(size):\n'
            progStr += '            self.memory[ind + i] = val >> ' \
                + '(size - i - 1) * 8\n'
            progStr += '        if ind >= 2 and ind <= 9:\n'
            progStr += \
                '            self.programCounter = self.getMemory(2, 8)\n'
            progStr += '    def resume(self):\n'
            progStr += '        if self.unPauseAmount > 0:\n'
            progStr += '            self.unPauseAmount -= 1\n'
            progStr += '        if self.unPauseAmount <= 0:\n'
            progStr += '            self.paused = False\n'
            progStr += '    def pause(self, amount):\n'
            progStr += '        self.paused = True\n'
            progStr += '        self.unPauseAmount = amount\n'
            progStr += '        if self.unPauseAmount <= 0:\n'
            progStr += '            self.paused = False\n'
            
            progStr += '\n'
            ind = 0
            for instruction in ast.children:
                progStr += Translater.translate(instruction, ind)
                ind += 1

            progStr += '\n    def run(self):\n'
            ind = 0
            for instruction in ast.children:
                progStr += '        self.instructions.append(self.inst_' + \
                    str(ind) + ')\n'
                ind += 1
            progStr += \
                '        while self.programCounter < len(self.instructions):\n'
            progStr += \
                '            curInst = self.instructions[self.programCounter]\n'
            progStr += '            curInst()\n'
            progStr += '            self.programCounter += 1\n\n'

            if debug:
                progStr += '            print(\'Machine State: {\')\n'
                progStr += '            print(\'    [\')\n'
                progStr += '            for i in range(len(self.memory)):\n'
                progStr += '                if i % 32 == 0:\n'
                progStr += '                    print()\n'
                progStr += \
                    '                    print(\'        \', end = \'\')\n'
                progStr += '                print(\' \', end = \'\')\n'
                progStr += '                if i < 2:\n'
                progStr += '                    print(\'-\', end = \'\')\n'
                progStr += '                else:\n'
                progStr += \
                    '                    print(self.memory[i], end = \'\')\n'
                progStr += '            print(\'\\n    ], PC =\', end = \'\')\n'
                progStr += \
                    '            print(\' \' + str(self.programCounter)' \
                    + ' + \',\')\n'
                progStr += \
                    '            print(\'    Paused = \' + str(self.paused))\n'
                progStr += '            print(\'}\')\n'
                progStr += '            input()\n'
            progStr += '\nvm = VirtualMachine()\n'
            progStr += 'vm.run()\n'
        else:
            progStr = '    def inst_' + str(instIndex) + '(self):\n'

            if ast.root.tokenType == lexer.TokenType.Pause:

                var = ast.children[1]
                if var.children[0].root.tokenType == lexer.TokenType.Int:
                    progStr += \
                        '        self.pause(' + var.children[0].root.source \
                            + ')\n'
                elif var.children[0].root.tokenType == lexer.TokenType.Addr:
                    addr = var.children[0].children[1].root.source
                    size = var.children[0].children[3].root.source
                    progStr += \
                        '        self.pause(self.getMemory(' + addr \
                            + ', self.types[\'' + size + '\']))\n'
                elif \
                var.children[0] .root.tokenType == lexer.TokenType.DoubleAddr:
                    addr = var.children[0].children[1].root.source
                    size = var.children[0].children[3].root.source

                    addr = var.children[0].children[1].root.source
                    size = var.children[0].children[3].root.source
                    progStr += \
                        '        self.pause(\n    self.getMemory(\n' \
                            + '            ' \
                            + 'self.getMemory(' + addr + ', self.types[\'' \
                            + size + '\']),\n' + '            self.types[\'' \
                            + size + '\']\n    )\n)\n'
                else:
                    assert False, 'Unexpected var type in skip statement'
            elif ast.root.tokenType == lexer.TokenType.Resume:
                progStr += '        self.resume()\n'
            elif ast.root.tokenType == lexer.TokenType.TypeDef:
                progStr += \
                    '        self.types[\'' + ast.children[1].root.source \
                        + '\'] = ' + ast.children[2].root.source + '\n'
            elif ast.root.tokenType == lexer.TokenType.Assign:
                var = ast.children[0]
                addr = var.children[0].children[1].root.source
                size = var.children[0].children[3].root.source
                varList = ast.children[2:len(ast.children) - 1]

                progStr += '        if not self.paused:\n'
                if ast.children[1].root.source != '=':
                    progStr += \
                        '            curVal = self.getMemory(' + addr \
                            + ', self.types[\'' + size + '\'])\n'
                
                for i in range(len(varList)):
                    token = varList[i].children[0]
                    if token.root.tokenType == lexer.TokenType.Int:
                        progStr += \
                            '            newMem = ' + token.root.source + '\n'
                        if ast.children[1].root.source != '=':
                            progStr += \
                                '            newMem = curVal ' \
                                    + ast.children[1].root.source[0] \
                                    + ' newMem\n'
                        progStr += \
                            '            self.setMemory(' + addr + ' + ' \
                                + str(i) + ', 1, newMem)\n'
                    elif token.root.tokenType == lexer.TokenType.Addr:
                        readAddr = token.children[1].root.source
                        readSize = token.children[3].root.source

                        if readAddr == '0':
                            progStr += '            strInp = input()\n'
                            progStr += \
                                '            for i in range(len(strInp)):\n'
                            progStr += \
                                '                self.setMemory(' \
                                    + addr + ' + ' + str(i) \
                                    + ' + i, 1, ord(strInp[i]))\n'
                        else:
                            progStr += '            newMem = self.getMemory(' \
                                + readAddr + ', self.types[\'' + readSize \
                                + '\'])\n'

                            if ast.children[1].root.source != '=':
                                progStr += \
                                    '            newMem = curVal ' \
                                        + ast.children[1].root.source[0] \
                                        + ' newMem\n'
                            progStr += \
                                '            self.setMemory(' + addr + ' + ' \
                                    + str(i) + ', self.types[\'' \
                                    + readSize + '\'], newMem)\n'
                    elif token.root.tokenType == lexer.TokenType.DoubleAddr:
                        readAddr = token.children[1].root.source
                        readSize = token.children[3].root.source

                        progStr += '            addr = 0\n'

                        if readAddr == '0':
                            progStr += '            strInp = input()\n'
                            progStr += \
                                '            for i in range(len(strInp)):\n'
                            progStr += \
                                '                addr = self.getMemory(' \
                                    + 'ord(strInp[i]) + i, 1)\n'
                        else:
                            progStr += '            addr = self.getMemory(' \
                                + readAddr + ', self.types[\'' + readSize \
                                + '\'])\n'
                        
                        progStr += '            newMem = self.getMemory(' \
                            + 'addr, self.types[\'' + readSize + '\'])\n'

                        if ast.children[1].root.source != '=':
                            progStr += \
                                '            newMem = curVal ' \
                                    + ast.children[1].root.source[0] \
                                    + ' newMem\n'
                        progStr += \
                            '            self.setMemory(' + addr + ' + ' \
                                + str(i) + ', self.types[\'' \
                                + readSize + '\'], newMem)\n'
                    else:
                        assert False, 'Unexpected var type in skip statement'
            else:
                progStr += '        pass\n'

        return progStr
    