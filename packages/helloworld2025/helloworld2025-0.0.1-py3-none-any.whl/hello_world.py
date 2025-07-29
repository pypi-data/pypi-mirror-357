def day_say_hello(Name=None):
    if Name is None:
        print('Hello,World!')
    else:
        print(f'Hello,{Name}!')

day_say_hello()
day_say_hello('Everyone')