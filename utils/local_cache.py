import time


class Data:
    def __init__(self, value, expire=None):
        self._value = value
        self._expire_time = expire + time.time() if expire else None

    def set_expire(self, expire):
        self._expire_time = expire + time.time() if expire else None

    def get(self):
        is_expire = False
        if self._expire_time:
            if time.time() > self._expire_time:
                self._value = None
                is_expire = True
        return self._value, is_expire


class Cache:
    def __init__(self, db=0):
        self._db = db if db is None else 0
        self._cache = {}
        self._cap = 0

    def get(self, key):
        data_obj = self._cache.get(key)
        if data_obj:
            data, is_expire = data_obj.get()
            if is_expire:
                self.remove(key)
                self._cap -= 1
            return data
        return None

    @property
    def length(self):
        return self._cap

    def set(self, key, obj, expire=None):
        data_obj = Data(obj, expire=expire)
        self._cap += 1
        self._cache[key] = data_obj

    def remove(self, key):
        if key in self._cache:
            self._cap -= 1
            return self._cache.pop(key)
        return None

    def expire(self, key, expire):
        if key in self._cache:
            data_obj = self._cache.get(key)
            data_obj.set_expire(expire)
            return True
        return False


cache = Cache()

# if __name__ == '__main__':
#     cache.set("1", "a", 5)
#     for i in range(15):
#         print(i, "data", cache.get("1"))
#         if i == 3:
#             cache.expire("1", 3)
#         time.sleep(1)
