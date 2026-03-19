class Test:
    def __contains__[T](self, item: T) -> T:
        return item
    
    
t = Test()
item: str = '1'
ans = item in t
print(ans)
