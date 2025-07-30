import inspect

def private(func):

    def packager(self, *args, **kwargs):

        caller_frame = inspect.currentframe().f_back

        is_internal = 'self' in caller_frame.f_locals and caller_frame.f_locals['self'].__class__ == self.__class__
        
        if is_internal:

            return func(self, *args, **kwargs)

        else:

            raise PermissionError(f"Private method '{func.__name__}' cannot be called from outsite class!")
        
    return packager

def public(func):

    def packager(self, *args, **kwargs):

        return func(self, *args, **kwargs)
    
    return packager