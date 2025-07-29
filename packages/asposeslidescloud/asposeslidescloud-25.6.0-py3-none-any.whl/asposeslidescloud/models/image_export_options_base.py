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

class ImageExportOptionsBase(ExportOptions):


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
        'height': 'int',
        'width': 'int'
    }

    attribute_map = {
        'default_regular_font': 'defaultRegularFont',
        'delete_embedded_binary_objects': 'deleteEmbeddedBinaryObjects',
        'gradient_style': 'gradientStyle',
        'font_fallback_rules': 'fontFallbackRules',
        'font_subst_rules': 'fontSubstRules',
        'skip_java_script_links': 'skipJavaScriptLinks',
        'format': 'format',
        'height': 'height',
        'width': 'width'
    }

    type_determiners = {
    }

    def __init__(self, default_regular_font=None, delete_embedded_binary_objects=None, gradient_style=None, font_fallback_rules=None, font_subst_rules=None, skip_java_script_links=None, format=None, height=None, width=None):  # noqa: E501
        """ImageExportOptionsBase - a model defined in Swagger"""  # noqa: E501
        super(ImageExportOptionsBase, self).__init__(default_regular_font, delete_embedded_binary_objects, gradient_style, font_fallback_rules, font_subst_rules, skip_java_script_links, format)

        self._height = None
        self._width = None

        if height is not None:
            self.height = height
        if width is not None:
            self.width = width

    @property
    def height(self):
        """Gets the height of this ImageExportOptionsBase.  # noqa: E501

        Gets or sets the height of slides in the output image format.  # noqa: E501

        :return: The height of this ImageExportOptionsBase.  # noqa: E501
        :rtype: int
        """
        return self._height

    @height.setter
    def height(self, height):
        """Sets the height of this ImageExportOptionsBase.

        Gets or sets the height of slides in the output image format.  # noqa: E501

        :param height: The height of this ImageExportOptionsBase.  # noqa: E501
        :type: int
        """
        self._height = height

    @property
    def width(self):
        """Gets the width of this ImageExportOptionsBase.  # noqa: E501

        Gets or sets the height of slides in the output the output image format.  # noqa: E501

        :return: The width of this ImageExportOptionsBase.  # noqa: E501
        :rtype: int
        """
        return self._width

    @width.setter
    def width(self, width):
        """Sets the width of this ImageExportOptionsBase.

        Gets or sets the height of slides in the output the output image format.  # noqa: E501

        :param width: The width of this ImageExportOptionsBase.  # noqa: E501
        :type: int
        """
        self._width = width

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
        if not isinstance(other, ImageExportOptionsBase):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
