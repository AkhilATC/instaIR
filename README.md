# instaIR
Intermediate representation of transformation grammer 

```text
DSL Script
     │
     ▼
Lexer
     │
     ▼
Parser
     │
     ▼
Concrete AST (Syntax Tree)
     │
     ▼
Semantic Analyzer
     │
     ▼
Execution Plan (IR)
     │
     ├── Python Executor
     ├── Mongo Aggregation Generator
     ├── History Migration Generator
     └── Validation
```
