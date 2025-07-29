
# mils-de

The `mils-de` package contains the models and tools necessary for performing analysis in the [`Intensity Refractometry`](https://gitlab.mpcdf.mpg.de/dataanalytics-public/intensity_refractometry) project. Specifically, it implements:

- The `DensityEstimator` model for predicting plasma density based on power and phase measurements from multiple receivers.
- Weighting functions and evaluation metrics.
- Constraints for the design space.
- Data loading and data manipulation tools, including synthetic design creation.

## Installation

To install the package, run:

```bash
pip install mils-de
```

### Optional Dependencies

To reproduce the analysis from the [`Intensity Refractometry`](https://gitlab.mpcdf.mpg.de/dataanalytics-public/intensity_refractometry) project, install the optional dependencies:

```bash
pip install mils-de[full]
```

## Usage

For usage examples and detailed guides, refer to the notebooks in the [`Intensity Refractometry`](https://gitlab.mpcdf.mpg.de/dataanalytics-public/intensity_refractometry) repository. A good starting point is [this notebook](https://gitlab.mpcdf.mpg.de/dataanalytics-public/intensity_refractometry/tools/notebooks/density_estimator.ipynb), which demonstrates how to fit a density estimator for a specific design and assess its performance.