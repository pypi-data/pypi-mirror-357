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

from asposeslidescloud.models.math_element import MathElement

class BarElement(MathElement):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'type': 'str',
        'base': 'MathElement',
        'position': 'str'
    }

    attribute_map = {
        'type': 'type',
        'base': 'base',
        'position': 'position'
    }

    type_determiners = {
        'type': 'Bar',
    }

    def __init__(self, type='Bar', base=None, position=None):  # noqa: E501
        """BarElement - a model defined in Swagger"""  # noqa: E501
        super(BarElement, self).__init__(type)

        self._base = None
        self._position = None
        self.type = 'Bar'

        if base is not None:
            self.base = base
        if position is not None:
            self.position = position

    @property
    def base(self):
        """Gets the base of this BarElement.  # noqa: E501

        Base  # noqa: E501

        :return: The base of this BarElement.  # noqa: E501
        :rtype: MathElement
        """
        return self._base

    @base.setter
    def base(self, base):
        """Sets the base of this BarElement.

        Base  # noqa: E501

        :param base: The base of this BarElement.  # noqa: E501
        :type: MathElement
        """
        self._base = base

    @property
    def position(self):
        """Gets the position of this BarElement.  # noqa: E501

        Position of the bar line.               # noqa: E501

        :return: The position of this BarElement.  # noqa: E501
        :rtype: str
        """
        return self._position

    @position.setter
    def position(self, position):
        """Sets the position of this BarElement.

        Position of the bar line.               # noqa: E501

        :param position: The position of this BarElement.  # noqa: E501
        :type: str
        """
        if position is not None:
            allowed_values = ["NotDefined", "Top", "Bottom"]  # noqa: E501
            if position.isdigit():
                int_position = int(position)
                if int_position < 0 or int_position >= len(allowed_values):
                    raise ValueError(
                        "Invalid value for `position` ({0}), must be one of {1}"  # noqa: E501
                        .format(position, allowed_values)
                    )
                self._position = allowed_values[int_position]
                return
            if position not in allowed_values:
                raise ValueError(
                    "Invalid value for `position` ({0}), must be one of {1}"  # noqa: E501
                    .format(position, allowed_values)
                )
        self._position = position

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
        if not isinstance(other, BarElement):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
