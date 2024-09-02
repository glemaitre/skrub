import itertools

import sklearn
from sklearn.utils.fixes import parse_version

from . import __version__

sklearn_version = parse_version(sklearn.__version__)

if sklearn_version > parse_version("1.6"):
    from sklearn.utils._estimator_html_repr import _HTMLDocumentationLinkMixin
else:

    class _HTMLDocumentationLinkMixin:
        """Mixin class allowing to generate a link to the API documentation.

        This mixin relies on three attributes:
        - `_doc_link_module`: it corresponds to the root module (e.g. `sklearn`). Using
          this mixin, the default value is `sklearn`.
        - `_doc_link_template`: it corresponds to the template used to generate the
          link to the API documentation. Using this mixin, the default value is
          `"https://scikit-learn.org/{version_url}/modules/generated/
          {estimator_module}.{estimator_name}.html"`.
        - `_doc_link_url_param_generator`: it corresponds to a function that generates
          the parameters to be used in the template when the estimator module and name
          are not sufficient.

        The method :meth:`_get_doc_link` generates the link to the API documentation for
        a given estimator.

        This useful provides all the necessary states for
        :func:`sklearn.utils.estimator_html_repr` to generate a link to the API
        documentation for the estimator HTML diagram.

        Examples
        --------
        If the default values for `_doc_link_module`, `_doc_link_template` are not
        suitable, then you can override them and provide a method to generate the URL
        parameters:
        >>> from sklearn.base import BaseEstimator
        >>> doc_link_template = "https://website.com/{single_param}.html"
        >>> def url_param_generator(estimator):
        ...     return {"single_param": estimator.__class__.__name__}
        >>> class MyEstimator(BaseEstimator):
        ...     _doc_link_module = "builtins"
        ...     _doc_link_template = doc_link_template
        ...     _doc_link_url_param_generator = url_param_generator
        >>> estimator = MyEstimator()
        >>> estimator._get_doc_link()
        'https://website.com/MyEstimator.html'

        If instead of overriding the attributes inside the class definition, you want to
        override a class instance, you can use `types.MethodType` to bind the method to
        the instance:
        >>> import types
        >>> estimator = BaseEstimator()
        >>> estimator._doc_link_template = doc_link_template
        >>> estimator._doc_link_url_param_generator = types.MethodType(
        ...     url_param_generator, estimator)
        >>> estimator._get_doc_link()
        'https://website.com/BaseEstimator.html'
        """

        _doc_link_module = "sklearn"
        _doc_link_url_param_generator = None

        @property
        def _doc_link_template(self):
            sklearn_version = parse_version(sklearn.__version__)
            if sklearn_version.dev is None:
                version_url = f"{sklearn_version.major}.{sklearn_version.minor}"
            else:
                version_url = "dev"
            return getattr(
                self,
                "__doc_link_template",
                (
                    f"https://scikit-learn.org/{version_url}/modules/generated/"
                    "{estimator_module}.{estimator_name}.html"
                ),
            )

        @_doc_link_template.setter
        def _doc_link_template(self, value):
            setattr(self, "__doc_link_template", value)

        def _get_doc_link(self):
            """Generates a link to the API documentation for a given estimator.

            This method generates the link to the estimator's documentation page
            by using the template defined by the attribute `_doc_link_template`.

            Returns
            -------
            url : str
                The URL to the API documentation for this estimator. If the estimator
                does not belong to module `_doc_link_module`, the empty string (i.e.
                `""`) is returned.
            """
            if self.__class__.__module__.split(".")[0] != self._doc_link_module:
                return ""

            if self._doc_link_url_param_generator is None:
                estimator_name = self.__class__.__name__
                # Construct the estimator's module name, up to the first private
                # submodule. This works because in scikit-learn all public estimators
                # are exposed at that level, even if they actually live in a private
                # sub-module.
                estimator_module = ".".join(
                    itertools.takewhile(
                        lambda part: not part.startswith("_"),
                        self.__class__.__module__.split("."),
                    )
                )
                return self._doc_link_template.format(
                    estimator_module=estimator_module, estimator_name=estimator_name
                )
            return self._doc_link_template.format(
                **self._doc_link_url_param_generator()
            )


doc_link_template = (
    "https://skrub-data.org/{version}/reference/generated/"
    "{estimator_module}.{estimator_name}.html"
)
doc_link_module = "skrub"


def doc_link_url_param_generator(estimator):
    skrub_version = parse_version(__version__)
    if skrub_version.dev is None:
        version_url = f"{skrub_version.major}.{skrub_version.minor}"
    else:
        version_url = "dev"
    estimator_name = estimator.__class__.__name__
    estimator_module = ".".join(
        itertools.takewhile(
            lambda part: not part.startswith("_"),
            estimator.__class__.__module__.split("."),
        )
    )
    return {
        "version": version_url,
        "estimator_module": estimator_module,
        "estimator_name": estimator_name,
    }