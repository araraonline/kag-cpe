"""
This is the package for specifying custom department behavior. Each
module (py file) should represent of a single department.

The naming of the module should be:

    dept{name}.py

Where {name} is the name of the department without dashes. E.g.
'3700027' for the Austin Police Department.

Loading is done automatically by the Department class:

>>> # if dept3700027.py exists
>>> Department('37-00027')
Department3700027('37-00027')
"""
