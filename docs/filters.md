# Filter Expressions

Boolean literals `true` and `false` are now recognised in filter expressions
(case-insensitive). They map to Python's ``True`` and ``False`` values.

This support was added after encountering placeholder expressions such as
``True`` in filter CSV files which previously triggered ``NameError`` because
the evaluator treated them as unknown variables.

