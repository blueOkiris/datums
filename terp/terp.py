import enum
import parser.parser as parser
import parser.lexer as lexer

class AssignType(enum.Enum):
    ADD = 0,
    SUB = 1,
    MUL = 2,
    DIV = 3,
    MOD = 4,
    SET = 5

class VirtualMachine:
    def __init__(self, insts):
        self.__instructions = []
        self.__memory = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
        self.types = {
            'long' : 8,
            'int' : 4,
            'short' : 2,
            'char' : 1
        }
        self.paused = False
        self.unPauseAmount = 0

        for i in range(min(2**64 - 1, len(insts) + 1)):
            if i < len(insts):
                assert \
                    insts[i].root.tokenType == lexer.TokenType.Assign \
                        or insts[i].root.tokenType == lexer.TokenType.Pause \
                        or insts[i].root.tokenType == lexer.TokenType.TypeDef \
                        or insts[i].root.tokenType == lexer.TokenType.Resume, \
                    'Unknown top level instruction: ' + str(insts.root[i])
                if insts[i].root.tokenType == lexer.TokenType.TypeDef:
                    self.types[insts[i].children[1].root.source] = \
                        int(insts[i].children[2].root.source, 10)
                else:
                    self.__instructions.append(insts[i])
            else:
                self.__instructions.append(
                    parser.TokenTree(
                        lexer.Token('nop', lexer.TokenType.NoTok), []
                    )
                )

    def getInstruction(self):
        pc = self.getMemory(2, 8)
        self.setMemory(2, 8, pc + 1)

        out = self.getMemory(1, 1)
        if out != 0:
            print(chr(out), end='')
            self.setMemory(1, 1, 0)

        return self.__instructions[pc]
    
    def getMemory(self, ind, size):
        while len(self.__memory) < ind + size:
            self.__memory.append(0)

        newVal = 0
        for i in range(size):
            newVal += self.__memory[ind + i] << (size - i - 1) * 8

        return newVal

    def setMemory(self, ind, size, val):
        while len(self.__memory) < ind + size:
            self.__memory.append(0)
        
        for i in range(size):
            self.__memory[ind + i] = val >> (size - i - 1) * 8
    
    def __str__(self):
        stateStr = \
            'Vm State: { len(instructions) = ' + str(len(self.__instructions)) \
                + ', len(memory) = ' + str(len(self.__memory)) \
                + ', len(types) = ' + str(len(self.types)) \
                + ', paused = ' + str(self.paused) \
                + ', unPauseAmmount = ' + str(self.unPauseAmount) + ' }'
        
        memStr = '\nMem {'
        for i in range(len(self.__memory)):
            if i % 10 == 0:
                memStr += '\n    '
            memStr += ' ' + str(self.__memory[i])
        memStr += '\n}'
        
        return stateStr + memStr

class Interpreter:
    @staticmethod
    def run(program, debug = False):
        instructions = []
        for instruction in program.children:
            instructions.append(instruction)
        vm = VirtualMachine(instructions)
        
        instruction = vm.getInstruction()
        while instruction.root.tokenType != lexer.TokenType.NoTok:            
            if instruction.root.tokenType == lexer.TokenType.Pause:
                vm.paused = True
                
                var = instruction.children[1]
                if var.children[0].root.tokenType == lexer.TokenType.Int:
                    vm.unPauseAmount = int(
                        var.children[0].root.source, 10
                    )
                elif var.children[0].root.tokenType == lexer.TokenType.Addr:
                    addr = int(
                        var.children[0].children[1].root.source, 10
                    )
                    vm.unPauseAmount = vm.getMemory(
                        addr, 
                        vm.types[var.children[0].children[3].root.source]
                    )
                elif \
                var.children[0].root.tokenType == lexer.TokenType.DoubleAddr:
                    addr1 = int(
                        var.children[0].children[1].root.source, 10
                    )
                    valueAddr = vm.getMemory(
                        addr1, 
                        vm.types[var.children[0].children[3].root.source]
                    )
                    vm.unPauseAmount = vm.getMemory(
                        valueAddr, 
                        vm.types[var.children[0].children[3].root.source]
                    )
                else:
                    assert False, 'Unexpected var type in skip statement'
                
                if vm.unPauseAmount <= 0:
                    vm.paused = False
            elif instruction.root.tokenType == lexer.TokenType.Resume:
                if vm.unPauseAmount > 0:
                    vm.unPauseAmount -= 1
                
                if vm.unPauseAmount <= 0:
                    vm.paused = False
            elif not vm.paused:
                var = instruction.children[0]
                assert \
                    var.children[0].root.tokenType == lexer.TokenType.Addr, \
                    'Cannot set direct integer value!'
                
                addr = int(var.children[0].children[1].root.source, 10)
                size = vm.types[var.children[0].children[3].root.source]

                operator = instruction.children[1]
                operation = AssignType.SET
                if operator.root.source == '+=':
                    operation = AssignType.ADD
                elif operator.root.source == '-=':
                    operation = AssignType.SUB
                elif operator.root.source == '*=':
                    operation = AssignType.MUL
                elif operator.root.source == '/=':
                    operation = AssignType.DIV
                elif operator.root.source == '%=':
                    operation = AssignType.MOD

                byteList = []
                varList = instruction.children[2:len(instruction.children) - 1]
                for setVar in varList:
                    if setVar.children[0].root.tokenType == lexer.TokenType.Int:
                        byteList.append(
                            int(
                                setVar.children[0].root.source, 10
                            )
                        )
                    elif \
                    setVar.children[0].root.tokenType == lexer.TokenType.Addr:
                        addr1 = int(
                            setVar.children[0].children[1].root.source, 10
                        )

                        if addr1 == 0:
                            strInput = input()
                            for i in range(len(strInput)):
                                byteList.append(ord(strInput[i]))
                        else:
                            byteList.append(
                                vm.getMemory(
                                    addr1, 
                                    vm.types[
                                        setVar.children[0].children[3].root.source
                                    ]
                                )
                            )
                    elif setVar.children[0].root.tokenType \
                    == lexer.TokenType.DoubleAddr:
                        addr1 = int(
                            setVar.children[0].children[1].root.source, 10
                        )
                        valueAddr = 0
                        if addr1 == 0:
                            strInput = input()
                            valueAddr = int(strInput, 10)
                        else:
                            valueAddr = vm.getMemory(
                                addr1, 
                                vm.types[
                                    setVar.children[0].children[3].root.source
                                ]
                            )
                        byteList.append(
                            vm.getMemory(
                                valueAddr, 
                                vm.types[
                                    setVar.children[0].children[3].root.source
                                ]
                            )
                        )
                    else:
                        assert False, 'Unexpected var type in skip statement'
                #print(byteList)
                assert \
                    len(byteList) <= size, \
                    'Incorrect size provide in assignment'
                
                if operation == AssignType.ADD:
                    for i in range(len(byteList)):
                        byteList[i] = vm.getMemory(addr + i, 1) + byteList[i]
                elif operation == AssignType.SUB:
                    for i in range(len(byteList)):
                        byteList[i] = vm.getMemory(addr + i, 1) - byteList[i]
                elif operation == AssignType.MUL:
                    for i in range(len(byteList)):
                        byteList[i] = vm.getMemory(addr + i, 1) * byteList[i]
                elif operation == AssignType.DIV:
                    for i in range(len(byteList)):
                        byteList[i] = vm.getMemory(addr + i, 1) / byteList[i]
                elif operation == AssignType.MOD:
                    for i in range(len(byteList)):
                        byteList[i] = vm.getMemory(addr + i, 1) % byteList[i]

                ind = 0
                for byte in byteList:
                    vm.setMemory(addr + ind, 1, byte)
                    ind += 1
                if len(byteList) < size:
                    for i in range(size - len(byteList)):
                        vm.setMemory(addr + ind + i, 1, 0)

            if debug:
                print(str(vm))
            instruction = vm.getInstruction()
            