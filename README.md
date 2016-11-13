# CS420-Compiler-Design
[CS420] Compiler Design Project

## [Project 1]
### Platform and dependencies
- OS : MacOS Sierra (version 10.12)
- Language : Python 3.5.1 
- External Library : ply 3.9 [http://www.dabeaz.com/ply/ply-3.9.tar.gz]

### Included files
`lexer.py`, `parser.py`, `main.py`, `parser.out`, `README.md`

### Prerequisites
- Install python 3
- Install ply 3.9

### Usage
```sh
$ python main.py -l testfile.c # Lexer test (prints lexer tokens)
$ python main.py -p testfile.c # Parser test (prints state, stack, and action in 퍟parselog.txt)
```

## [Project 2]
### Platform and dependencies
I used same environment as Project 1 except Python language is now 3.5.2

### Included files
`lexer.py`, `parser.py`, `main.py`, `parser.out`, `README.md`, `AST.py`, `SymbolTable.py`

### Prerequisites
- Install python 3
- Install ply 3.9
-
### Usage
```sh
$ python main.py -p testfile.c # Parser test (This will generate tree.txt AST output)
```

