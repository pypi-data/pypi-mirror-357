import abc
import typing

import sklearn.base


class FeatureExtractorBase(sklearn.base.TransformerMixin):
    def nest_feature_names(self, prefix: str, names: typing.List[str]) -> typing.List[str]:
        return [ f"{prefix} -> {name}" for name in names ]

    @abc.abstractmethod
    def feature_names(self) -> typing.List[str]:
        pass
