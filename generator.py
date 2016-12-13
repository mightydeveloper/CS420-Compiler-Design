# Symbol table generator implementation
# 20121022 Young Seok Kim
# 20100896 Junho CHA

import ply.yacc as yacc
from lexer import tokens
import logging
# p should be given as program node
import itertools
from AST import *
from SymbolTable import *
import ErrorCollector


# Usage :
# generator = TMachineCodeGenerator()
# areaInstr = Instruction(Instruction.AREA, "MEM")
# generator.addInstruction(areaInstr)

def register(num):
    return "R("+num+")"

def getFromAddress(location):
    return location + "@"

def getFromRegister(num):
    return "R("+num+")@"

class Instruction(object):
    AREA = "AREA"
    MOVE = "MOVE"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    I2F = "I2F"
    FADD = "FADD"
    FSUB = "FSUB"
    FMUL = "FMUL"
    FDIV = "FDIV"
    F2I = "F2I"
    TOZ = "TOZ"
    JMP = "JMP"
    JMPZ = "JMPZ"
    JMPN = "JMPN"
    LAB = "LAB"
    READI = "READI"
    READF = "READF"
    WRITE = "WRITE"

    def __init__(self, instr, arg1, arg2=None, arg3=None):
        self.instr = instr
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def __str__(self):
        outputstr = ""
        if self.instr != "LABEL":
            outputstr += "\t"
        outputstr += self.instr + "\t"
        outputstr += self.arg1
        if self.arg2 is not None:
            outputstr += "\t"+self.arg2
        if self.arg3 is not None:
            outputstr += "\t"+self.arg3
        return outputstr


class TMachineCodeGenerator(object):
    def __init__(self, symtable):
        self.instructions = []
        self.table = symtable
        self.registercnt = 0

    def addInstruction(self, instruction):
        self.instructions.append(instruction)

    def getNewRegister(self):
        self.registercnt += 1
        return self.registercnt - 1

    def getMemRegionWithVaraibleID(self, id, scope):
        # TODO
        pass

    # given rootNodeP should be program node
    def generateInstructions(self, rootNodeP: Program):
        handleProgramDeclist(rootNodeP.DecList)
        # TODO

    # Processes Program's declist and add to the global variables area
    def handleProgramDeclist(self, p: DecList):
        # TODO
        pass

    # Returns the register number where the value of expr is stored after computing.
    def handleExpr(self, p: Expr):
        if p.expr_type == "paren":
            prev = self.handleExpr(p.operand1)
            return prev
        elif p.expr_type == "unop":
            prev = self.handleExpr(p.operand1)
            result_register = self.getNewRegister()
            type = p.return_type()
            if type == "int":
                instr = Instruction(Instruction.SUB, 0, getFromRegister(prev), register(result_register))
            else:
                instr = Instruction(Instruction.FSUB, 0, getFromRegister(prev), register(result_register))
            self.addInstruction(instr)
            return result_register
        elif p.expr_type == "binop":
            op1 = self.handleExpr(p.operand1)
            op2 = self.handleExpr(p.operand2)
            result_register = self.getNewRegister()
            type = p.return_type()
            if p.operator == "+":
                if type == "int":
                    instr = Instruction(Instruction.ADD, getFromRegister(op1), getFromRegister(op2),
                                        register(result_register))
                else:  # float case
                    instr = Instruction(Instruction.FADD, getFromRegister(op1), getFromRegister(op2),
                                        register(result_register))
            elif p.operator == "-":
                if type == "int":
                    instr = Instruction(Instruction.SUB, getFromRegister(op1), getFromRegister(op2),
                                        register(result_register))
                else:  # float case
                    instr = Instruction(Instruction.FSUB, getFromRegister(op1), getFromRegister(op2),
                                        register(result_register))
            elif p.operator == "*":
                if type == "int":
                    instr = Instruction(Instruction.MUL, getFromRegister(op1), getFromRegister(op2),
                                        register(result_register))
                else:  # float case
                    instr = Instruction(Instruction.FMUL, getFromRegister(op1), getFromRegister(op2),
                                        register(result_register))
            elif p.operator == "/":
                if type == "int":
                    instr = Instruction(Instruction.DIV, getFromRegister(op1), getFromRegister(op2),
                                        register(result_register))
                else:  # float case
                    instr = Instruction(Instruction.FDIV, getFromRegister(op1), getFromRegister(op2),
                                        register(result_register))
            elif p.operator == "==":
                # 0 is false. Otherwise true.
                # TODO
                pass
            elif p.operator == "!=":
                # 0 is false. Otherwise true. If they are different, the subtraction will be nonzero.
                if type == "int":
                    instr = Instruction(Instruction.SUB, getFromRegister(op1), getFromRegister(op2),
                                        register(result_register))
                else:
                    instr = Instruction(Instruction.FSUB, getFromRegister(op1), getFromRegister(op2),
                                        register(result_register))
            elif p.operator == "<":
                # TODO
                pass
            elif p.operator == ">":
                # TODO
                pass
            elif p.operator == "<=":
                # TODO
                pass
            elif p.operator == ">=":
                # TODO
                pass
            self.addInstruction(instr)
            return result_register

    def handleSpecialFunctionCall(self, p: Call):
        if p.id == "printf" and len(p.arglist) == 1:
            variableAddr = self.getMemRegionWithVaraibleID() # TODO
            instr = Instruction(Instruction.WRITE, variableAddr)
            self.addInstruction(instr)
        elif p.id == "scanf" and len(p.arglist) == 1:
            variableAddr = self.getMemRegionWithVaraibleID()  # TODO
            if type == "int":
                instr = Instruction(Instruction.READI, variableAddr)
            else:
                instr = Instruction(Instruction.READF, variableAddr)
            self.addInstruction(instr)









