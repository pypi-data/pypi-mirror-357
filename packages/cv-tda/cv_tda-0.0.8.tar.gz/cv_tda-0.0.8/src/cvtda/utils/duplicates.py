import typing

import numpy
import joblib
import sklearn.base

import cvtda.logging

class DuplicateFeaturesRemover(sklearn.base.TransformerMixin):
    def __init__(
        self,
        n_jobs: int = -1,

        tolerance: float = 1e-8,

        partition_search_batch_size: int = 2000,
        naive_threshold: int = 300
    ):
        self.fitted_ = False
        self.n_jobs_ = n_jobs

        self.tolerance_ = tolerance

        self.partition_search_batch_size_ = partition_search_batch_size
        self.naive_threshold_ = naive_threshold
    
    def fit(self, features: numpy.ndarray):
        self.non_duplicates_ = self.analyze_columns_(features)[0]
        self.fitted_ = True
        return self
    
    def transform(self, features: numpy.ndarray) -> numpy.ndarray:
        assert self.fitted_ is True, 'fit() must be called before transform()'
        return features[:, self.non_duplicates_]


    def naive_find_duplicate_columns_(self, features: numpy.ndarray) -> set:
        duplicates = set()
        features = features.transpose()
        for i in range(features.shape[0]):
            if i in duplicates:
                continue
            comp = numpy.abs(features - features[i]) < self.tolerance_
            comp = numpy.sum(comp, axis = 1)
            comp = numpy.where(comp == features.shape[1])[0]
            for j in comp[1:]:
                duplicates.add(j)
        return duplicates

    def analyze_columns_(
        self,
        features: numpy.ndarray,
        force_naive: bool = False,
        depth: int = 0
    ) -> typing.List[int]:
        if (features.shape[1] < self.naive_threshold_) or force_naive:
            if force_naive:
                cvtda.logging.logger().print(f"Naive check for {features.shape[1]} features at depth {depth}")
            duplicates = self.naive_find_duplicate_columns_(features)
            return list(set(range(features.shape[1])) - duplicates), list(duplicates)
        
        partition_by = self.find_best_partition_(features)
        partition_item = features[partition_by, :]
        duplicates = set()

        prev_value = numpy.min(partition_item) - 5 * self.tolerance_
        pbar = cvtda.logging.logger().pbar(numpy.unique(partition_item))
        for partition_value in pbar:
            if partition_value - prev_value < self.tolerance_:
                continue

            partition_idxs = numpy.where(numpy.abs(partition_item - partition_value) < self.tolerance_)[0]
            partition_idxs = numpy.setdiff1d(partition_idxs, numpy.array(list(duplicates)), assume_unique = True)

            cvtda.logging.logger().set_pbar_postfix(pbar, {
                'partition_by': partition_by,
                'num_features': len(partition_idxs),
                'duplicates': len(duplicates)
            })

            is_bad_partition = (len(partition_idxs) == features.shape[1])
            with cvtda.logging.DevNullLogger():
                _, partition_duplicates = self.analyze_columns_(
                    features[:, partition_idxs],
                    force_naive = is_bad_partition,
                    depth = depth + 1
                )

            for item in partition_idxs[list(partition_duplicates)]:
                duplicates.add(item)
            prev_value = partition_value

        cvtda.logging.logger().print(f'Found {len(duplicates)} duplicates')
        return list(set(range(features.shape[1])) - duplicates), list(duplicates)

    def find_best_partition_(self, features: numpy.ndarray) -> int:
        def bulk_biggest_partition_(items: numpy.ndarray) -> list:
            return [ numpy.max(numpy.unique(item, return_counts = True)[1]) for item in items ]
        
        partitions = joblib.Parallel(return_as = 'generator', n_jobs = self.n_jobs_)(
            joblib.delayed(bulk_biggest_partition_)(features[batch_start:batch_start + self.partition_search_batch_size_])
            for batch_start in range(0, features.shape[0], self.partition_search_batch_size_)
        )
        partitions = numpy.hstack(list(partitions))
        return numpy.argmin(partitions)
