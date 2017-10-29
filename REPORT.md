# Implimentation Report

## Technical Decisions

### Name of custom command for import

Name of custom command for import is changed to "import\_data".
This is because "import" is reserved word, and it causes an following error for my test implementation.

```
Traceback (most recent call last):
  File "/usr/local/lib/python2.7/unittest/loader.py", line 254, in _find_tests
    module = self._get_module_from_name(name)
  File "/usr/local/lib/python2.7/unittest/loader.py", line 232, in _get_module_from_name
    __import__(name)
  File "/service/dashboard/api/tests.py", line 8
    from consumption.management.commands.import import import_user, import_consumption
                                              ^
SyntaxError: invalid syntax
```


### DB

Sqlite3 is too slow for this kind of service.
PostgreSQL will be better:)


### Docker

Docker will help you preparing environments.
If docker is already installed, you are ready for build & deploy!


### Summary visualization

Summary is visualized by daily summarized data.
If api returns all timestamp data, it will takes many time to process.
For all period visualization, this will be sufficient for granularity.


### Authentication

No Authentication is implemented.


### Summary calculation

Calcuration in client(for table and chart) is done in synchronous manner.


### Validation

API arguments are not validated in detail.
For production, it should be done more carefully.


## Problems

### Consumption data type

FloatField was used to store consumption. But float will cause errors in calculations.
```
>>> 0.1 + 0.1 + 0.1 == 0.3
False
>>> sum([0.1 for _ in range(100000)])
10000.000000018848
```

Decimal is useful.
```
>>> decimal.Decimal("0.1") + decimal.Decimal("0.1") + decimal.Decimal("0.1") == decimal.Decimal("0.3")
True
>>> sum([decimal.Decimal("0.1") for _ in range(100000)])
Decimal('10000.0')
```

But it is too slow.
```
import decimal
import time

a1 = [0.1 for _ in range(100000)]
a2 = [decimal.Decimal("0.1") for _ in range(100000)]

t0 = time.time()
sum(a1)
print "float: {}".format(time.time() - t0)

t1 = time.time()
sum(a2)
print "decimal: {}".format(time.time() - t1)

# float: 0.000397920608521
# decimal: 1.02504205704
```

If we know that consumption data is up to a first decimal place, we can make the data 10 times and save it as an integer.
```
>>> int(0.1 * 10) + int(0.1 * 10) + int(0.1 * 10) == int(0.3 * 10)
True
>>> sum([int(0.1 * 10) for _ in range(100000)]) / 10.0
10000.0
```

So, IntegerField may be better for saving consumption.


### Data duprication

Dupricated data was found in consumption files.
It is also assumed that there may be data which is duplicated with data already in the DB.
What is the desirable handling?


### Fail to connect to DB

Immediately after DB docker image start up, connection to DB could be failed.

