# from django.test import TestCase
from decimal import Decimal
from functools import reduce

# Create your tests here.
q = [ Decimal('12.00'), Decimal('12.00'), Decimal('12.00'), Decimal('12.00'), Decimal('12.00')]
x = reduce(lambda x,y:x+y,q)
print(x)