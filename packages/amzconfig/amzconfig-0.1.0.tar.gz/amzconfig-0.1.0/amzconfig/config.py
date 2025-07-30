import os
import yaml


class ConstantClassMeta(type):
    """
    对子类也生效的元类
    """

    def __setattr__(cls, name, value):
        # 检查属性是否已存在且非特殊属性
        if hasattr(cls, name) and not name.startswith("__"):
            raise AttributeError(f"The property '{name}' of the constant class {cls.__name__} is not allowed to be modified.")

    def __call__(cls, *args, **kwargs):
        raise TypeError(f"The constant class {cls.__name__} cannot be instantiated.")


class ConstantClass(metaclass=ConstantClassMeta):
    pass


class OsVarField:
    def __init__(self, os_var_name, default_value=None):
        self.os_var_name = os_var_name
        self.default_value = default_value

    def getValue(self):
        os_var = os.getenv(self.os_var_name, None)
        if not os_var:
            return self.default_value  # 环境变量优先值更高
        else:
            return os_var


class OsAttrMeta(type(ConstantClass), type):
    def __new__(cls, name, bases, attrs):
        # 动态生成 1 到 5 的属性
        for attr in attrs["__annotations__"]:
            # 从环境变量中获取值，全大写
            attrs[attr] = os.getenv(attr.upper(), attrs.get(attr, None))
        return super().__new__(cls, name, bases, attrs)


class YamlConfigLoader:
    __config = {}
    __loaded = False

    @classmethod
    def isLoaded(cls):
        return cls.__loaded

    @classmethod
    def load(cls, file_path: str):
        with open(file_path, "r") as file:
            cls.__config = yaml.safe_load(file)
            cls.__loaded = True

    @classmethod
    def getConfig(cls):
        return cls.__config

    @staticmethod
    def section_inject(section_name: str):
        """
        装饰器工厂：用于从 Config 加载指定配置段并注入到模型类中
        """

        def decorator(cls):
            def remove_none_values(data):
                """
                递归删除字典和列表中的 None 值。
                """
                if isinstance(data, dict):
                    return {
                        key: remove_none_values(value)
                        for key, value in data.items()
                        if value is not None
                    }
                elif isinstance(data, list):
                    return [
                        remove_none_values(item) for item in data if item is not None
                    ]
                else:
                    return data

            original_init = cls.__init__

            def __init__(self, *args, **kwargs):
                # 从 Config 获取对应的配置段, 配置类无视所有的传入参数
                config_section = YamlConfigLoader.getConfig().get(section_name, {})

                original_init(self, **remove_none_values(config_section))

            def __setattr__(self, key, value):
                raise TypeError("Cannot modify frozen instance")

            cls.__setattr__ = __setattr__
            cls.__init__ = __init__

            return cls

        return decorator

    @staticmethod
    def ofParametrizedMeta(section_name: str = None):
        class _ParametrizedMeta(type(ConstantClass), type):
            def __new__(cls, name, bases, attrs):
                for attr in attrs["__annotations__"]:
                    # 从环境变量中获取值，全大写
                    if attrs.get(attr) is not None:
                        if isinstance(attrs.get(attr), OsVarField):
                            attrs[attr] = attrs.get(attr).getValue()
                    else:
                        attrs[attr] = None  # 这里必须赋予None,否则报错属性不存在

                if YamlConfigLoader.isLoaded() and section_name is not None:
                    _params_dict: dict = {
                        k.upper(): v
                        for k, v in YamlConfigLoader.getConfig()
                        .get(section_name, {})
                        .items()
                    }
                    # 修改类属性, 优先级：配置值 > 环境变量 > 默认值
                    for attr, _type in attrs["__annotations__"].items():
                        _param_name = attr.upper()
                        # 配置文件的值
                        _file_val = _params_dict.get(_param_name, None)
                        if _file_val is not None:
                            if not isinstance(_file_val, _type):
                                raise TypeError(
                                    f"配置{attr}的值{_file_val}是{type(_file_val)}类型与类型{_type}不匹配"
                                )
                            attrs[attr] = _file_val  # 配置文件中村存在这个值且不是None

                return super().__new__(cls, name, bases, attrs)

        return _ParametrizedMeta
