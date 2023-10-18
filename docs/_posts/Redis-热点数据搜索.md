# Redis-热点数据搜索
```

def prefix_wrapper(fun):
    @functools.wraps(fun)
    def wrapper(self, name, *args, **kwargs):
        return fun(self, self.prefix + name, *args, **kwargs)
    return wrapper


class PrefixMinIn(object):

    @property
    def prefix(self):
        return "fuxi:"

class SugManager(PrefixMinIn):
    """
    test环境下的redis 版本为3
    线上环境的版本为4
    redis 版本太低, 删除的时候不能使用ZPOPMIN 命令
    """
    lua_add_sug_key = None
    ADD_SUG_KEY_SCRIPT = """
        local token = redis.call('zadd', KEYS[1], KEYS[2], KEYS[3])
        
        local count = redis.call('zcard', KEYS[1])
        local number_capacity = tonumber(ARGV[1])
        if count <= number_capacity then
            return
        end
        local need_to_del = count - number_capacity
        redis.call('ZREMRANGEBYRANK', KEYS[1], 0, need_to_del - 1)
        return
    """

    def __init__(self, capacity=10, json_type=True):
        self.redis = RedisTool()
        self.capacity = capacity
        self.register_scripts()
        self.json_type = json_type

    def register_scripts(self):
        cls = self.__class__
        client = self.redis.conn
        if cls.lua_add_sug_key is None:
            cls.lua_add_sug_key = client.register_script(cls.ADD_SUG_KEY_SCRIPT)

    @prefix_wrapper
    def zadd(self, key_name, value, score=None):
        """
        key_name: 对应 redis zadd 的key_name
        value: 对应存储的值
        score: 排序依赖的字段，必须为数字（可以为小数）
        return: True
        """
        if score is None:
            score = time.monotonic()
        if self.json_type:
            value = json.dumps(value)

        self.lua_add_sug_key(
                keys=[key_name, score, value],
                args=[self.capacity],
                client=self.redis.conn,
            )
        return True

    @prefix_wrapper
    def zget(self, key_name):
        """
        返回的数据为已排序的数据
        格式： [({'key': 1, 'value': 'zd_11'}, 111971.828263478)]
        """
        query_obj = self.redis.conn.zrevrange(key_name, 0, -1, withscores=True)
        ans = query_obj
        if self.json_type:
            ans = [(json.loads(item[0]), item[1]) for item in query_obj]
        return ans
```

利用Redis 有序集合 + lua 实现 个人常搜数据的记录。
redis 线上版本是4，
