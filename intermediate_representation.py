from dataclasses import dataclass, field
from typing import List, Optional, Any
from lark import Transformer,Lark
from dataclasses import dataclass

# ------------------------

class Statement:
    pass

class Expression:
    pass

# ------------------------

@dataclass
class Program:
    entity: "Entity"

@dataclass
class Entity:
    name: str
    body: list[Statement]

# ------------------------

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class NewObject(Expression):
    pass

@dataclass
class Path(Expression):
    root: Identifier
    parts: list

@dataclass
class Field:
    name: str

@dataclass
class Index:
    name: str
    index: int

@dataclass
class Wildcard:
    name: str

# ------------------------

@dataclass
class Let(Statement):
    variable: str
    value: Expression

@dataclass
class Move(Statement):
    source: Path
    destination: Path

@dataclass
class Pop(Statement):
    variable:str
    target: List[str] #Path

@dataclass
class Convert(Statement):
    operation: str
    target: Expression

@dataclass
class ForEach(Statement):
    iterable: Path
    variable: str
    body: list[Statement]





class DSLTransformer(Transformer):

    def program(self, items):

        return Program(items[0])

    def entity(self, items):
        print("[IR|🧠]  ENTITY NODE ")
        print(items)
        return Entity(
            name=str(items[0]),
            body=items[1]
        )

    def block(self, items):
        return items

    # -------------------

    def let_stmt(self, items):
        print("[IR|🧠]  LET statement ")
        keyword = str(items[0])
        rhs = str(items[1])
        lhs = items[2]
        expression = ""
        if isinstance(lhs,Path):
            root = lhs.root.name
            parts = lhs.parts
            parts_normalized = [s.name for s in parts]
            parts_normalized.insert(0,f"${root}")
            expression = '.'.join(parts_normalized)
        elif isinstance(lhs,NewObject):
            expression = {}
        return Let(
            variable=str(rhs),
            value=expression
        )

    def move_stmt(self, items):
        print("[IR|🧠]  MOVE statement ")

        return Move(
            source=items[1],
            destination=items[2]
        )

    def pop_stmt(self, items):
        print("[IR|🧠]  POP statement ")
        variable = items[1].root.name
        target_path = [p.name for p in items[1].parts]
        return Pop(variable=variable,target=target_path)

    def convert_stmt(self, items):
        return Convert(
            operation=str(items[0]),
            target=items[1]
        )

    def foreach_stmt(self, items):
        print("[IR|🧠]  FOR LOOP statement ")
        print(items)
        return ForEach(
            iterable=items[0],
            variable=str(items[1]),
            body=items[2]
        )

    # -------------------

    def variable(self, items):
        return Identifier(str(items[0]))

    def new_object(self, _):
        return NewObject()

    # -------------------
    # PATH
    # -------------------

    def root(self, items):
        return Identifier(str(items[-1]))

    def field(self, items):
        return Field(str(items[0]))

    def index(self, items):
        return Index(
            name=str(items[0]),
            index=int(items[1])
        )

    def wildcard(self, items):
        return Wildcard(str(items[0]))

    def path(self, items):
        return Path(
            root=items[0],
            parts=items[1:]
        )

    # -------------------

    def NAME(self, token):
        return str(token)

    def NUMBER(self, token):
        return int(token)

    def STRING(self, token):
        return token[1:-1]



if __name__ == '__main__':
    with open("grammar.lark", "r") as f:
        grammar = f.read()

    parser = Lark(grammar, parser='lalr', start='start')

    from dsl import dsl
    tree = parser.parse(dsl)
    transformer = DSLTransformer()
    result = transformer.transform(tree)
    from pprint import pprint
    from dataclasses import asdict

    pprint(asdict(result))