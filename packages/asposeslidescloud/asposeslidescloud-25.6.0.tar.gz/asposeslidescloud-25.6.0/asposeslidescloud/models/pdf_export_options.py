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

class PdfExportOptions(ExportOptions):


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
        'text_compression': 'str',
        'embed_full_fonts': 'bool',
        'compliance': 'str',
        'sufficient_resolution': 'float',
        'jpeg_quality': 'int',
        'draw_slides_frame': 'bool',
        'show_hidden_slides': 'bool',
        'save_metafiles_as_png': 'bool',
        'password': 'str',
        'embed_true_type_fonts_for_ascii': 'bool',
        'additional_common_font_families': 'list[str]',
        'slides_layout_options': 'SlidesLayoutOptions',
        'image_transparent_color': 'str',
        'apply_image_transparent': 'bool',
        'access_permissions': 'AccessPermissions',
        'hide_ink': 'bool',
        'interpret_mask_op_as_opacity': 'bool',
        'rasterize_unsupported_font_styles': 'bool',
        'include_ole_data': 'bool'
    }

    attribute_map = {
        'default_regular_font': 'defaultRegularFont',
        'delete_embedded_binary_objects': 'deleteEmbeddedBinaryObjects',
        'gradient_style': 'gradientStyle',
        'font_fallback_rules': 'fontFallbackRules',
        'font_subst_rules': 'fontSubstRules',
        'skip_java_script_links': 'skipJavaScriptLinks',
        'format': 'format',
        'text_compression': 'textCompression',
        'embed_full_fonts': 'embedFullFonts',
        'compliance': 'compliance',
        'sufficient_resolution': 'sufficientResolution',
        'jpeg_quality': 'jpegQuality',
        'draw_slides_frame': 'drawSlidesFrame',
        'show_hidden_slides': 'showHiddenSlides',
        'save_metafiles_as_png': 'saveMetafilesAsPng',
        'password': 'password',
        'embed_true_type_fonts_for_ascii': 'embedTrueTypeFontsForAscii',
        'additional_common_font_families': 'additionalCommonFontFamilies',
        'slides_layout_options': 'slidesLayoutOptions',
        'image_transparent_color': 'imageTransparentColor',
        'apply_image_transparent': 'applyImageTransparent',
        'access_permissions': 'accessPermissions',
        'hide_ink': 'hideInk',
        'interpret_mask_op_as_opacity': 'interpretMaskOpAsOpacity',
        'rasterize_unsupported_font_styles': 'rasterizeUnsupportedFontStyles',
        'include_ole_data': 'includeOleData'
    }

    type_determiners = {
        'format': 'pdf',
    }

    def __init__(self, default_regular_font=None, delete_embedded_binary_objects=None, gradient_style=None, font_fallback_rules=None, font_subst_rules=None, skip_java_script_links=None, format='pdf', text_compression=None, embed_full_fonts=None, compliance=None, sufficient_resolution=None, jpeg_quality=None, draw_slides_frame=None, show_hidden_slides=None, save_metafiles_as_png=None, password=None, embed_true_type_fonts_for_ascii=None, additional_common_font_families=None, slides_layout_options=None, image_transparent_color=None, apply_image_transparent=None, access_permissions=None, hide_ink=None, interpret_mask_op_as_opacity=None, rasterize_unsupported_font_styles=None, include_ole_data=None):  # noqa: E501
        """PdfExportOptions - a model defined in Swagger"""  # noqa: E501
        super(PdfExportOptions, self).__init__(default_regular_font, delete_embedded_binary_objects, gradient_style, font_fallback_rules, font_subst_rules, skip_java_script_links, format)

        self._text_compression = None
        self._embed_full_fonts = None
        self._compliance = None
        self._sufficient_resolution = None
        self._jpeg_quality = None
        self._draw_slides_frame = None
        self._show_hidden_slides = None
        self._save_metafiles_as_png = None
        self._password = None
        self._embed_true_type_fonts_for_ascii = None
        self._additional_common_font_families = None
        self._slides_layout_options = None
        self._image_transparent_color = None
        self._apply_image_transparent = None
        self._access_permissions = None
        self._hide_ink = None
        self._interpret_mask_op_as_opacity = None
        self._rasterize_unsupported_font_styles = None
        self._include_ole_data = None
        self.format = 'pdf'

        if text_compression is not None:
            self.text_compression = text_compression
        if embed_full_fonts is not None:
            self.embed_full_fonts = embed_full_fonts
        if compliance is not None:
            self.compliance = compliance
        if sufficient_resolution is not None:
            self.sufficient_resolution = sufficient_resolution
        if jpeg_quality is not None:
            self.jpeg_quality = jpeg_quality
        if draw_slides_frame is not None:
            self.draw_slides_frame = draw_slides_frame
        if show_hidden_slides is not None:
            self.show_hidden_slides = show_hidden_slides
        if save_metafiles_as_png is not None:
            self.save_metafiles_as_png = save_metafiles_as_png
        if password is not None:
            self.password = password
        if embed_true_type_fonts_for_ascii is not None:
            self.embed_true_type_fonts_for_ascii = embed_true_type_fonts_for_ascii
        if additional_common_font_families is not None:
            self.additional_common_font_families = additional_common_font_families
        if slides_layout_options is not None:
            self.slides_layout_options = slides_layout_options
        if image_transparent_color is not None:
            self.image_transparent_color = image_transparent_color
        if apply_image_transparent is not None:
            self.apply_image_transparent = apply_image_transparent
        if access_permissions is not None:
            self.access_permissions = access_permissions
        if hide_ink is not None:
            self.hide_ink = hide_ink
        if interpret_mask_op_as_opacity is not None:
            self.interpret_mask_op_as_opacity = interpret_mask_op_as_opacity
        if rasterize_unsupported_font_styles is not None:
            self.rasterize_unsupported_font_styles = rasterize_unsupported_font_styles
        if include_ole_data is not None:
            self.include_ole_data = include_ole_data

    @property
    def text_compression(self):
        """Gets the text_compression of this PdfExportOptions.  # noqa: E501

        Specifies compression type to be used for all textual content in the document.  # noqa: E501

        :return: The text_compression of this PdfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._text_compression

    @text_compression.setter
    def text_compression(self, text_compression):
        """Sets the text_compression of this PdfExportOptions.

        Specifies compression type to be used for all textual content in the document.  # noqa: E501

        :param text_compression: The text_compression of this PdfExportOptions.  # noqa: E501
        :type: str
        """
        if text_compression is not None:
            allowed_values = ["None", "Flate"]  # noqa: E501
            if text_compression.isdigit():
                int_text_compression = int(text_compression)
                if int_text_compression < 0 or int_text_compression >= len(allowed_values):
                    raise ValueError(
                        "Invalid value for `text_compression` ({0}), must be one of {1}"  # noqa: E501
                        .format(text_compression, allowed_values)
                    )
                self._text_compression = allowed_values[int_text_compression]
                return
            if text_compression not in allowed_values:
                raise ValueError(
                    "Invalid value for `text_compression` ({0}), must be one of {1}"  # noqa: E501
                    .format(text_compression, allowed_values)
                )
        self._text_compression = text_compression

    @property
    def embed_full_fonts(self):
        """Gets the embed_full_fonts of this PdfExportOptions.  # noqa: E501

        Determines if all characters of font should be embedded or only used subset.  # noqa: E501

        :return: The embed_full_fonts of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._embed_full_fonts

    @embed_full_fonts.setter
    def embed_full_fonts(self, embed_full_fonts):
        """Sets the embed_full_fonts of this PdfExportOptions.

        Determines if all characters of font should be embedded or only used subset.  # noqa: E501

        :param embed_full_fonts: The embed_full_fonts of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._embed_full_fonts = embed_full_fonts

    @property
    def compliance(self):
        """Gets the compliance of this PdfExportOptions.  # noqa: E501

        Desired conformance level for generated PDF document.  # noqa: E501

        :return: The compliance of this PdfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._compliance

    @compliance.setter
    def compliance(self, compliance):
        """Sets the compliance of this PdfExportOptions.

        Desired conformance level for generated PDF document.  # noqa: E501

        :param compliance: The compliance of this PdfExportOptions.  # noqa: E501
        :type: str
        """
        if compliance is not None:
            allowed_values = ["Pdf15", "Pdf16", "Pdf17", "PdfA1b", "PdfA1a", "PdfA2b", "PdfA2a", "PdfA3b", "PdfA3a", "PdfUa", "PdfA2u"]  # noqa: E501
            if compliance.isdigit():
                int_compliance = int(compliance)
                if int_compliance < 0 or int_compliance >= len(allowed_values):
                    raise ValueError(
                        "Invalid value for `compliance` ({0}), must be one of {1}"  # noqa: E501
                        .format(compliance, allowed_values)
                    )
                self._compliance = allowed_values[int_compliance]
                return
            if compliance not in allowed_values:
                raise ValueError(
                    "Invalid value for `compliance` ({0}), must be one of {1}"  # noqa: E501
                    .format(compliance, allowed_values)
                )
        self._compliance = compliance

    @property
    def sufficient_resolution(self):
        """Gets the sufficient_resolution of this PdfExportOptions.  # noqa: E501

        Returns or sets a value determining resolution of images inside PDF document.  Property affects on file size, time of export and image quality. The default value is 96.  # noqa: E501

        :return: The sufficient_resolution of this PdfExportOptions.  # noqa: E501
        :rtype: float
        """
        return self._sufficient_resolution

    @sufficient_resolution.setter
    def sufficient_resolution(self, sufficient_resolution):
        """Sets the sufficient_resolution of this PdfExportOptions.

        Returns or sets a value determining resolution of images inside PDF document.  Property affects on file size, time of export and image quality. The default value is 96.  # noqa: E501

        :param sufficient_resolution: The sufficient_resolution of this PdfExportOptions.  # noqa: E501
        :type: float
        """
        self._sufficient_resolution = sufficient_resolution

    @property
    def jpeg_quality(self):
        """Gets the jpeg_quality of this PdfExportOptions.  # noqa: E501

        Returns or sets a value determining the quality of the JPEG images inside PDF document.  # noqa: E501

        :return: The jpeg_quality of this PdfExportOptions.  # noqa: E501
        :rtype: int
        """
        return self._jpeg_quality

    @jpeg_quality.setter
    def jpeg_quality(self, jpeg_quality):
        """Sets the jpeg_quality of this PdfExportOptions.

        Returns or sets a value determining the quality of the JPEG images inside PDF document.  # noqa: E501

        :param jpeg_quality: The jpeg_quality of this PdfExportOptions.  # noqa: E501
        :type: int
        """
        self._jpeg_quality = jpeg_quality

    @property
    def draw_slides_frame(self):
        """Gets the draw_slides_frame of this PdfExportOptions.  # noqa: E501

        True to draw black frame around each slide.  # noqa: E501

        :return: The draw_slides_frame of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._draw_slides_frame

    @draw_slides_frame.setter
    def draw_slides_frame(self, draw_slides_frame):
        """Sets the draw_slides_frame of this PdfExportOptions.

        True to draw black frame around each slide.  # noqa: E501

        :param draw_slides_frame: The draw_slides_frame of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._draw_slides_frame = draw_slides_frame

    @property
    def show_hidden_slides(self):
        """Gets the show_hidden_slides of this PdfExportOptions.  # noqa: E501

        Specifies whether the generated document should include hidden slides or not. Default is false.   # noqa: E501

        :return: The show_hidden_slides of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._show_hidden_slides

    @show_hidden_slides.setter
    def show_hidden_slides(self, show_hidden_slides):
        """Sets the show_hidden_slides of this PdfExportOptions.

        Specifies whether the generated document should include hidden slides or not. Default is false.   # noqa: E501

        :param show_hidden_slides: The show_hidden_slides of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._show_hidden_slides = show_hidden_slides

    @property
    def save_metafiles_as_png(self):
        """Gets the save_metafiles_as_png of this PdfExportOptions.  # noqa: E501

        True to convert all metafiles used in a presentation to the PNG images.  # noqa: E501

        :return: The save_metafiles_as_png of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._save_metafiles_as_png

    @save_metafiles_as_png.setter
    def save_metafiles_as_png(self, save_metafiles_as_png):
        """Sets the save_metafiles_as_png of this PdfExportOptions.

        True to convert all metafiles used in a presentation to the PNG images.  # noqa: E501

        :param save_metafiles_as_png: The save_metafiles_as_png of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._save_metafiles_as_png = save_metafiles_as_png

    @property
    def password(self):
        """Gets the password of this PdfExportOptions.  # noqa: E501

        Setting user password to protect the PDF document.   # noqa: E501

        :return: The password of this PdfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """Sets the password of this PdfExportOptions.

        Setting user password to protect the PDF document.   # noqa: E501

        :param password: The password of this PdfExportOptions.  # noqa: E501
        :type: str
        """
        self._password = password

    @property
    def embed_true_type_fonts_for_ascii(self):
        """Gets the embed_true_type_fonts_for_ascii of this PdfExportOptions.  # noqa: E501

        Determines if Aspose.Slides will embed common fonts for ASCII (33..127 code range) text. Fonts for character codes greater than 127 are always embedded. Common fonts list includes PDF's base 14 fonts and additional user specified fonts.  # noqa: E501

        :return: The embed_true_type_fonts_for_ascii of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._embed_true_type_fonts_for_ascii

    @embed_true_type_fonts_for_ascii.setter
    def embed_true_type_fonts_for_ascii(self, embed_true_type_fonts_for_ascii):
        """Sets the embed_true_type_fonts_for_ascii of this PdfExportOptions.

        Determines if Aspose.Slides will embed common fonts for ASCII (33..127 code range) text. Fonts for character codes greater than 127 are always embedded. Common fonts list includes PDF's base 14 fonts and additional user specified fonts.  # noqa: E501

        :param embed_true_type_fonts_for_ascii: The embed_true_type_fonts_for_ascii of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._embed_true_type_fonts_for_ascii = embed_true_type_fonts_for_ascii

    @property
    def additional_common_font_families(self):
        """Gets the additional_common_font_families of this PdfExportOptions.  # noqa: E501

        Returns or sets an array of user-defined names of font families which Aspose.Slides should consider common.  # noqa: E501

        :return: The additional_common_font_families of this PdfExportOptions.  # noqa: E501
        :rtype: list[str]
        """
        return self._additional_common_font_families

    @additional_common_font_families.setter
    def additional_common_font_families(self, additional_common_font_families):
        """Sets the additional_common_font_families of this PdfExportOptions.

        Returns or sets an array of user-defined names of font families which Aspose.Slides should consider common.  # noqa: E501

        :param additional_common_font_families: The additional_common_font_families of this PdfExportOptions.  # noqa: E501
        :type: list[str]
        """
        self._additional_common_font_families = additional_common_font_families

    @property
    def slides_layout_options(self):
        """Gets the slides_layout_options of this PdfExportOptions.  # noqa: E501

        Slides layouting options  # noqa: E501

        :return: The slides_layout_options of this PdfExportOptions.  # noqa: E501
        :rtype: SlidesLayoutOptions
        """
        return self._slides_layout_options

    @slides_layout_options.setter
    def slides_layout_options(self, slides_layout_options):
        """Sets the slides_layout_options of this PdfExportOptions.

        Slides layouting options  # noqa: E501

        :param slides_layout_options: The slides_layout_options of this PdfExportOptions.  # noqa: E501
        :type: SlidesLayoutOptions
        """
        self._slides_layout_options = slides_layout_options

    @property
    def image_transparent_color(self):
        """Gets the image_transparent_color of this PdfExportOptions.  # noqa: E501

        Image transparent color.  # noqa: E501

        :return: The image_transparent_color of this PdfExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._image_transparent_color

    @image_transparent_color.setter
    def image_transparent_color(self, image_transparent_color):
        """Sets the image_transparent_color of this PdfExportOptions.

        Image transparent color.  # noqa: E501

        :param image_transparent_color: The image_transparent_color of this PdfExportOptions.  # noqa: E501
        :type: str
        """
        self._image_transparent_color = image_transparent_color

    @property
    def apply_image_transparent(self):
        """Gets the apply_image_transparent of this PdfExportOptions.  # noqa: E501

        True to apply specified ImageTransparentColor  to an image.  # noqa: E501

        :return: The apply_image_transparent of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._apply_image_transparent

    @apply_image_transparent.setter
    def apply_image_transparent(self, apply_image_transparent):
        """Sets the apply_image_transparent of this PdfExportOptions.

        True to apply specified ImageTransparentColor  to an image.  # noqa: E501

        :param apply_image_transparent: The apply_image_transparent of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._apply_image_transparent = apply_image_transparent

    @property
    def access_permissions(self):
        """Gets the access_permissions of this PdfExportOptions.  # noqa: E501

        Access permissions that should be granted when the document is opened with user access.  Default is AccessPermissions.None.               # noqa: E501

        :return: The access_permissions of this PdfExportOptions.  # noqa: E501
        :rtype: AccessPermissions
        """
        return self._access_permissions

    @access_permissions.setter
    def access_permissions(self, access_permissions):
        """Sets the access_permissions of this PdfExportOptions.

        Access permissions that should be granted when the document is opened with user access.  Default is AccessPermissions.None.               # noqa: E501

        :param access_permissions: The access_permissions of this PdfExportOptions.  # noqa: E501
        :type: AccessPermissions
        """
        self._access_permissions = access_permissions

    @property
    def hide_ink(self):
        """Gets the hide_ink of this PdfExportOptions.  # noqa: E501

        True to hide Ink elements in exported document.  # noqa: E501

        :return: The hide_ink of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._hide_ink

    @hide_ink.setter
    def hide_ink(self, hide_ink):
        """Sets the hide_ink of this PdfExportOptions.

        True to hide Ink elements in exported document.  # noqa: E501

        :param hide_ink: The hide_ink of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._hide_ink = hide_ink

    @property
    def interpret_mask_op_as_opacity(self):
        """Gets the interpret_mask_op_as_opacity of this PdfExportOptions.  # noqa: E501

        True to use ROP operation or Opacity for rendering brush.  # noqa: E501

        :return: The interpret_mask_op_as_opacity of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._interpret_mask_op_as_opacity

    @interpret_mask_op_as_opacity.setter
    def interpret_mask_op_as_opacity(self, interpret_mask_op_as_opacity):
        """Sets the interpret_mask_op_as_opacity of this PdfExportOptions.

        True to use ROP operation or Opacity for rendering brush.  # noqa: E501

        :param interpret_mask_op_as_opacity: The interpret_mask_op_as_opacity of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._interpret_mask_op_as_opacity = interpret_mask_op_as_opacity

    @property
    def rasterize_unsupported_font_styles(self):
        """Gets the rasterize_unsupported_font_styles of this PdfExportOptions.  # noqa: E501

        True if text should be rasterized as a bitmap and saved to PDF when the font does not support bold styling. This approach can enhance the quality of text in the resulting PDF for certain fonts.  # noqa: E501

        :return: The rasterize_unsupported_font_styles of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._rasterize_unsupported_font_styles

    @rasterize_unsupported_font_styles.setter
    def rasterize_unsupported_font_styles(self, rasterize_unsupported_font_styles):
        """Sets the rasterize_unsupported_font_styles of this PdfExportOptions.

        True if text should be rasterized as a bitmap and saved to PDF when the font does not support bold styling. This approach can enhance the quality of text in the resulting PDF for certain fonts.  # noqa: E501

        :param rasterize_unsupported_font_styles: The rasterize_unsupported_font_styles of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._rasterize_unsupported_font_styles = rasterize_unsupported_font_styles

    @property
    def include_ole_data(self):
        """Gets the include_ole_data of this PdfExportOptions.  # noqa: E501

        True to convert all OLE data from the presentation to embedded files in the resulting PDF.  # noqa: E501

        :return: The include_ole_data of this PdfExportOptions.  # noqa: E501
        :rtype: bool
        """
        return self._include_ole_data

    @include_ole_data.setter
    def include_ole_data(self, include_ole_data):
        """Sets the include_ole_data of this PdfExportOptions.

        True to convert all OLE data from the presentation to embedded files in the resulting PDF.  # noqa: E501

        :param include_ole_data: The include_ole_data of this PdfExportOptions.  # noqa: E501
        :type: bool
        """
        self._include_ole_data = include_ole_data

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
        if not isinstance(other, PdfExportOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
