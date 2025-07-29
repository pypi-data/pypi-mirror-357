# coding: utf-8

# flake8: noqa
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

from __future__ import absolute_import

# import models into model package
from asposeslidescloud.models.accent_element import AccentElement
from asposeslidescloud.models.access_permissions import AccessPermissions
from asposeslidescloud.models.add_layout_slide import AddLayoutSlide
from asposeslidescloud.models.add_master_slide import AddMasterSlide
from asposeslidescloud.models.add_shape import AddShape
from asposeslidescloud.models.add_slide import AddSlide
from asposeslidescloud.models.alpha_bi_level_effect import AlphaBiLevelEffect
from asposeslidescloud.models.alpha_ceiling_effect import AlphaCeilingEffect
from asposeslidescloud.models.alpha_floor_effect import AlphaFloorEffect
from asposeslidescloud.models.alpha_inverse_effect import AlphaInverseEffect
from asposeslidescloud.models.alpha_modulate_effect import AlphaModulateEffect
from asposeslidescloud.models.alpha_modulate_fixed_effect import AlphaModulateFixedEffect
from asposeslidescloud.models.alpha_replace_effect import AlphaReplaceEffect
from asposeslidescloud.models.api_info import ApiInfo
from asposeslidescloud.models.arc_to_path_segment import ArcToPathSegment
from asposeslidescloud.models.array_element import ArrayElement
from asposeslidescloud.models.arrow_head_properties import ArrowHeadProperties
from asposeslidescloud.models.audio_frame import AudioFrame
from asposeslidescloud.models.axes import Axes
from asposeslidescloud.models.axis import Axis
from asposeslidescloud.models.axis_type import AxisType
from asposeslidescloud.models.bar_element import BarElement
from asposeslidescloud.models.base64_input_file import Base64InputFile
from asposeslidescloud.models.bi_level_effect import BiLevelEffect
from asposeslidescloud.models.block_element import BlockElement
from asposeslidescloud.models.blur_effect import BlurEffect
from asposeslidescloud.models.blur_image_effect import BlurImageEffect
from asposeslidescloud.models.border_box_element import BorderBoxElement
from asposeslidescloud.models.box_element import BoxElement
from asposeslidescloud.models.bubble_chart_data_point import BubbleChartDataPoint
from asposeslidescloud.models.bubble_series import BubbleSeries
from asposeslidescloud.models.camera import Camera
from asposeslidescloud.models.caption_track import CaptionTrack
from asposeslidescloud.models.caption_tracks import CaptionTracks
from asposeslidescloud.models.chart import Chart
from asposeslidescloud.models.chart_category import ChartCategory
from asposeslidescloud.models.chart_lines_format import ChartLinesFormat
from asposeslidescloud.models.chart_series_group import ChartSeriesGroup
from asposeslidescloud.models.chart_title import ChartTitle
from asposeslidescloud.models.chart_wall import ChartWall
from asposeslidescloud.models.chart_wall_type import ChartWallType
from asposeslidescloud.models.close_path_segment import ClosePathSegment
from asposeslidescloud.models.color_change_effect import ColorChangeEffect
from asposeslidescloud.models.color_replace_effect import ColorReplaceEffect
from asposeslidescloud.models.color_scheme import ColorScheme
from asposeslidescloud.models.comment_author import CommentAuthor
from asposeslidescloud.models.comment_authors import CommentAuthors
from asposeslidescloud.models.common_slide_view_properties import CommonSlideViewProperties
from asposeslidescloud.models.connector import Connector
from asposeslidescloud.models.cubic_bezier_to_path_segment import CubicBezierToPathSegment
from asposeslidescloud.models.custom_dash_pattern import CustomDashPattern
from asposeslidescloud.models.data_point import DataPoint
from asposeslidescloud.models.data_source import DataSource
from asposeslidescloud.models.delimiter_element import DelimiterElement
from asposeslidescloud.models.disc_usage import DiscUsage
from asposeslidescloud.models.document import Document
from asposeslidescloud.models.document_properties import DocumentProperties
from asposeslidescloud.models.document_property import DocumentProperty
from asposeslidescloud.models.document_replace_result import DocumentReplaceResult
from asposeslidescloud.models.drawing_guide import DrawingGuide
from asposeslidescloud.models.duotone_effect import DuotoneEffect
from asposeslidescloud.models.effect import Effect
from asposeslidescloud.models.effect_format import EffectFormat
from asposeslidescloud.models.entity_exists import EntityExists
from asposeslidescloud.models.error import Error
from asposeslidescloud.models.error_details import ErrorDetails
from asposeslidescloud.models.export_format import ExportFormat
from asposeslidescloud.models.export_options import ExportOptions
from asposeslidescloud.models.file_version import FileVersion
from asposeslidescloud.models.file_versions import FileVersions
from asposeslidescloud.models.files_list import FilesList
from asposeslidescloud.models.files_upload_result import FilesUploadResult
from asposeslidescloud.models.fill_format import FillFormat
from asposeslidescloud.models.fill_overlay_effect import FillOverlayEffect
from asposeslidescloud.models.fill_overlay_image_effect import FillOverlayImageEffect
from asposeslidescloud.models.font_data import FontData
from asposeslidescloud.models.font_fallback_rule import FontFallbackRule
from asposeslidescloud.models.font_scheme import FontScheme
from asposeslidescloud.models.font_set import FontSet
from asposeslidescloud.models.font_subst_rule import FontSubstRule
from asposeslidescloud.models.fonts_data import FontsData
from asposeslidescloud.models.format_scheme import FormatScheme
from asposeslidescloud.models.fraction_element import FractionElement
from asposeslidescloud.models.function_element import FunctionElement
from asposeslidescloud.models.geometry_path import GeometryPath
from asposeslidescloud.models.geometry_paths import GeometryPaths
from asposeslidescloud.models.geometry_shape import GeometryShape
from asposeslidescloud.models.gif_export_options import GifExportOptions
from asposeslidescloud.models.glow_effect import GlowEffect
from asposeslidescloud.models.gradient_fill import GradientFill
from asposeslidescloud.models.gradient_fill_stop import GradientFillStop
from asposeslidescloud.models.graphical_object import GraphicalObject
from asposeslidescloud.models.gray_scale_effect import GrayScaleEffect
from asposeslidescloud.models.group_shape import GroupShape
from asposeslidescloud.models.grouping_character_element import GroupingCharacterElement
from asposeslidescloud.models.handout_layouting_options import HandoutLayoutingOptions
from asposeslidescloud.models.header_footer import HeaderFooter
from asposeslidescloud.models.hsl_effect import HslEffect
from asposeslidescloud.models.html5_export_options import Html5ExportOptions
from asposeslidescloud.models.html_export_options import HtmlExportOptions
from asposeslidescloud.models.hyperlink import Hyperlink
from asposeslidescloud.models.i_shape_export_options import IShapeExportOptions
from asposeslidescloud.models.image import Image
from asposeslidescloud.models.image_export_format import ImageExportFormat
from asposeslidescloud.models.image_export_options import ImageExportOptions
from asposeslidescloud.models.image_export_options_base import ImageExportOptionsBase
from asposeslidescloud.models.image_transform_effect import ImageTransformEffect
from asposeslidescloud.models.images import Images
from asposeslidescloud.models.inner_shadow_effect import InnerShadowEffect
from asposeslidescloud.models.input import Input
from asposeslidescloud.models.input_file import InputFile
from asposeslidescloud.models.interactive_sequence import InteractiveSequence
from asposeslidescloud.models.layout_slide import LayoutSlide
from asposeslidescloud.models.layout_slides import LayoutSlides
from asposeslidescloud.models.left_sub_superscript_element import LeftSubSuperscriptElement
from asposeslidescloud.models.legend import Legend
from asposeslidescloud.models.light_rig import LightRig
from asposeslidescloud.models.limit_element import LimitElement
from asposeslidescloud.models.line_format import LineFormat
from asposeslidescloud.models.line_to_path_segment import LineToPathSegment
from asposeslidescloud.models.literals import Literals
from asposeslidescloud.models.luminance_effect import LuminanceEffect
from asposeslidescloud.models.markdown_export_options import MarkdownExportOptions
from asposeslidescloud.models.master_slide import MasterSlide
from asposeslidescloud.models.master_slides import MasterSlides
from asposeslidescloud.models.math_element import MathElement
from asposeslidescloud.models.math_format import MathFormat
from asposeslidescloud.models.math_paragraph import MathParagraph
from asposeslidescloud.models.matrix_element import MatrixElement
from asposeslidescloud.models.merge import Merge
from asposeslidescloud.models.merging_source import MergingSource
from asposeslidescloud.models.move_to_path_segment import MoveToPathSegment
from asposeslidescloud.models.nary_operator_element import NaryOperatorElement
from asposeslidescloud.models.no_fill import NoFill
from asposeslidescloud.models.normal_view_restored_properties import NormalViewRestoredProperties
from asposeslidescloud.models.notes_comments_layouting_options import NotesCommentsLayoutingOptions
from asposeslidescloud.models.notes_slide import NotesSlide
from asposeslidescloud.models.notes_slide_export_format import NotesSlideExportFormat
from asposeslidescloud.models.notes_slide_header_footer import NotesSlideHeaderFooter
from asposeslidescloud.models.object_exist import ObjectExist
from asposeslidescloud.models.ole_object_frame import OleObjectFrame
from asposeslidescloud.models.one_value_chart_data_point import OneValueChartDataPoint
from asposeslidescloud.models.one_value_series import OneValueSeries
from asposeslidescloud.models.operation import Operation
from asposeslidescloud.models.operation_error import OperationError
from asposeslidescloud.models.operation_progress import OperationProgress
from asposeslidescloud.models.ordered_merge_request import OrderedMergeRequest
from asposeslidescloud.models.outer_shadow_effect import OuterShadowEffect
from asposeslidescloud.models.output_file import OutputFile
from asposeslidescloud.models.paragraph import Paragraph
from asposeslidescloud.models.paragraph_format import ParagraphFormat
from asposeslidescloud.models.paragraphs import Paragraphs
from asposeslidescloud.models.path_input_file import PathInputFile
from asposeslidescloud.models.path_output_file import PathOutputFile
from asposeslidescloud.models.path_segment import PathSegment
from asposeslidescloud.models.pattern_fill import PatternFill
from asposeslidescloud.models.pdf_export_options import PdfExportOptions
from asposeslidescloud.models.pdf_import_options import PdfImportOptions
from asposeslidescloud.models.picture_fill import PictureFill
from asposeslidescloud.models.picture_frame import PictureFrame
from asposeslidescloud.models.pipeline import Pipeline
from asposeslidescloud.models.placeholder import Placeholder
from asposeslidescloud.models.placeholders import Placeholders
from asposeslidescloud.models.plot_area import PlotArea
from asposeslidescloud.models.portion import Portion
from asposeslidescloud.models.portion_format import PortionFormat
from asposeslidescloud.models.portions import Portions
from asposeslidescloud.models.pptx_export_options import PptxExportOptions
from asposeslidescloud.models.presentation_to_merge import PresentationToMerge
from asposeslidescloud.models.presentations_merge_request import PresentationsMergeRequest
from asposeslidescloud.models.preset_shadow_effect import PresetShadowEffect
from asposeslidescloud.models.protection_properties import ProtectionProperties
from asposeslidescloud.models.quadratic_bezier_to_path_segment import QuadraticBezierToPathSegment
from asposeslidescloud.models.radical_element import RadicalElement
from asposeslidescloud.models.reflection_effect import ReflectionEffect
from asposeslidescloud.models.remove_shape import RemoveShape
from asposeslidescloud.models.remove_slide import RemoveSlide
from asposeslidescloud.models.reorder_slide import ReorderSlide
from asposeslidescloud.models.replace_text import ReplaceText
from asposeslidescloud.models.request_input_file import RequestInputFile
from asposeslidescloud.models.reset_slide import ResetSlide
from asposeslidescloud.models.resource_base import ResourceBase
from asposeslidescloud.models.resource_uri import ResourceUri
from asposeslidescloud.models.response_output_file import ResponseOutputFile
from asposeslidescloud.models.right_sub_superscript_element import RightSubSuperscriptElement
from asposeslidescloud.models.save import Save
from asposeslidescloud.models.save_shape import SaveShape
from asposeslidescloud.models.save_slide import SaveSlide
from asposeslidescloud.models.scatter_chart_data_point import ScatterChartDataPoint
from asposeslidescloud.models.scatter_series import ScatterSeries
from asposeslidescloud.models.section import Section
from asposeslidescloud.models.section_zoom_frame import SectionZoomFrame
from asposeslidescloud.models.sections import Sections
from asposeslidescloud.models.series import Series
from asposeslidescloud.models.series_marker import SeriesMarker
from asposeslidescloud.models.shape import Shape
from asposeslidescloud.models.shape_base import ShapeBase
from asposeslidescloud.models.shape_bevel import ShapeBevel
from asposeslidescloud.models.shape_export_format import ShapeExportFormat
from asposeslidescloud.models.shape_image_export_options import ShapeImageExportOptions
from asposeslidescloud.models.shape_thumbnail_bounds import ShapeThumbnailBounds
from asposeslidescloud.models.shape_type import ShapeType
from asposeslidescloud.models.shapes import Shapes
from asposeslidescloud.models.shapes_alignment_type import ShapesAlignmentType
from asposeslidescloud.models.slide import Slide
from asposeslidescloud.models.slide_animation import SlideAnimation
from asposeslidescloud.models.slide_background import SlideBackground
from asposeslidescloud.models.slide_comment import SlideComment
from asposeslidescloud.models.slide_comment_base import SlideCommentBase
from asposeslidescloud.models.slide_comments import SlideComments
from asposeslidescloud.models.slide_export_format import SlideExportFormat
from asposeslidescloud.models.slide_modern_comment import SlideModernComment
from asposeslidescloud.models.slide_properties import SlideProperties
from asposeslidescloud.models.slide_replace_result import SlideReplaceResult
from asposeslidescloud.models.slide_show_properties import SlideShowProperties
from asposeslidescloud.models.slide_show_transition import SlideShowTransition
from asposeslidescloud.models.slides import Slides
from asposeslidescloud.models.slides_layout_options import SlidesLayoutOptions
from asposeslidescloud.models.smart_art import SmartArt
from asposeslidescloud.models.smart_art_node import SmartArtNode
from asposeslidescloud.models.smart_art_shape import SmartArtShape
from asposeslidescloud.models.soft_edge_effect import SoftEdgeEffect
from asposeslidescloud.models.solid_fill import SolidFill
from asposeslidescloud.models.special_slide_type import SpecialSlideType
from asposeslidescloud.models.split_document_result import SplitDocumentResult
from asposeslidescloud.models.storage_exist import StorageExist
from asposeslidescloud.models.storage_file import StorageFile
from asposeslidescloud.models.subscript_element import SubscriptElement
from asposeslidescloud.models.summary_zoom_frame import SummaryZoomFrame
from asposeslidescloud.models.summary_zoom_section import SummaryZoomSection
from asposeslidescloud.models.superscript_element import SuperscriptElement
from asposeslidescloud.models.svg_export_options import SvgExportOptions
from asposeslidescloud.models.swf_export_options import SwfExportOptions
from asposeslidescloud.models.table import Table
from asposeslidescloud.models.table_cell import TableCell
from asposeslidescloud.models.table_cell_merge_options import TableCellMergeOptions
from asposeslidescloud.models.table_cell_split_type import TableCellSplitType
from asposeslidescloud.models.table_column import TableColumn
from asposeslidescloud.models.table_row import TableRow
from asposeslidescloud.models.task import Task
from asposeslidescloud.models.text_bounds import TextBounds
from asposeslidescloud.models.text_element import TextElement
from asposeslidescloud.models.text_frame_format import TextFrameFormat
from asposeslidescloud.models.text_item import TextItem
from asposeslidescloud.models.text_items import TextItems
from asposeslidescloud.models.theme import Theme
from asposeslidescloud.models.three_d_format import ThreeDFormat
from asposeslidescloud.models.tiff_export_options import TiffExportOptions
from asposeslidescloud.models.tint_effect import TintEffect
from asposeslidescloud.models.update_background import UpdateBackground
from asposeslidescloud.models.update_shape import UpdateShape
from asposeslidescloud.models.vba_module import VbaModule
from asposeslidescloud.models.vba_project import VbaProject
from asposeslidescloud.models.vba_reference import VbaReference
from asposeslidescloud.models.video_export_options import VideoExportOptions
from asposeslidescloud.models.video_frame import VideoFrame
from asposeslidescloud.models.view_properties import ViewProperties
from asposeslidescloud.models.workbook import Workbook
from asposeslidescloud.models.xy_series import XYSeries
from asposeslidescloud.models.xaml_export_options import XamlExportOptions
from asposeslidescloud.models.xps_export_options import XpsExportOptions
from asposeslidescloud.models.zoom_frame import ZoomFrame
from asposeslidescloud.models.zoom_object import ZoomObject
