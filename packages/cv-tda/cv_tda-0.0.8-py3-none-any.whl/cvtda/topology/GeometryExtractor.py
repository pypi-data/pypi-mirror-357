import typing

import numpy
import joblib
import skimage.measure
import skimage.feature

import cvtda.utils
import cvtda.logging

from . import utils
from .interface import Extractor


def calc_curvature(gray_image: numpy.ndarray) -> numpy.ndarray:
    min_, max_= gray_image.min(), gray_image.max()
    assert (min_ >= 0) and (max_ <= 1), f'Bad image format: should be [0, 1]; received [{min_}, {max_}]'

    euler_numbers, area, perimeter = [], [], []
    for threshold in range(256):
        bin = (gray_image > threshold / 255.)
        euler_numbers.append(skimage.measure.euler_number(bin))
        area.append(bin.sum())
        perimeter.append(skimage.measure.perimeter(bin))
    series = numpy.array([ euler_numbers, area, perimeter ])
    series_diff = numpy.array([ numpy.diff(euler_numbers), numpy.diff(area), numpy.diff(perimeter) ])
    
    return numpy.concatenate([
        cvtda.utils.sequence2features(series).flatten(),
        cvtda.utils.sequence2features(series_diff).flatten(),
    ])


class GrayGeometryExtractor(cvtda.utils.FeatureExtractorBase):
    def __init__(self, n_jobs: int = -1, reduced: bool = True):
        self.fitted_ = False
        self.n_jobs_ = n_jobs
        self.reduced_ = reduced
        self.feature_names_ = []

    def feature_names(self) -> typing.List[str]:
        assert self.fitted_ is True, 'fit() must be called before feature_names()'
        return self.feature_names_

    def fit(self, gray_images: numpy.ndarray):
        feature_names = [
            "daisy", "sift", "orb", "hog", "basic", "blur_effect", "centroid", "inertia_eigvals",
            "moments", "central_moments", "hu_moments", "shannon_entropy", "curvature"
        ]
        for features, name in zip(self.calc_raw_(gray_images[0]), feature_names):
            self.feature_names_.extend([ f"{name}-{i}" for i in range(len(features)) ])
    
        self.fitted_ = True
        return self

    def transform(self, gray_images: numpy.ndarray) -> numpy.ndarray:
        assert self.fitted_ is True, 'fit() must be called before transform()'
        
        def process_one_(gray_image: numpy.ndarray) -> numpy.ndarray:
            return numpy.nan_to_num(numpy.concatenate(self.calc_raw_(gray_image)), 0)
        features = numpy.stack(
            joblib.Parallel(n_jobs = self.n_jobs_)(
                joblib.delayed(process_one_)(img)
                for img in cvtda.logging.logger().pbar(gray_images, desc = 'GrayGeometryExtractor')
            )
        )
        assert features.shape == (len(gray_images), len(self.feature_names()))
        return features

    def calc_raw_(self, gray_image: numpy.ndarray) -> typing.List[numpy.ndarray]:
        sift = skimage.feature.SIFT()
        try:
            sift.detect_and_extract(gray_image)
            sift_descriptors = sift.descriptors.transpose()
            if sift_descriptors.shape[1] == 0:
                raise 'How is this possible?'
        except:
            sift_descriptors = numpy.zeros((128,1))
            
        orb = skimage.feature.ORB()
        try:
            orb.detect_and_extract(gray_image)
            orb_descriptors = orb.descriptors.transpose()
            if orb_descriptors.shape[1] == 0:
                raise 'How is this possible?'
        except:
            orb_descriptors = numpy.zeros((128,1))

        basic_features = skimage.feature.multiscale_basic_features(gray_image).reshape((-1, 24))

        moments_central = skimage.measure.moments_central(gray_image, order = 9)
        moments_normalized = skimage.measure.moments_normalized(moments_central)

        image_shape = max(*gray_image.shape)
        daisy_parameters = dict(
            step = (6 * image_shape // 32),
            radius = (12 * image_shape // 32),
            rings = 5,
            histograms = 5,
            orientations = 8
        )

        try:
            inertia_tensor_eigvals = skimage.measure.inertia_tensor_eigvals(gray_image)
        except:
            inertia_tensor_eigvals = numpy.zeros((2))
    
        return [
            skimage.feature.daisy(gray_image, **daisy_parameters).flatten(),
            cvtda.utils.sequence2features(numpy.ma.array(sift_descriptors), reduced = self.reduced_).flatten(),
            cvtda.utils.sequence2features(numpy.ma.array(orb_descriptors), reduced = self.reduced_).flatten(),
            skimage.feature.hog(gray_image, pixels_per_cell = (gray_image.shape[0] // 4, gray_image.shape[1] // 4)),
            cvtda.utils.sequence2features(numpy.ma.array(basic_features.transpose()), reduced = self.reduced_).flatten(),
            numpy.array([ skimage.measure.blur_effect(gray_image) ]),
            skimage.measure.centroid(gray_image),
            numpy.array(inertia_tensor_eigvals),
            skimage.measure.moments(gray_image, order = 9).flatten(),
            moments_central.flatten(),
            skimage.measure.moments_hu(moments_normalized).flatten(),
            numpy.array([ skimage.measure.shannon_entropy(gray_image) ]),
            calc_curvature(gray_image)
        ]


class RGBGeometryExtractor(cvtda.utils.FeatureExtractorBase):
    def __init__(self, n_jobs: int = -1, reduced: bool = True):
        self.fitted_ = False
        self.n_jobs_ = n_jobs
        self.reduced_ = reduced
        self.feature_names_ = []

    def feature_names(self) -> typing.List[str]:
        assert self.fitted_ is True, 'fit() must be called before feature_names()'
        return self.feature_names_

    def fit(self, rgb_images: numpy.ndarray):
        feature_names = [ "hog", "centroid", "inertia_eigvals", "moments", "central_moments", "corr_coef" ]
        for features, name in zip(self.calc_raw_(rgb_images[0]), feature_names):
            self.feature_names_.extend([ f"{name}-{i}" for i in range(len(features)) ])
    
        self.fitted_ = True
        return self

    def transform(self, rgb_images: numpy.ndarray) -> numpy.ndarray:
        assert self.fitted_ is True, 'fit() must be called before transform()'

        def process_one_(rgb_image: numpy.ndarray) -> numpy.ndarray:
            return numpy.nan_to_num(numpy.concatenate(self.calc_raw_(rgb_image)), 0)
        features = numpy.stack(
            joblib.Parallel(n_jobs = self.n_jobs_)(
                joblib.delayed(process_one_)(img)
                for img in cvtda.logging.logger().pbar(rgb_images, desc = 'RGBGeometryExtractor')
            )
        )
        assert features.shape == (len(rgb_images), len(self.feature_names()))
        return features
    
    def calc_raw_(self, rgb_image: numpy.ndarray) -> typing.Optional[numpy.ndarray]:
        try:
            inertia_tensor_eigvals = skimage.measure.inertia_tensor_eigvals(rgb_image)
        except:
            inertia_tensor_eigvals = numpy.zeros((3))
        
        return [
            skimage.feature.hog(rgb_image, channel_axis = 2),
            skimage.measure.centroid(rgb_image),
            numpy.array(inertia_tensor_eigvals),
            skimage.measure.moments(rgb_image, order = 6).flatten(),
            skimage.measure.moments_central(rgb_image, order = 6).flatten(),
            numpy.array([
                skimage.measure.pearson_corr_coeff(rgb_image[:, :, 0], rgb_image[:, :, 1])[0],
                skimage.measure.pearson_corr_coeff(rgb_image[:, :, 0], rgb_image[:, :, 2])[0],
                skimage.measure.pearson_corr_coeff(rgb_image[:, :, 1], rgb_image[:, :, 2])[0],
            ])
        ]


class MultidimensionalGeometryExtractor(cvtda.utils.FeatureExtractorBase):
    def __init__(self, n_jobs: int = -1, reduced: bool = True):
        self.fitted_ = False
        self.n_jobs_ = n_jobs
        self.reduced_ = reduced
        self.feature_names_ = []

    def feature_names(self) -> typing.List[str]:
        assert self.fitted_ is True, 'fit() must be called before feature_names()'
        return self.feature_names_

    def fit(self, nd_images: numpy.ndarray):
        feature_names = [ "basic", "blur_effect", "centroid", "inertia_eigvals", "moments", "central_moments" ]
        for features, name in zip(self.calc_raw_(nd_images[0]), feature_names):
            self.feature_names_.extend([ f"{name}-{i}" for i in range(len(features)) ])
    
        self.fitted_ = True
        return self

    def transform(self, nd_images: numpy.ndarray) -> numpy.ndarray:
        assert self.fitted_ is True, 'fit() must be called before transform()'
        
        def process_one_(nd_image: numpy.ndarray) -> numpy.ndarray:
            return numpy.nan_to_num(numpy.concatenate(self.calc_raw_(nd_image)), 0)
        features = numpy.stack(
            joblib.Parallel(n_jobs = self.n_jobs_)(
                joblib.delayed(process_one_)(img)
                for img in cvtda.logging.logger().pbar(nd_images, desc = 'MultidimensionalGeometryExtractor')
            )
        )
        assert features.shape == (len(nd_images), len(self.feature_names()))
        return features
    
    def calc_raw_(self, nd_image: numpy.ndarray) -> typing.Optional[numpy.ndarray]:
        basic_features = skimage.feature.multiscale_basic_features(nd_image)
        basic_features = basic_features.reshape((-1, basic_features.shape[-1]))

        try:
            inertia_tensor_eigvals = skimage.measure.inertia_tensor_eigvals(nd_image)
        except:
            inertia_tensor_eigvals = numpy.zeros((len(nd_image.shape)))

        return [
            cvtda.utils.sequence2features(numpy.ma.array(basic_features.transpose()), reduced = self.reduced_).flatten(),
            numpy.array([ skimage.measure.blur_effect(nd_image) ]),
            skimage.measure.centroid(nd_image),
            numpy.array(inertia_tensor_eigvals),
            skimage.measure.moments(nd_image, order = 9).flatten(),
            skimage.measure.moments_central(nd_image, order = 9).flatten()
        ]
    

class GeometryExtractor(Extractor):
    def __init__(self, n_jobs: int = -1, reduced: bool = True, only_get_from_dump: bool = False):
        super().__init__(n_jobs = n_jobs, reduced = reduced, only_get_from_dump = only_get_from_dump)

        self.rgb_extractor_ = RGBGeometryExtractor(n_jobs = self.n_jobs_, reduced = self.reduced_)
        self.gray_extractor_ = GrayGeometryExtractor(n_jobs = self.n_jobs_, reduced = self.reduced_)
        self.multidimensional_extractor_ = MultidimensionalGeometryExtractor(n_jobs = self.n_jobs_, reduced = self.reduced_)


    def process_rgb_(self, rgb_images: numpy.ndarray, do_fit: bool, dump_name: typing.Optional[str] = None) -> numpy.ndarray:
        return utils.process_iter_dump(self.rgb_extractor_, rgb_images, do_fit, self.features_dump_(dump_name))
    
    def feature_names_rgb_(self) -> typing.List[str]:
        return self.rgb_extractor_.feature_names()

    def process_gray_(self, gray_images: numpy.ndarray, do_fit: bool, dump_name: typing.Optional[str] = None) -> numpy.ndarray:
        if len(gray_images.shape) == 3:
            return utils.process_iter_dump(self.gray_extractor_, gray_images, do_fit, self.features_dump_(dump_name))
        else:
            return utils.process_iter_dump(self.multidimensional_extractor_, gray_images, do_fit, self.features_dump_(dump_name))

    def feature_names_gray_(self) -> typing.List[str]:
        if len(self.fit_dimensions_) == 2:
            return self.gray_extractor_.feature_names()
        else:
            return self.multidimensional_extractor_.feature_names()
