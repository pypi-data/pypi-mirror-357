# infdate

_Python module for date calculations implementing a concept of infinity_

The **Date** class provided in this package wraps the standard library’s
**datetime.date** class and adds the capability to specify dates in positive
(after everything else) or negative (before everything else) infinity,
and to do calculations (add days, or subtract days or other **Date** instances)
with these objects.

For easier usage, differences are expressed as integers (1 = one day)
or floats (inf and -inf _only_).

These capabilities can come handy when dealing with API representations of dates,
eg. in GitLab’s [Personal Access Tokens API].

* * *
[Personal Access Tokens API]: https://docs.gitlab.com/api/personal_access_tokens/