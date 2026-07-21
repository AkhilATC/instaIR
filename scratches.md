## LET DSL declarations

LET var = value

[Token('LET', 'LET'), 'identity', Path(root=Identifier(name='ROOT'), parts=[Field(name='source_identity')])]

LHS SIDE - variable

RHS - PATH or CONTAINER
 
------------------
Let(variable='ROOT', value='$ROOT')
--- --- --- --- --- --- --- --- ---
Let(variable='target', value={})
--- --- --- --- --- --- --- --- ---
Let(variable='source', value='$ROOT.data')
--- --- --- --- --- --- --- --- ---
Let(variable='identity', value='$ROOT.source_identity')
--- --- --- --- --- --- --- --- ---
Pop(variable='source', target=['security'])
--- --- --- --- --- --- --- --- ---
Move(source=Path(root=Identifier(name='source'), parts=[Field(name='name')]), destination=Path(root=Identifier(name='target'), parts=[Field(name='_meta'), Field(name='name')]))
--- --- --- --- --- --- --- --- ---
Move(source=Path(root=Identifier(name='source'), parts=[Field(name='characteristics')]), destination=Path(root=Identifier(name='target'), parts=[Field(name='_meta')]))
--- --- --- --- --- --- --- --- ---
Move(source=Path(root=Identifier(name='source'), parts=[Index(name='source', index=0), Field(name='emails')]), destination=Path(root=Identifier(name='target'), parts=[Field(name='_meta')]))
--- --- --- --- --- --- --- --- ---
ForEach(iterable='emails', variable='source', alias='contact', body=[Move(source=Path(root=Identifier(name='contact'), parts=[Field(name='email_address')]), destination=Path(root=Identifier(name='target'), parts=[Field(name='_meta'), Field(name='email')]))])
--- --- --- --- --- --- --- --- ---
Convert(operation='TO_SNAKE_CASE', target='target')



