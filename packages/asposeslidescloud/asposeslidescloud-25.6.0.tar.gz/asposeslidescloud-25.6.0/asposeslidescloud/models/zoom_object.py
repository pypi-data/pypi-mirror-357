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

from asposeslidescloud.models.shape_base import ShapeBase

class ZoomObject(ShapeBase):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'self_uri': 'ResourceUri',
        'alternate_links': 'list[ResourceUri]',
        'name': 'str',
        'width': 'float',
        'height': 'float',
        'alternative_text': 'str',
        'alternative_text_title': 'str',
        'hidden': 'bool',
        'is_decorative': 'bool',
        'x': 'float',
        'y': 'float',
        'z_order_position': 'int',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'three_d_format': 'ThreeDFormat',
        'line_format': 'LineFormat',
        'hyperlink_click': 'Hyperlink',
        'hyperlink_mouse_over': 'Hyperlink',
        'type': 'str',
        'image_type': 'str',
        'return_to_parent': 'bool',
        'show_background': 'bool',
        'image': 'ResourceUri',
        'transition_duration': 'float'
    }

    attribute_map = {
        'self_uri': 'selfUri',
        'alternate_links': 'alternateLinks',
        'name': 'name',
        'width': 'width',
        'height': 'height',
        'alternative_text': 'alternativeText',
        'alternative_text_title': 'alternativeTextTitle',
        'hidden': 'hidden',
        'is_decorative': 'isDecorative',
        'x': 'x',
        'y': 'y',
        'z_order_position': 'zOrderPosition',
        'fill_format': 'fillFormat',
        'effect_format': 'effectFormat',
        'three_d_format': 'threeDFormat',
        'line_format': 'lineFormat',
        'hyperlink_click': 'hyperlinkClick',
        'hyperlink_mouse_over': 'hyperlinkMouseOver',
        'type': 'type',
        'image_type': 'imageType',
        'return_to_parent': 'returnToParent',
        'show_background': 'showBackground',
        'image': 'image',
        'transition_duration': 'transitionDuration'
    }

    type_determiners = {
    }

    def __init__(self, self_uri=None, alternate_links=None, name=None, width=None, height=None, alternative_text=None, alternative_text_title=None, hidden=None, is_decorative=None, x=None, y=None, z_order_position=None, fill_format=None, effect_format=None, three_d_format=None, line_format=None, hyperlink_click=None, hyperlink_mouse_over=None, type=None, image_type=None, return_to_parent=None, show_background=None, image=None, transition_duration=None):  # noqa: E501
        """ZoomObject - a model defined in Swagger"""  # noqa: E501
        super(ZoomObject, self).__init__(self_uri, alternate_links, name, width, height, alternative_text, alternative_text_title, hidden, is_decorative, x, y, z_order_position, fill_format, effect_format, three_d_format, line_format, hyperlink_click, hyperlink_mouse_over, type)

        self._image_type = None
        self._return_to_parent = None
        self._show_background = None
        self._image = None
        self._transition_duration = None

        if image_type is not None:
            self.image_type = image_type
        if return_to_parent is not None:
            self.return_to_parent = return_to_parent
        if show_background is not None:
            self.show_background = show_background
        if image is not None:
            self.image = image
        if transition_duration is not None:
            self.transition_duration = transition_duration

    @property
    def image_type(self):
        """Gets the image_type of this ZoomObject.  # noqa: E501

        Image type of a zoom object.   # noqa: E501

        :return: The image_type of this ZoomObject.  # noqa: E501
        :rtype: str
        """
        return self._image_type

    @image_type.setter
    def image_type(self, image_type):
        """Sets the image_type of this ZoomObject.

        Image type of a zoom object.   # noqa: E501

        :param image_type: The image_type of this ZoomObject.  # noqa: E501
        :type: str
        """
        if image_type is not None:
            allowed_values = ["Preview", "Cover"]  # noqa: E501
            if image_type.isdigit():
                int_image_type = int(image_type)
                if int_image_type < 0 or int_image_type >= len(allowed_values):
                    raise ValueError(
                        "Invalid value for `image_type` ({0}), must be one of {1}"  # noqa: E501
                        .format(image_type, allowed_values)
                    )
                self._image_type = allowed_values[int_image_type]
                return
            if image_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `image_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(image_type, allowed_values)
                )
        self._image_type = image_type

    @property
    def return_to_parent(self):
        """Gets the return_to_parent of this ZoomObject.  # noqa: E501

        Navigation behavior in slideshow.   # noqa: E501

        :return: The return_to_parent of this ZoomObject.  # noqa: E501
        :rtype: bool
        """
        return self._return_to_parent

    @return_to_parent.setter
    def return_to_parent(self, return_to_parent):
        """Sets the return_to_parent of this ZoomObject.

        Navigation behavior in slideshow.   # noqa: E501

        :param return_to_parent: The return_to_parent of this ZoomObject.  # noqa: E501
        :type: bool
        """
        self._return_to_parent = return_to_parent

    @property
    def show_background(self):
        """Gets the show_background of this ZoomObject.  # noqa: E501

        Specifies whether the Zoom will use the background of the destination slide.  # noqa: E501

        :return: The show_background of this ZoomObject.  # noqa: E501
        :rtype: bool
        """
        return self._show_background

    @show_background.setter
    def show_background(self, show_background):
        """Sets the show_background of this ZoomObject.

        Specifies whether the Zoom will use the background of the destination slide.  # noqa: E501

        :param show_background: The show_background of this ZoomObject.  # noqa: E501
        :type: bool
        """
        self._show_background = show_background

    @property
    def image(self):
        """Gets the image of this ZoomObject.  # noqa: E501

        Internal image link for zoom object  # noqa: E501

        :return: The image of this ZoomObject.  # noqa: E501
        :rtype: ResourceUri
        """
        return self._image

    @image.setter
    def image(self, image):
        """Sets the image of this ZoomObject.

        Internal image link for zoom object  # noqa: E501

        :param image: The image of this ZoomObject.  # noqa: E501
        :type: ResourceUri
        """
        self._image = image

    @property
    def transition_duration(self):
        """Gets the transition_duration of this ZoomObject.  # noqa: E501

        Duration of the transition between Zoom and slide.  # noqa: E501

        :return: The transition_duration of this ZoomObject.  # noqa: E501
        :rtype: float
        """
        return self._transition_duration

    @transition_duration.setter
    def transition_duration(self, transition_duration):
        """Sets the transition_duration of this ZoomObject.

        Duration of the transition between Zoom and slide.  # noqa: E501

        :param transition_duration: The transition_duration of this ZoomObject.  # noqa: E501
        :type: float
        """
        self._transition_duration = transition_duration

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
        if not isinstance(other, ZoomObject):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
