# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose">
#   Copyright (c) 2018 Aspose.Slides for Cloud
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------

import pprint
import re  # noqa: F401

import six

from asposeslidescloud.models.export_options import ExportOptions

class Html5ExportOptions(ExportOptions):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'default_regular_font': 'str',
        'delete_embedded_binary_objects': 'bool',
        'gradient_style': 'str',
        'font_fallback_rules': 'list[FontFallbackRule]',
        'font_subst_rules': 'list[FontSubstRule]',
        'skip_java_script_links': 'bool',
        'format': 'str',
        'animate_transitions': 'bool',
        'animate_shapes': 'bool',
        'embed_images': 'bool',
        'slides_layout_options': 'SlidesLayoutOptions',
        'templates_path': 'str',
        'disable_font_ligatures': 'bool'
    }

    attribute_map = {
        'default_regular_font': 'defaultRegularFont',
        'delete_embedded_binary_objects': 'deleteEmbeddedBinaryObjects',
        'gradient_style': 'gradientStyle',
        'font_fallback_rules': 'fontFallbackRules',
        'font_subst_rules': 'fontSubstRules',
        'skip_java_script_links': 'skipJavaScriptLinks',
        'format': 'format',
        'animate_transitions': 'animateTransitions',
        'animate_shapes': 'animateShapes',
        'embed_images': 'embedImages',
        'slides_layout_options': 'slidesLayoutOptions',
        'templates_path': 'templatesPath',
        'disable_font_ligatures': 'disableFontLigatures'
    }

    type_determiners = {
        'format': 'html5',
    }

    def __init__(self, default_regular_font=None, delete_embedded_binary_objects=None, gradient_style=None, font_fallback_rules=None, font_subst_rules=None, skip_java_script_links=None, format='html5', animate_transitions=None, animate_shapes=None, embed_images=None, slides_layout_options=None, templates_path=None, disable_font_ligatures=None):  # noqa: E501
        """Html5ExportOptions - a model defined in Swagger"""  # noqa: E501
        super(Html5ExportOptions, self).__init__(default_regular_font, delete_embedded_binary_objects, gradient_style, font_fallback_rules, font_subst_rules, skip_java_script_links, format)

        self._animate_transitions = None
        self._animate_shapes = None
        self._embed_images = None
        self._slides_layout_options = None
        self._templates_path = None
        self._disable_font_ligatures = None
        self.format = 'html5'

        if animate_transitions is not None:
            self.animate_transitions = animate_transitions
        if animate_shapes is not None:
            self.animate_shapes = animate_shapes
        if embed_images is not None:
            self.embed_images = embed_images
        if slides_layout_options is not None:
            self.slides_layout_options = slides_layout_options
        if templates_path is not None:
            self.templates_path = templates_path
        if disable_font_ligatures is not None:
            self.disable_font_ligatures = disable_font_ligatures

    @property
    def animate_transitions(self):
        """Gets the animate_transitions of this Html5ExportOptions.  # noqa: E501

        Gets or sets transitions animation option.  # noqa: E501

        :return: The animate_transitions of this Html5ExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._animate_transitions

    @animate_transitions.setter
    def animate_transitions(self, animate_transitions):
        """Sets the animate_transitions of this Html5ExportOptions.

        Gets or sets transitions animation option.  # noqa: E501

        :param animate_transitions: The animate_transitions of this Html5ExportOptions.  # noqa: E501
        :type: bool
        """
        self._animate_transitions = animate_transitions

    @property
    def animate_shapes(self):
        """Gets the animate_shapes of this Html5ExportOptions.  # noqa: E501

        Gets or sets shapes animation option.  # noqa: E501

        :return: The animate_shapes of this Html5ExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._animate_shapes

    @animate_shapes.setter
    def animate_shapes(self, animate_shapes):
        """Sets the animate_shapes of this Html5ExportOptions.

        Gets or sets shapes animation option.  # noqa: E501

        :param animate_shapes: The animate_shapes of this Html5ExportOptions.  # noqa: E501
        :type: bool
        """
        self._animate_shapes = animate_shapes

    @property
    def embed_images(self):
        """Gets the embed_images of this Html5ExportOptions.  # noqa: E501

        Gets or sets embed images option.  # noqa: E501

        :return: The embed_images of this Html5ExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._embed_images

    @embed_images.setter
    def embed_images(self, embed_images):
        """Sets the embed_images of this Html5ExportOptions.

        Gets or sets embed images option.  # noqa: E501

        :param embed_images: The embed_images of this Html5ExportOptions.  # noqa: E501
        :type: bool
        """
        self._embed_images = embed_images

    @property
    def slides_layout_options(self):
        """Gets the slides_layout_options of this Html5ExportOptions.  # noqa: E501

        Slides layouting options  # noqa: E501

        :return: The slides_layout_options of this Html5ExportOptions.  # noqa: E501
        :rtype: SlidesLayoutOptions
        """
        return self._slides_layout_options

    @slides_layout_options.setter
    def slides_layout_options(self, slides_layout_options):
        """Sets the slides_layout_options of this Html5ExportOptions.

        Slides layouting options  # noqa: E501

        :param slides_layout_options: The slides_layout_options of this Html5ExportOptions.  # noqa: E501
        :type: SlidesLayoutOptions
        """
        self._slides_layout_options = slides_layout_options

    @property
    def templates_path(self):
        """Gets the templates_path of this Html5ExportOptions.  # noqa: E501

        Path to custom templates  # noqa: E501

        :return: The templates_path of this Html5ExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._templates_path

    @templates_path.setter
    def templates_path(self, templates_path):
        """Sets the templates_path of this Html5ExportOptions.

        Path to custom templates  # noqa: E501

        :param templates_path: The templates_path of this Html5ExportOptions.  # noqa: E501
        :type: str
        """
        self._templates_path = templates_path

    @property
    def disable_font_ligatures(self):
        """Gets the disable_font_ligatures of this Html5ExportOptions.  # noqa: E501

        true to disable ligatures in the rendered output.  # noqa: E501

        :return: The disable_font_ligatures of this Html5ExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._disable_font_ligatures

    @disable_font_ligatures.setter
    def disable_font_ligatures(self, disable_font_ligatures):
        """Sets the disable_font_ligatures of this Html5ExportOptions.

        true to disable ligatures in the rendered output.  # noqa: E501

        :param disable_font_ligatures: The disable_font_ligatures of this Html5ExportOptions.  # noqa: E501
        :type: bool
        """
        self._disable_font_ligatures = disable_font_ligatures

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Html5ExportOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
