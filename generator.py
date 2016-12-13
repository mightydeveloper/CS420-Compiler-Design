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


class TMachineCodeGenerator(object):
    def __init__(self):
        self.instructions = []

    def addInstruction(self, instruction):
        self.instructions.append(instruction)

    def generateInstructions(self, rootnodeP):


