#!/usr/bin/env python
# encoding: utf-8

class DeepModel:
    def __init__(self):
        pass

    @classmethod
    def name(cls):
        sname = cls._name()
        assert isinstance(sname, str)
        return sname

    @classmethod
    def _name(cls):
        return "deepModel"

    def process(self, message):
        raise NotImplementedError

    def train(self, data):
        raise NotImplementedError

    def transform(self, X, scale_, min_):
        """Scaling features of X according to feature_range.

        Parameters
        ----------
        X : array-like, shape [n_samples, n_features]
            Input data that will be transformed.
        """
        X1 = X * scale_
        X1 = X1 + min_
        return X1

    def inverse_transform(self, X, scale_, min_):
        """Undo the scaling of X according to feature_range.

        Parameters
        ----------
        X : array-like, shape [n_samples, n_features]
            Input data that will be transformed. It cannot be sparse.
        """
        X1 = X - min_
        X1 = X1 / scale_
        return X1


class ClassFactory:

    @staticmethod
    def all_subclasses(cls):
        """Returns all known (imported) subclasses of a class."""
        # 递归地查找给定类的所有子类
        # for s in cls.__subclasses__() 返回所有从基类继承的子类，s表示子类本身
        # for g in ClassFactory.all_subclasses(s) 返回继承上面子类的子类，也就是找到子类的子类
        # 最后把所有子类存放到list中
        return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                       for g in ClassFactory.all_subclasses(s)]

    @staticmethod
    def all_classes(cls):
        return ClassFactory.all_subclasses(cls) + [cls]

    @staticmethod
    def subclasses_dict(cls):
        subclasses = ClassFactory.all_classes(cls)  # 所有子类
        sub_dict = {}
        for sub_cls in subclasses:
            sub_name = sub_cls.name()
            if sub_name in sub_dict:
                raise Exception("Name conflict: class {} and {} have the same name".format(sub_dict[sub_name], sub_cls))
            sub_dict[sub_name] = sub_cls
        return sub_dict
