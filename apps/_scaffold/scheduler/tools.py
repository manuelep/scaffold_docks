import datetime

# from hashlib import md5

# def get_checksum(path):
#     """ Courtesy of: https://stackoverflow.com/a/67412295/1039510 """
#     # with open(path) as file, mmap(file.fileno(), 0, access=ACCESS_READ) as file:
#     #     print(md5(file).hexdigest())
#     # with open(path, 'rb') as file:
#     #     print(md5(file.read()).hexdigest())

#     if isinstance(path, str):
#         with open(path, 'rb') as file:
#             cs = md5(file.read()).hexdigest()
#     else:
#         cs = md5(path.read()).hexdigest()
#     return cs

UTC_TIME = False
now = lambda: UTC_TIME and datetime.datetime.utcnow() or datetime.datetime.now()
