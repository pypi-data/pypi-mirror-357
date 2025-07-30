def autotest(func):
    func.__autotest__ = True
    return func
