"""gr.Image() component."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Literal, cast

import numpy as np
import PIL.Image
from gradio_client.documentation import document
from PIL import ImageOps

from gradio import image_utils, utils
from gradio.components.base import Component, StreamingInput
from gradio.data_classes import FileData
from gradio.events import Events

PIL.Image.init()  # fixes https://github.com/gradio-app/gradio/issues/2843


class image_annotator(Component):
    """
    Creates a component to annotate images with bounding boxes. The bounding boxes can be created and edited by the user or be passed by code.
    It is also possible to predefine a set of valid classes and colors.
    """

    EVENTS = [
        Events.clear,
        Events.change,
        Events.upload,
    ]

    data_model = AnnotatedImageData

    def __init__(
        self,
        value: dict | None = None,
        *,
        boxes_alpha: float | None = None,
        label_list: list[str] | None = None,
        label_colors: list[str] | None = None,
        box_min_size: int | None = None,
        handle_size: int | None = None,
        box_thickness: int | None = None,
        box_selected_thickness: int | None = None,
        disable_edit_boxes: bool | None = None,
        single_box: bool = False,
        height: int | str | None = None,
        width: int | str | None = None,
        image_mode: Literal[
            "1", "L", "P", "RGB", "RGBA", "CMYK", "YCbCr", "LAB", "HSV", "I", "F"
        ] = "RGB",
        sources: list[Literal["upload", "webcam", "clipboard"]] | None = [
            "upload",
            "webcam",
            "clipboard",
        ],
        image_type: Literal["numpy", "pil", "filepath"] = "numpy",
        label: str | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = True,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        show_label: bool | None = None,
        show_download_button: bool = True,
        show_share_button: bool | None = None,
        show_clear_button: bool | None = True,
        show_remove_button: bool | None = None,
        handles_cursor: bool | None = True,
        use_default_label: bool | None = False,
        enable_keyboard_shortcuts: bool = True, 
    ):
        """
        Parameters:
            value: A dict or None. The dictionary must contain a key 'image' with either an URL to an image, a numpy image or a PIL image. Optionally it may contain a key 'boxes' with a list of boxes. Each box must be a dict wit the keys: 'xmin', 'ymin', 'xmax' and 'ymax' with the absolute image coordinates of the box. Optionally can also include the keys 'label' and 'color' describing the label and color of the box. Color must be a tuple of RGB values (e.g. `(255,255,255)`). Optionally can also include the keys 'orientation' with a integer between 0 and 3, describing the number of times the image is rotated by 90 degrees in frontend, the rotation is clockwise.
            boxes_alpha: Opacity of the bounding boxes 0 and 1.
            label_list: List of valid labels.
            label_colors: Optional list of colors for each label when `label_list` is used. Colors must be a tuple of RGB values (e.g. `(255,255,255)`).
            box_min_size: Minimum valid bounding box size.
            handle_size: Size of the bounding box resize handles.
            box_thickness: Thickness of the bounding box outline.
            box_selected_thickness: Thickness of the bounding box outline when it is selected.
            disable_edit_boxes: Disables the ability to set and edit the label and color of the boxes.
            single_box: If True, at most one box can be drawn.
            height: The height of the displayed image, specified in pixels if a number is passed, or in CSS units if a string is passed.
            width: The width of the displayed image, specified in pixels if a number is passed, or in CSS units if a string is passed.
            image_mode: "RGB" if color, or "L" if black and white. See https://pillow.readthedocs.io/en/stable/handbook/concepts.html for other supported image modes and their meaning.
            sources: List of sources for the image. "upload" creates a box where user can drop an image file, "webcam" allows user to take snapshot from their webcam, "clipboard" allows users to paste an image from the clipboard. If None, defaults to ["upload", "webcam", "clipboard"].
            image_type: The format the image is converted before being passed into the prediction function. "numpy" converts the image to a numpy array with shape (height, width, 3) and values from 0 to 255, "pil" converts the image to a PIL image object, "filepath" passes a str path to a temporary file containing the image. If the image is SVG, the `type` is ignored and the filepath of the SVG is returned.
            label: The label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, will allow users to upload and annotate an image; if False, can only be used to display annotated images.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            show_label: if True, will display label.
            show_download_button: If True, will show a button to download the image.
            show_share_button: If True, will show a share icon in the corner of the component that allows user to share outputs to Hugging Face Spaces Discussions. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.
            show_clear_button: If True, will show a button to clear the current image.
            show_remove_button: If True, will show a button to remove the selected bounding box.
            handles_cursor: If True, the cursor will change when hovering over box handles in drag mode. Can be CPU-intensive.
            use_default_label: If True, the first item in label_list will be used as the default label when creating boxes.
            enable_keyboard_shortcuts: If True, the component will respond to keyboard events.
        """

        valid_types = ["numpy", "pil", "filepath"]
        if image_type not in valid_types:
            raise ValueError(
                f"Invalid value for parameter `type`: {type}. Please choose from one of: {valid_types}"
            )
        self.image_type = image_type
        self.height = height
        self.width = width
        self.image_mode = image_mode
        
        self.sources = sources
        valid_sources = ["upload", "clipboard", "webcam", None]
        if isinstance(sources, str):
            self.sources = [sources]
        if self.sources is None:
            self.sources = []
        if self.sources is not None:
            for source in self.sources:
                if source not in valid_sources:
                    raise ValueError(
                        f"`sources` must a list consisting of elements in {valid_sources}"
                    )
        
        self.show_download_button = show_download_button
        self.show_share_button = (
            (utils.get_space() is not None)
            if show_share_button is None
            else show_share_button
        )
        self.show_clear_button = show_clear_button
        self.show_remove_button = show_remove_button
        self.handles_cursor = handles_cursor
        self.use_default_label = use_default_label
        self.enable_keyboard_shortcuts = enable_keyboard_shortcuts

        self.boxes_alpha = boxes_alpha
        self.box_min_size = box_min_size
        self.handle_size = handle_size
        self.box_thickness = box_thickness
        self.box_selected_thickness = box_selected_thickness
        self.disable_edit_boxes = disable_edit_boxes
        self.single_box = single_box
        if label_list:
            self.label_list = [(l, i) for i, l in enumerate(label_list)]
        else:
            self.label_list = None
        
        # Parse colors
        self.label_colors = label_colors
        if self.label_colors:
            if (not isinstance(self.label_colors, list)
                or self.label_list is None
                or len(self.label_colors) != len(self.label_list)):
                raise ValueError("``label_colors`` must be a list with the "
                                 "same length as ``label_list``")
            for i, color in enumerate(self.label_colors):
                if isinstance(color, str):
                    if len(color) != 7 or color[0] != "#":
                        raise ValueError(f"Invalid color value {color}")
                elif isinstance(color, (list, tuple)):
                    self.label_colors[i] = rgb2hex(*color)

        super().__init__(
            label=label,
            every=None,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            value=value,
        )

    def preprocess_image(self, image: FileData | None) -> str | None:
        if image is None:
            return None
        file_path = Path(image.path)
        if image.orig_name:
            p = Path(image.orig_name)
            name = p.stem
            suffix = p.suffix.replace(".", "")
            if suffix in ["jpg", "jpeg"]:
                suffix = "jpeg"
        else:
            name = "image"
            suffix = "png"

        if suffix.lower() == "svg":
            return str(file_path)
        
        im = PIL.Image.open(file_path)
        exif = im.getexif()
        # 274 is the code for image rotation and 1 means "correct orientation"
        if exif.get(274, 1) != 1 and hasattr(ImageOps, "exif_transpose"):
            try:
                im = ImageOps.exif_transpose(im)
            except Exception:
                warnings.warn(
                    f"Failed to transpose image {file_path} based on EXIF data."
                )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            im = im.convert(self.image_mode)
        return image_utils.format_image(
            im,
            cast(Literal["numpy", "pil", "filepath"], self.image_type),
            self.GRADIO_CACHE,
            name=name,
            format=suffix,
        )

    def preprocess_boxes(self, boxes: List[dict] | None) -> list:
        parsed_boxes = []
        for box in boxes:
            new_box = {}
            new_box["label"] = box.get("label", "")
            new_box["color"] = (0,0,0)
            if "color" in box:
                match = re.match(r'rgb\((\d+), (\d+), (\d+)\)', box["color"])
                if match:
                    new_box["color"] = tuple(int(match.group(i)) for i in range(1, 4))
            scale_factor = box.get("scaleFactor", 1)
            new_box["xmin"] = round(box["xmin"] / scale_factor)
            new_box["ymin"] = round(box["ymin"] / scale_factor)
            new_box["xmax"] = round(box["xmax"] / scale_factor)
            new_box["ymax"] = round(box["ymax"] / scale_factor)
            parsed_boxes.append(new_box)
        return parsed_boxes

    def preprocess(self, payload: AnnotatedImageData | None) -> AnnotatedImageValue | None:
        """
        Parameters:
            payload: an AnnotatedImageData object.
        Returns:
            A dict with the image and boxes or None.
        """
        if payload is None:
            return None
        
        ret_value = {
            "image": self.preprocess_image(payload.image),
            "boxes": self.preprocess_boxes(payload.boxes),
            "orientation": payload.orientation,
        }
        return ret_value

    def postprocess(self, value: AnnotatedImageValue | None) -> AnnotatedImageData | None:
        """
        Parameters:
            value: A dict with an image and an optional list of boxes or None.
        Returns:
            Returns an AnnotatedImageData object.
        """
        # Check value
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError(f"``value`` must be a dict. Got {type(value)}")
    
        # Check and get boxes
        boxes = value.setdefault("boxes", [])
        if boxes:
            if not isinstance(value["boxes"], (list, tuple)):
                raise ValueError(f"'boxes' must be a list of dicts. Got "
                                 f"{type(value['boxes'])}")
            for box in value["boxes"]:
                if (not isinstance(box, dict)
                    or not set(box.keys()).issubset({"label", "xmin", "ymin", "xmax", "ymax", "color"})
                    or not set(box.keys()).issuperset({"xmin", "ymin", "xmax", "ymax"})
                    ):
                    raise ValueError("Box must be a dict with the following "
                                     "keys: 'xmin', 'ymin', 'xmax', 'ymax', "
                                     f"['label', 'color']'. Got {box}")

        # Check and parse image
        image = value.setdefault("image", None)
        if image is not None:
            if isinstance(image, str) and image.lower().endswith(".svg"):
                image = FileData(path=image, orig_name=Path(image).name)
            else:
                saved = image_utils.save_image(image, self.GRADIO_CACHE)
                orig_name = Path(saved).name if Path(saved).exists() else None
                image = FileData(path=saved, orig_name=orig_name)
        else:
            raise ValueError(f"An image must be provided. Got {value}")
        
        orientation = value.setdefault("orientation", 0)
        if orientation is None:
            orientation = 0

        return AnnotatedImageData(image=image, boxes=boxes, orientation=orientation)

    def process_example(self, value: dict | None) -> FileData | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError(f"``value`` must be a dict. Got {type(value)}")

        image = value.setdefault("image", None)
        if image is not None:
            if isinstance(image, str) and image.lower().endswith(".svg"):
                image = FileData(path=image, orig_name=Path(image).name)
            else:
                saved = image_utils.save_image(image, self.GRADIO_CACHE)
                orig_name = Path(saved).name if Path(saved).exists() else None
                image = FileData(path=saved, orig_name=orig_name)
        else:
            raise ValueError(f"An image must be provided. Got {value}")

        return image

    def example_inputs(self) -> Any:
        return {
            "image": "https://raw.githubusercontent.com/gradio-app/gradio/main/guides/assets/logo.png",
            "boxes": [
                {
                    "xmin": 30,
                    "ymin": 70,
                    "xmax": 530,
                    "ymax": 500,
                    "label": "Gradio",
                    "color": (250,185,0),
                }
            ]
        }
    from typing import Callable, Literal, Sequence, Any, TYPE_CHECKING
    from gradio.blocks import Block
    if TYPE_CHECKING:
        from gradio.components import Timer
        from gradio.components.base import Component

    
    def clear(self,
        fn: Callable[..., Any] | None = None,
        inputs: Block | Sequence[Block] | set[Block] | None = None,
        outputs: Block | Sequence[Block] | None = None,
        api_name: str | None | Literal[False] = None,
        scroll_to_output: bool = False,
        show_progress: Literal["full", "minimal", "hidden"] = "full",
        show_progress_on: Component | Sequence[Component] | None = None,
        queue: bool | None = None,
        batch: bool = False,
        max_batch_size: int = 4,
        preprocess: bool = True,
        postprocess: bool = True,
        cancels: dict[str, Any] | list[dict[str, Any]] | None = None,
        every: Timer | float | None = None,
        trigger_mode: Literal["once", "multiple", "always_last"] | None = None,
        js: str | Literal[True] | None = None,
        concurrency_limit: int | None | Literal["default"] = "default",
        concurrency_id: str | None = None,
        show_api: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
    
        ) -> Dependency:
        """
        Parameters:
            fn: the function to call when this event is triggered. Often a machine learning model's prediction function. Each parameter of the function corresponds to one input component, and the function should return a single value or a tuple of values, with each element in the tuple corresponding to one output component.
            inputs: list of gradio.components to use as inputs. If the function takes no inputs, this should be an empty list.
            outputs: list of gradio.components to use as outputs. If the function returns no outputs, this should be an empty list.
            api_name: defines how the endpoint appears in the API docs. Can be a string, None, or False. If False, the endpoint will not be exposed in the api docs. If set to None, will use the functions name as the endpoint route. If set to a string, the endpoint will be exposed in the api docs with the given name.
            scroll_to_output: if True, will scroll to output component on completion
            show_progress: how to show the progress animation while event is running: "full" shows a spinner which covers the output component area as well as a runtime display in the upper right corner, "minimal" only shows the runtime display, "hidden" shows no progress animation at all
            show_progress_on: Component or list of components to show the progress animation on. If None, will show the progress animation on all of the output components.
            queue: if True, will place the request on the queue, if the queue has been enabled. If False, will not put this event on the queue, even if the queue has been enabled. If None, will use the queue setting of the gradio app.
            batch: if True, then the function should process a batch of inputs, meaning that it should accept a list of input values for each parameter. The lists should be of equal length (and be up to length `max_batch_size`). The function is then *required* to return a tuple of lists (even if there is only 1 output component), with each list in the tuple corresponding to one output component.
            max_batch_size: maximum number of inputs to batch together if this is called from the queue (only relevant if batch=True)
            preprocess: if False, will not run preprocessing of component data before running 'fn' (e.g. leaving it as a base64 string if this method is called with the `Image` component).
            postprocess: if False, will not run postprocessing of component data before returning 'fn' output to the browser.
            cancels: a list of other events to cancel when this listener is triggered. For example, setting cancels=[click_event] will cancel the click_event, where click_event is the return value of another components .click method. Functions that have not yet run (or generators that are iterating) will be cancelled, but functions that are currently running will be allowed to finish.
            every: continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            trigger_mode: if "once" (default for all events except `.change()`) would not allow any submissions while an event is pending. If set to "multiple", unlimited submissions are allowed while pending, and "always_last" (default for `.change()` and `.key_up()` events) would allow a second submission after the pending event is complete.
            js: optional frontend js method to run before running 'fn'. Input arguments for js method are values of 'inputs' and 'outputs', return should be a list of values for output components.
            concurrency_limit: if set, this is the maximum number of this event that can be running simultaneously. Can be set to None to mean no concurrency_limit (any number of this event can be running simultaneously). Set to "default" to use the default concurrency limit (defined by the `default_concurrency_limit` parameter in `Blocks.queue()`, which itself is 1 by default).
            concurrency_id: if set, this is the id of the concurrency group. Events with the same concurrency_id will be limited by the lowest set concurrency_limit.
            show_api: whether to show this event in the "view API" page of the Gradio app, or in the ".view_api()" method of the Gradio clients. Unlike setting api_name to False, setting show_api to False will still allow downstream apps as well as the Clients to use this event. If fn is None, show_api will automatically be set to False.
            key: A unique key for this event listener to be used in @gr.render(). If set, this value identifies an event as identical across re-renders when the key is identical.
        
        """
        ...
    
    def change(self,
        fn: Callable[..., Any] | None = None,
        inputs: Block | Sequence[Block] | set[Block] | None = None,
        outputs: Block | Sequence[Block] | None = None,
        api_name: str | None | Literal[False] = None,
        scroll_to_output: bool = False,
        show_progress: Literal["full", "minimal", "hidden"] = "full",
        show_progress_on: Component | Sequence[Component] | None = None,
        queue: bool | None = None,
        batch: bool = False,
        max_batch_size: int = 4,
        preprocess: bool = True,
        postprocess: bool = True,
        cancels: dict[str, Any] | list[dict[str, Any]] | None = None,
        every: Timer | float | None = None,
        trigger_mode: Literal["once", "multiple", "always_last"] | None = None,
        js: str | Literal[True] | None = None,
        concurrency_limit: int | None | Literal["default"] = "default",
        concurrency_id: str | None = None,
        show_api: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
    
        ) -> Dependency:
        """
        Parameters:
            fn: the function to call when this event is triggered. Often a machine learning model's prediction function. Each parameter of the function corresponds to one input component, and the function should return a single value or a tuple of values, with each element in the tuple corresponding to one output component.
            inputs: list of gradio.components to use as inputs. If the function takes no inputs, this should be an empty list.
            outputs: list of gradio.components to use as outputs. If the function returns no outputs, this should be an empty list.
            api_name: defines how the endpoint appears in the API docs. Can be a string, None, or False. If False, the endpoint will not be exposed in the api docs. If set to None, will use the functions name as the endpoint route. If set to a string, the endpoint will be exposed in the api docs with the given name.
            scroll_to_output: if True, will scroll to output component on completion
            show_progress: how to show the progress animation while event is running: "full" shows a spinner which covers the output component area as well as a runtime display in the upper right corner, "minimal" only shows the runtime display, "hidden" shows no progress animation at all
            show_progress_on: Component or list of components to show the progress animation on. If None, will show the progress animation on all of the output components.
            queue: if True, will place the request on the queue, if the queue has been enabled. If False, will not put this event on the queue, even if the queue has been enabled. If None, will use the queue setting of the gradio app.
            batch: if True, then the function should process a batch of inputs, meaning that it should accept a list of input values for each parameter. The lists should be of equal length (and be up to length `max_batch_size`). The function is then *required* to return a tuple of lists (even if there is only 1 output component), with each list in the tuple corresponding to one output component.
            max_batch_size: maximum number of inputs to batch together if this is called from the queue (only relevant if batch=True)
            preprocess: if False, will not run preprocessing of component data before running 'fn' (e.g. leaving it as a base64 string if this method is called with the `Image` component).
            postprocess: if False, will not run postprocessing of component data before returning 'fn' output to the browser.
            cancels: a list of other events to cancel when this listener is triggered. For example, setting cancels=[click_event] will cancel the click_event, where click_event is the return value of another components .click method. Functions that have not yet run (or generators that are iterating) will be cancelled, but functions that are currently running will be allowed to finish.
            every: continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            trigger_mode: if "once" (default for all events except `.change()`) would not allow any submissions while an event is pending. If set to "multiple", unlimited submissions are allowed while pending, and "always_last" (default for `.change()` and `.key_up()` events) would allow a second submission after the pending event is complete.
            js: optional frontend js method to run before running 'fn'. Input arguments for js method are values of 'inputs' and 'outputs', return should be a list of values for output components.
            concurrency_limit: if set, this is the maximum number of this event that can be running simultaneously. Can be set to None to mean no concurrency_limit (any number of this event can be running simultaneously). Set to "default" to use the default concurrency limit (defined by the `default_concurrency_limit` parameter in `Blocks.queue()`, which itself is 1 by default).
            concurrency_id: if set, this is the id of the concurrency group. Events with the same concurrency_id will be limited by the lowest set concurrency_limit.
            show_api: whether to show this event in the "view API" page of the Gradio app, or in the ".view_api()" method of the Gradio clients. Unlike setting api_name to False, setting show_api to False will still allow downstream apps as well as the Clients to use this event. If fn is None, show_api will automatically be set to False.
            key: A unique key for this event listener to be used in @gr.render(). If set, this value identifies an event as identical across re-renders when the key is identical.
        
        """
        ...
    
    def upload(self,
        fn: Callable[..., Any] | None = None,
        inputs: Block | Sequence[Block] | set[Block] | None = None,
        outputs: Block | Sequence[Block] | None = None,
        api_name: str | None | Literal[False] = None,
        scroll_to_output: bool = False,
        show_progress: Literal["full", "minimal", "hidden"] = "full",
        show_progress_on: Component | Sequence[Component] | None = None,
        queue: bool | None = None,
        batch: bool = False,
        max_batch_size: int = 4,
        preprocess: bool = True,
        postprocess: bool = True,
        cancels: dict[str, Any] | list[dict[str, Any]] | None = None,
        every: Timer | float | None = None,
        trigger_mode: Literal["once", "multiple", "always_last"] | None = None,
        js: str | Literal[True] | None = None,
        concurrency_limit: int | None | Literal["default"] = "default",
        concurrency_id: str | None = None,
        show_api: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
    
        ) -> Dependency:
        """
        Parameters:
            fn: the function to call when this event is triggered. Often a machine learning model's prediction function. Each parameter of the function corresponds to one input component, and the function should return a single value or a tuple of values, with each element in the tuple corresponding to one output component.
            inputs: list of gradio.components to use as inputs. If the function takes no inputs, this should be an empty list.
            outputs: list of gradio.components to use as outputs. If the function returns no outputs, this should be an empty list.
            api_name: defines how the endpoint appears in the API docs. Can be a string, None, or False. If False, the endpoint will not be exposed in the api docs. If set to None, will use the functions name as the endpoint route. If set to a string, the endpoint will be exposed in the api docs with the given name.
            scroll_to_output: if True, will scroll to output component on completion
            show_progress: how to show the progress animation while event is running: "full" shows a spinner which covers the output component area as well as a runtime display in the upper right corner, "minimal" only shows the runtime display, "hidden" shows no progress animation at all
            show_progress_on: Component or list of components to show the progress animation on. If None, will show the progress animation on all of the output components.
            queue: if True, will place the request on the queue, if the queue has been enabled. If False, will not put this event on the queue, even if the queue has been enabled. If None, will use the queue setting of the gradio app.
            batch: if True, then the function should process a batch of inputs, meaning that it should accept a list of input values for each parameter. The lists should be of equal length (and be up to length `max_batch_size`). The function is then *required* to return a tuple of lists (even if there is only 1 output component), with each list in the tuple corresponding to one output component.
            max_batch_size: maximum number of inputs to batch together if this is called from the queue (only relevant if batch=True)
            preprocess: if False, will not run preprocessing of component data before running 'fn' (e.g. leaving it as a base64 string if this method is called with the `Image` component).
            postprocess: if False, will not run postprocessing of component data before returning 'fn' output to the browser.
            cancels: a list of other events to cancel when this listener is triggered. For example, setting cancels=[click_event] will cancel the click_event, where click_event is the return value of another components .click method. Functions that have not yet run (or generators that are iterating) will be cancelled, but functions that are currently running will be allowed to finish.
            every: continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            trigger_mode: if "once" (default for all events except `.change()`) would not allow any submissions while an event is pending. If set to "multiple", unlimited submissions are allowed while pending, and "always_last" (default for `.change()` and `.key_up()` events) would allow a second submission after the pending event is complete.
            js: optional frontend js method to run before running 'fn'. Input arguments for js method are values of 'inputs' and 'outputs', return should be a list of values for output components.
            concurrency_limit: if set, this is the maximum number of this event that can be running simultaneously. Can be set to None to mean no concurrency_limit (any number of this event can be running simultaneously). Set to "default" to use the default concurrency limit (defined by the `default_concurrency_limit` parameter in `Blocks.queue()`, which itself is 1 by default).
            concurrency_id: if set, this is the id of the concurrency group. Events with the same concurrency_id will be limited by the lowest set concurrency_limit.
            show_api: whether to show this event in the "view API" page of the Gradio app, or in the ".view_api()" method of the Gradio clients. Unlike setting api_name to False, setting show_api to False will still allow downstream apps as well as the Clients to use this event. If fn is None, show_api will automatically be set to False.
            key: A unique key for this event listener to be used in @gr.render(). If set, this value identifies an event as identical across re-renders when the key is identical.
        
        """
        ...
