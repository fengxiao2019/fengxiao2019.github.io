# Pytest 参数化方式[part2-高级用法]
业务诉求：在做单元测试时，针对API的测试，需要构造各种不同的参数，多个API接口测试的数据存在少量的区别。

如何实现？
可以利用 `@pytest.fixture` 构造`fixture`，多个 `fixture`作为函数的入参，会自动进行组合。类似：

```python
@pytest.fixture(params=[item[0] for item in _QUERY_OBJ_LIST],
                ids=[item[1] for item in _QUERY_OBJ_LIST])
def query_demand_statistic_data(request):
    return request.param

@pytest.fixture(params=GranularityEnum.greater_than_day_granularity(),
                ids=GranularityEnum.greater_than_day_granularity())
def granularity_payload(request):
    return request.param
```
具体的测试函数可以将上面的`fixture`作为参数：
``` python
class TestDemandFinishedQuery:
    def test_empty_query_parameter(self, test_client, query_path, granularity_payload, query_demand_statistic_data):
        query_demand_statistic_data['granularity'] = granularity_payload
        response = test_client.post(query_path,
                                    json=query_demand_statistic_data,
                                    follow_redirects=True)
        json_data = response.get_json(force=True)
        assert json_data['code'] == 0
```

如果不存在多个test case 共用一组测试参数的话，可以直接使用`pytest.mark.parameterize`:

``` python
@pytest.mark.parametrize("granularity_payload", GranularityEnum.greater_than_day_granularity())
@pytest.mark.parametrize("query_demand_statistic_data", [item[0] for item in _QUERY_OBJ_LIST])
def test_empty_query_parameter(self, test_client, query_path, granularity_payload, query_demand_statistic_data):
    query_demand_statistic_data['granularity'] = granularity_payload
    response = test_client.post(query_path,
                                json=query_demand_statistic_data,
                                follow_redirects=True)
    json_data = response.get_json(force=True)
    
    assert json_data['code'] == 0

```

上面的函数中主要用到了 `pytest`的内置装饰器 `pytest.mark.parameterize`，实现测试函数参数化。

## 参考
https://docs.pytest.org/en/7.1.x/reference/reference.html#pytest.Metafunc.parametrize
