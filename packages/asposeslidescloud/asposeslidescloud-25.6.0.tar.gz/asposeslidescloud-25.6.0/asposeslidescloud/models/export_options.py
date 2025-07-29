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


class ExportOptions(object):


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
        'format': 'str'
    }

    attribute_map = {
        'default_regular_font': 'defaultRegularFont',
        'delete_embedded_binary_objects': 'deleteEmbeddedBinaryObjects',
        'gradient_style': 'gradientStyle',
        'font_fallback_rules': 'fontFallbackRules',
        'font_subst_rules': 'fontSubstRules',
        'skip_java_script_links': 'skipJavaScriptLinks',
        'format': 'format'
    }

    type_determiners = {
    }

    def __init__(self, default_regular_font=None, delete_embedded_binary_objects=None, gradient_style=None, font_fallback_rules=None, font_subst_rules=None, skip_java_script_links=None, format=None):  # noqa: E501
        """ExportOptions - a model defined in Swagger"""  # noqa: E501

        self._default_regular_font = None
        self._delete_embedded_binary_objects = None
        self._gradient_style = None
        self._font_fallback_rules = None
        self._font_subst_rules = None
        self._skip_java_script_links = None
        self._format = None

        if default_regular_font is not None:
            self.default_regular_font = default_regular_font
        if delete_embedded_binary_objects is not None:
            self.delete_embedded_binary_objects = delete_embedded_binary_objects
        if gradient_style is not None:
            self.gradient_style = gradient_style
        if font_fallback_rules is not None:
            self.font_fallback_rules = font_fallback_rules
        if font_subst_rules is not None:
            self.font_subst_rules = font_subst_rules
        if skip_java_script_links is not None:
            self.skip_java_script_links = skip_java_script_links
        if format is not None:
            self.format = format

    @property
    def default_regular_font(self):
        """Gets the default_regular_font of this ExportOptions.  # noqa: E501

        Default regular font for rendering the presentation.   # noqa: E501

        :return: The default_regular_font of this ExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._default_regular_font

    @default_regular_font.setter
    def default_regular_font(self, default_regular_font):
        """Sets the default_regular_font of this ExportOptions.

        Default regular font for rendering the presentation.   # noqa: E501

        :param default_regular_font: The default_regular_font of this ExportOptions.  # noqa: E501
        :type: str
        """
        self._default_regular_font = default_regular_font

    @property
    def delete_embedded_binary_objects(self):
        """Gets the delete_embedded_binary_objects of this ExportOptions.  # noqa: E501

        True to delete delete all embedded binary objects.  # noqa: E501

        :return: The delete_embedded_binary_objects of this ExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._delete_embedded_binary_objects

    @delete_embedded_binary_objects.setter
    def delete_embedded_binary_objects(self, delete_embedded_binary_objects):
        """Sets the delete_embedded_binary_objects of this ExportOptions.

        True to delete delete all embedded binary objects.  # noqa: E501

        :param delete_embedded_binary_objects: The delete_embedded_binary_objects of this ExportOptions.  # noqa: E501
        :type: bool
        """
        self._delete_embedded_binary_objects = delete_embedded_binary_objects

    @property
    def gradient_style(self):
        """Gets the gradient_style of this ExportOptions.  # noqa: E501

        Default regular font for rendering the presentation.   # noqa: E501

        :return: The gradient_style of this ExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._gradient_style

    @gradient_style.setter
    def gradient_style(self, gradient_style):
        """Sets the gradient_style of this ExportOptions.

        Default regular font for rendering the presentation.   # noqa: E501

        :param gradient_style: The gradient_style of this ExportOptions.  # noqa: E501
        :type: str
        """
        if gradient_style is not None:
            allowed_values = ["Default", "PowerPointUI"]  # noqa: E501
            if gradient_style.isdigit():
                int_gradient_style = int(gradient_style)
                if int_gradient_style < 0 or int_gradient_style >= len(allowed_values):
                    raise ValueError(
                        "Invalid value for `gradient_style` ({0}), must be one of {1}"  # noqa: E501
                        .format(gradient_style, allowed_values)
                    )
                self._gradient_style = allowed_values[int_gradient_style]
                return
            if gradient_style not in allowed_values:
                raise ValueError(
                    "Invalid value for `gradient_style` ({0}), must be one of {1}"  # noqa: E501
                    .format(gradient_style, allowed_values)
                )
        self._gradient_style = gradient_style

    @property
    def font_fallback_rules(self):
        """Gets the font_fallback_rules of this ExportOptions.  # noqa: E501

        Gets of sets list of font fallback rules.  # noqa: E501

        :return: The font_fallback_rules of this ExportOptions.  # noqa: E501
        :rtype: list[FontFallbackRule]
        """
        return self._font_fallback_rules

    @font_fallback_rules.setter
    def font_fallback_rules(self, font_fallback_rules):
        """Sets the font_fallback_rules of this ExportOptions.

        Gets of sets list of font fallback rules.  # noqa: E501

        :param font_fallback_rules: The font_fallback_rules of this ExportOptions.  # noqa: E501
        :type: list[FontFallbackRule]
        """
        self._font_fallback_rules = font_fallback_rules

    @property
    def font_subst_rules(self):
        """Gets the font_subst_rules of this ExportOptions.  # noqa: E501

        Gets of sets list of font substitution rules.  # noqa: E501

        :return: The font_subst_rules of this ExportOptions.  # noqa: E501
        :rtype: list[FontSubstRule]
        """
        return self._font_subst_rules

    @font_subst_rules.setter
    def font_subst_rules(self, font_subst_rules):
        """Sets the font_subst_rules of this ExportOptions.

        Gets of sets list of font substitution rules.  # noqa: E501

        :param font_subst_rules: The font_subst_rules of this ExportOptions.  # noqa: E501
        :type: list[FontSubstRule]
        """
        self._font_subst_rules = font_subst_rules

    @property
    def skip_java_script_links(self):
        """Gets the skip_java_script_links of this ExportOptions.  # noqa: E501

        True to skip hyperlinks with javascript calls when saving the presentation.  # noqa: E501

        :return: The skip_java_script_links of this ExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._skip_java_script_links

    @skip_java_script_links.setter
    def skip_java_script_links(self, skip_java_script_links):
        """Sets the skip_java_script_links of this ExportOptions.

        True to skip hyperlinks with javascript calls when saving the presentation.  # noqa: E501

        :param skip_java_script_links: The skip_java_script_links of this ExportOptions.  # noqa: E501
        :type: bool
        """
        self._skip_java_script_links = skip_java_script_links

    @property
    def format(self):
        """Gets the format of this ExportOptions.  # noqa: E501


        :return: The format of this ExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._format

    @format.setter
    def format(self, format):
        """Sets the format of this ExportOptions.


        :param format: The format of this ExportOptions.  # noqa: E501
        :type: str
        """
        self._format = format

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
        if not isinstance(other, ExportOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
