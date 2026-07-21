from dataclasses import dataclass, field
from typing import List, Optional, Any
from lark import Transformer,Lark
from dataclasses import dataclass
from abc import ABC, abstractmethod
import re

FunctionRegistry = {}
# ------------------------
class Operation(ABC):
    @abstractmethod
    def execute(self, context):
        pass

class MoveOperation(Operation):

    def __init__(self,
                 source_variable,
                 target_variable,
                 source_path,
                 target_path):
        print("MOVE OPERATION [🪏]")
        self.source_variable = source_variable
        self.target_variable = target_variable
        self.source_path = source_path
        self.target_path = target_path

    def execute(self, context):
        self.source_path = '.'.join(self.source_path)
        self.target_path = '.'.join(self.target_path)
        if (
                self.source_variable in context.variables
                and self.target_variable in context.variables
        ):
            temp_value = context.safe_get(context.variables[self.source_variable],self.source_path)
            ExecutionContext.safe_set(context.variables[self.target_variable], self.target_path,temp_value)





class PopOperation(Operation):

    def __init__(self, variable,path):
        print("POP OPERATION [🥤]")
        self.variable = variable
        self.path = path

    def execute(self, context):
        source_variable = self.variable
        pop_path = '.'.join(self.path)
        if source_variable in context.variables:
            context.pop_context_variable(source_variable,pop_path)

class LetOperation(Operation):

    def __init__(self, name, expression):
        print("LET OPERATION [🥡]")
        self.name = name
        self.expression = expression

    def execute(self, context):
        context.set_context_variable(self.name,self.expression)



class DefaultOperation(Operation):

    def __init__(self, assignments):
        self.assignments = assignments

    def execute(self, context):
        for target, expr in self.assignments:
            if context.get(target) is None:
                context.set(target, expr.evaluate(context))

class ConvertOperation(Operation):

    def __init__(self, function_name, source_path, target_path):
        self.function_name = function_name
        self.source_path = source_path
        self.target_path = target_path

    def execute(self, context):
        value = context.get(self.source_path)
        value = FunctionRegistry.execute(self.function_name, value)
        context.set(self.target_path, value)

class ForEachOperation(Operation):

    def __init__(self, variable, iterable, operations, alias):
        print("FOR-LOOP OPERATION [🎛️]")
        self.iterable = iterable
        self.variable = variable
        self.operations = operations
        self.alias = alias

    def execute(self, context):
        print("variable = ",self.variable)
        print("iterable = ",self.iterable)
        print("operations = ",self.operations)
        print("alias = ",self.alias)

        # set alias as new array container

        context.set_context_variable(self.alias, [])
        iterable = context.safe_get(context.variables[self.variable], self.iterable) or []
        for each in iterable:
            for op in self.operations:
                if hasattr(op,"transformer"):
                    op.transformer.execute(context)

        # items = context.get(self.iterable)
        #
        # for item in items:
        #     context.variables[self.variable] = item
        #
        #     for op in self.operations:
        #         op.execute(context)

class Statement:
    pass

class Expression:
    pass

# ------------------------

@dataclass
class Program:
    source_type:str
    actions: any

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
    transformer: LetOperation

@dataclass
class Move(Statement):
    source: Path
    destination: Path
    transformer: MoveOperation


@dataclass
class Pop(Statement):
    variable:str
    target: List[str] #Path
    transformer: PopOperation

@dataclass
class Convert(Statement):
    operation: str
    target: Expression

@dataclass
class ForEach(Statement):
    iterable: Path
    variable: str
    alias: str
    body: list[Statement]
    transformer: ForEachOperation


class DSLTransformer(Transformer):

    def program(self, items):
        print("[IR|🧠]  PROGRAM NODE ")

        return Program(
            source_type=items[0].name,
            actions=items[0].body
        )

    def entity(self, items):
        print("[IR|🧠]  ENTITY NODE ")
        return Entity(
            name=str(items[1].lower()),
            body=items[2]
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
            value=expression,
            transformer=LetOperation(rhs,expression)
        )

    def move_stmt(self, items):
        print("[IR|🧠]  MOVE statement ")
        s = items[1]
        d = items[2]
        source_variable = s.root.name
        target_variable = d.root.name
        source_path = [p.name for p in s.parts]
        target_path = [p.name for p in d.parts]
        return Move(
            source= s,
            destination= d,
            transformer= MoveOperation(
                source_variable=source_variable,
                target_variable=target_variable,
                source_path=source_path,
                target_path=target_path)
        )

    def pop_stmt(self, items):
        print("[IR|🧠]  POP statement ")
        variable = items[1].root.name
        target_path = [p.name for p in items[1].parts]
        return Pop(variable=variable,
                   target=target_path,
                   transformer=PopOperation(
                                                variable=variable,
                                                path=target_path
                                            )
                   )

    def convert_stmt(self, items):
        print("[IR|🧠]  CONVERT statement ")
        map_function = items[1]
        target = items[2]
        variable = target.root.name
        return Convert(
            operation=map_function,
            target=variable,
        )

    def foreach_stmt(self, items):
        print("[IR|🧠]  FOR LOOP statement ")
        variable = items[1].root.name
        iterable = '.'.join([s.name for s in items[1].parts])

        return ForEach(
            iterable=iterable,
            variable=variable,
            alias=str(items[3]),
            body=items[4],
            transformer=ForEachOperation(
                variable=variable,
                iterable=iterable,
                operations=items[4],
                alias=str(items[3])
            )
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

class CreateExecutionPlan:
    def __init__(self):
        self.source_type = None
        self.operations = []



class ExecutionContext:

    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.variables = {}
        self.emits = []
        self.db_configurations = []

    @staticmethod
    def safe_get(data, path, default=None):
        current = data

        # Split into tokens: "root[0].name" -> ["root", "[0]", "name"]
        tokens = re.findall(r'[^.\[\]]+|\[\d+\]', path)

        for token in tokens:
            try:
                if token.startswith("["):
                    index = int(token[1:-1])
                    current = current[index]
                else:
                    current = current[token]
            except (KeyError, IndexError, TypeError):
                return default

        return current

    @staticmethod
    def safe_pop(data, path, default=None):

        current = data

        # Split into tokens: "root[0].name" -> ["root", "[0]", "name"]
        tokens = re.findall(r'[^.\[\]]+|\[\d+\]', path)

        if not tokens:
            return default

        # Traverse to the parent
        for token in tokens[:-1]:
            try:
                if token.startswith("["):
                    current = current[int(token[1:-1])]
                else:
                    current = current[token]
            except (KeyError, IndexError, TypeError):
                return default

        # Pop the final element
        last = tokens[-1]
        try:
            if last.startswith("["):
                index = int(last[1:-1])
                return current.pop(index)  # list
            else:
                return current.pop(last, default)  # dict
        except (AttributeError, IndexError, TypeError):
            return default

    @staticmethod
    def safe_set(data, path, value):
        current = data

        # "_meta.n" -> ["_meta", "n"]
        tokens = re.findall(r'[^.\[\]]+|\[\d+\]', path)

        for token in tokens[:-1]:
            if token.startswith("["):
                index = int(token[1:-1])

                while len(current) <= index:
                    current.append({})

                if current[index] is None:
                    current[index] = {}

                current = current[index]
            else:
                if token not in current or not isinstance(current[token], dict):
                    current[token] = {}

                current = current[token]

        last = tokens[-1]
        if last.startswith("["):
            index = int(last[1:-1])
            while len(current) <= index:
                current.append(None)
            current[index] = value
        else:
            current[last] = value

    def set_context_variable(self,variable_name,value):
        assign_value = None
        if value == "$ROOT":
            assign_value = self.source
        elif isinstance(value, dict) and not value:
            assign_value = {}
        elif isinstance(value, list) and not value:
            assign_value = []
        elif value.startswith("$ROOT."):
            root = self.variables['ROOT']
            path = value.replace('$ROOT.','')
            assign_value = ExecutionContext.safe_get(root,path=path)

        self.variables[variable_name] = assign_value

    def pop_context_variable(self,variable_name,path):
        ExecutionContext.safe_pop(self.variables[variable_name],path)

class Executor:
    def __init__(self,plan):
        self.plan =  plan

    def execute(self,source_document):
        context = ExecutionContext(
            source=source_document,
            target={}
        )

        for operation in self.plan.operations:
            print(f"operation = {operation}")
            if hasattr(operation,"transformer"):
                operation.transformer.execute(context)

            # print("FINALIZE : context")

            print("======= FINAL =========")
            print(context.variables.get('target'))
            # operation.execute(context)

        return context.target

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
    source_type = result.source_type
    operations = result.actions

    execution_plan = CreateExecutionPlan()
    execution_plan.source_type = source_type # source Type
    execution_plan.operations = operations # Operations

    executor = Executor(execution_plan)

    from data import d
    for i in [d]:
        n  = executor.execute(i)
        # print(n)





