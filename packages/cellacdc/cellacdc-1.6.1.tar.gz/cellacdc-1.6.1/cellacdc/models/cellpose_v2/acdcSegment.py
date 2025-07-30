import os

import numpy as np

import skimage.measure

from cellpose import models
from cellacdc import printl, myutils, core

from _types import NotGUIParam
from typing import Tuple
import torch

class AvailableModels:
    from cellpose.models import MODEL_NAMES
    values = MODEL_NAMES
    
    is_exclusive_with = ['model_path']
    default_exclusive = 'Using custom model'

class Model:
    def __init__(
            self, 
            model_type: AvailableModels='cyto', 
            model_path: os.PathLike='',
            net_avg:bool=False, 
            gpu:bool=False,
            directml_gpu:NotGUIParam=False,
            device:torch.device|int='None',
            custom_concatenation:bool=False,
            custom_style_on:bool=True,
            custom_residual_on:bool=True,
            custom_diam_mean:float=30.0,
            backbone:NotGUIParam=None,

        ):
        """Initialize cellpose 2  model

        Parameters
        ----------
        model_type : AvailableModels, optional
            Cellpose model type to use. Default is 'cyto3'. Mutually exclusive
            with `model_path`. If you want to use a custom model, set
            `model_path` to the path of the model file.
        model_path : os.PathLike, optional
            Path to a custom cellpose model file. If set, it will override
            `model_type`. If you want to use a custom model, set this to the
            path of the model file. Default is None.
        gpu : bool, optional
            If True and PyTorch for your GPU is correctly installed, 
            denoising and segmentation processes will run on the GPU. 
            Default is False
        directml_gpu : bool, optional
            If True, will attempt to use DirectML for GPU acceleration.
            Only for v3 and v4. v2 loads the model later, which causes problems. Dont want to edit cellpose code too much...
        device : torch.device or int or None
            If not None, this is the device used for running the model
            (torch.device('cuda') or torch.device('cpu')). 
            It overrides `gpu`, recommended if you want to use a specific GPU 
            (e.g. torch.device('cuda:1'). Default is None
        custom_concatenation : bool, optional
            Only effects custom trained models. See cellpose v2 for more info.
        custom_style_on : bool, optional
            Only effects custom trained models. See cellpose v2 for more info.
        custom_residual_on : bool, optional
            Only effects custom trained models. See cellpose v2 for more info.
        custom_diam_mean : float, optional
            Only effects custom trained models. See cellpose v2 for more info.
            Default is 30.0
        backbone : NotGUIParam, optional
            Only for v3

        """

        self.initConstants()
        model_type, model_path, device = myutils.translateStrNone(model_type, model_path, device)
        
        if model_path is not None and model_type is not None:
            raise TypeError(
                "You cannot set both `model_type` and `model_path`. "
                "Please set only one of them."
            )
        
        if model_path is None and model_type is None:
            raise TypeError(
                "You must set either `model_type` or `model_path`. "
                "Please set one of them."
            )
        
        major_version = self.cp_version

        print(f'Initializing Cellpose v{major_version}...')

        if directml_gpu:
            from cellacdc.models.cellpose_v2._directML import init_directML
            directml_gpu = init_directML()

        if directml_gpu and gpu:
            printl(
                """
                gpu is preferable to directml_gpu, but doesn't work with non NVIDIA GPUs.
                Since directml_gpu and set to True, the gpu argument will be ignored.
                """
            )
            gpu = False

        if major_version == 3:
            if model_type:
                try:
                    self.model = models.Cellpose(
                        gpu=gpu,
                        device=device,
                        model_type=model_type,
                        backbone=backbone,
                    )
                    self._sizemodelnotfound = False                    

                except FileNotFoundError:
                    printl(f'Size model for {model_type} not found.')
                    self._sizemodelnotfound = True
                    self.model = models.CellposeModel(
                        gpu=gpu,
                        device=device,
                        model_type=model_type,
                        backbone=backbone,
                        )
            elif model_path is not None:
                self._sizemodelnotfound = True
                self.model = models.CellposeModel(
                    gpu=gpu,
                    device=device,
                    pretrained_model=model_path,
                    backbone=backbone,
                )
        else:
            if model_type:
                try:
                    self.model = models.Cellpose(
                        gpu=gpu, net_avg=net_avg, 
                        model_type=model_type,
                        device=device,
                    )
                    self._sizemodelnotfound = False
                except FileNotFoundError:
                    self._sizemodelnotfound = True
                    self.model = models.CellposeModel(
                        gpu=gpu, net_avg=net_avg, model_type=model_type,
                        device=device,
                    )
            elif model_path is not None:
                self._sizemodelnotfound = True
                self.model = models.CellposeModel(
                    gpu=gpu, net_avg=net_avg, device=device,
                    pretrained_model=model_path,
                    concatenation=custom_concatenation,
                    style_on=custom_style_on,
                    residual_on=custom_residual_on,
                    diam_mean=custom_diam_mean,
                )
        
        if directml_gpu:
            from cellacdc.models.cellpose_v2._directML import setup_directML
            setup_directML(self)

            from cellacdc.core import fix_sparse_directML
            fix_sparse_directML()
        
        if gpu: # sometimes gpu is not properly set up ^^
            from cellacdc.models.cellpose_v2._directML import setup_custom_device
            if device is None:
                device = 0
            try:
                device = int(device)
            except ValueError:
                pass

            if isinstance(device, int):
                device = torch.device(f'cuda:{device}')
            elif isinstance(device, str):
                device = torch.device(device)
            
            setup_custom_device(self, device)

    
    def initConstants(self):
        self.is_rgb = False
        self.img_shape = None
        self.img_ndim = None
        self.z_axis = None
        self.channel_axis = None
        self.cp_version  = myutils.get_cellpose_major_version()
        self._sizemodelnotfound = True
        
    def setupLogger(self, logger):
        models.models_logger = logger
    
    def closeLogger(self):
        handlers = models.models_logger.handlers[:]
        for handler in handlers:
            handler.close()
            models.models_logger.removeHandler(handler)
    
    def _eval(self, image, **kwargs):
        if self.cp_version == 4:
            del kwargs['channels']
            kwargs['channel_axis'] = self.channel_axis
            kwargs['z_axis'] = self.z_axis
            return self.model.eval(image, **kwargs)[0]
        else:
            return self.model.eval(image, **kwargs)[0]
    
    def second_ch_img_to_stack(self, first_ch_data, second_ch_data):
        # The 'cyto' model can work with a second channel (e.g., nucleus).
        # However, it needs to be encoded into one of the RGB channels
        # Here we put the first channel in the 'red' channel and the 
        # second channel in the 'green' channel. We then pass
        # `channels = [1,2]` to the segment method
        rgb_stack = np.zeros((*first_ch_data.shape, 3), dtype=first_ch_data.dtype)
        
        R_slice = [slice(None)]*(rgb_stack.ndim)
        R_slice[-1] = 0
        R_slice = tuple(R_slice)
        rgb_stack[R_slice] = first_ch_data

        G_slice = [slice(None)]*(rgb_stack.ndim)
        G_slice[-1] = 1
        G_slice = tuple(G_slice)

        rgb_stack[G_slice] = second_ch_data
        
        self.is_rgb = True

        return rgb_stack
    
    def _get_eval_kwargs(
            self, image,
            diameter=0.0,
            flow_threshold=0.4,
            cellprob_threshold=0.0,
            stitch_threshold=0.0,
            min_size=15,
            anisotropy=0.0,
            normalize=True,
            resample=True,
            segment_3D_volume=False,
            **kwargs
        ):

        if anisotropy == 0.0 and segment_3D_volume:
            raise TypeError(
                'Anisotropy is 0.0 but segment_3D_volume is True. '
                'Please set anisotropy to a non-zero value.'
            )

        if diameter == 0.0 and self._sizemodelnotfound:
            raise TypeError(
                'Diameter is 0.0 but size model is not found. '
                'Please set diameter to a non-zero value.'
            )
    

        if self.img_shape is None:
            self.img_shape = image.shape
        if self.img_ndim is None:
            self.img_ndim = len(self.img_shape)
        isRGB = self.img_shape[-1] == 3 or self.img_shape[-1] == 4
        isZstack = (self.img_ndim==3 and not isRGB) or (self.img_ndim==4)

        if anisotropy == 0 or not isZstack:
            printl(
                'Anisotropy is set to 1.0 (assuming isotropic data) '
                'or irrelevant, since not a z-stack.'
            )

            anisotropy = 1.0
        
        do_3D = segment_3D_volume
        if not isZstack:
            stitch_threshold = 0.0
            segment_3D_volume = False
            do_3D = False
        
        if stitch_threshold > 0:
            printl(
                'Using stiching mode instead of trying to segment 3D volume.'
                )
            do_3D = False
        
        if isZstack and flow_threshold > 0:
            printl(
                'Flow threshold is not used for 3D segmentation. '
                'Setting it to 0.0.'
            )
            flow_threshold = 0.0
            
        if flow_threshold==0.0:
            flow_threshold = None

        channels = [0,0] if not isRGB else [1,2]

        eval_kwargs = {
            'channels': channels,
            'diameter': diameter,
            'flow_threshold': flow_threshold,
            'cellprob_threshold': cellprob_threshold,
            'stitch_threshold': stitch_threshold,
            'min_size': min_size,
            'normalize': normalize,
            'do_3D': do_3D,
            'anisotropy': anisotropy,
            'resample': resample
        }

        if not segment_3D_volume and isZstack and stitch_threshold>0:
            raise TypeError(
                "`stitch_threshold` must be 0 when segmenting slice-by-slice. "
                "Alternatively, set `segment_3D_volume = True`."
            )
        
        return eval_kwargs, isZstack

    def segment(
            self, image,
            diameter:float=0.0,
            flow_threshold:float=0.4,
            cellprob_threshold:float=0.0,
            stitch_threshold:float=0.0,
            min_size:int=15,
            anisotropy:float=0.0,
            normalize:bool=True,
            resample:bool=True,
            segment_3D_volume:bool=False            
        ):
        """Segment image using cellpose eval

        Parameters
        ----------
        image : (Y, X) or (Z, Y, X) numpy.ndarray
            Input image. Either 2D or 3D z-stack.
        diameter : float, optional
            Average diameter (in pixels) of the obejcts of interest. 
            Default is 0.0
        flow_threshold : float, optional
            Flow error threshold (all cells with errors below threshold are 
            kept) (not used for 3D). Default is 0.4
        cellprob_threshold : float, optional
            All pixels with value above threshold will be part of an object. 
            Decrease this value to find more and larger masks. Default is 0.0
        stitch_threshold : float, optional
            If `stitch_threshold` is greater than 0.0 and `segment_3D_volume` 
            is True, masks are stitched in 3D to return volume segmentation. 
            Default is 0.0
        min_size : int, optional
            Minimum number of pixels per mask, you can turn off this filter 
            with `min_size = -1`. Default is 15
        anisotropy : float, optional
            For 3D segmentation, optional rescaling factor (e.g. set to 2.0 if 
            Z is sampled half as dense as X or Y). Default is 0.0
        normalize : bool, optional
            If True, normalize image using the other parameters. 
            Default is True
        resample : bool, optional
            Run dynamics at original image size (will be slower but create 
            more accurate boundaries). Default is True
        segment_3D_volume : bool, optional
            If True and input `image` is a 3D z-stack the entire z-stack 
            is passed to cellpose model. If False, Cell-ACDC will force one 
            z-slice at the time. Best results with 3D data are obtained by 
            passing the entire z-stack, but with a `stitch_threshold` greater 
            than 0 (e.g., 0.4). This way cellpose will internally segment 
            slice-by-slice and it will merge the resulting z-slice masks 
            belonging to the same object. 
            Default is False

        Returns
        -------
        np.ndarray of ints
            Segmentations masks array

        Raises
        ------
        TypeError
            `stitch_threshold` must be 0 when segmenting slice-by-slice.
        """        
        # Preprocess image
        # image = image/image.max()
        # image = skimage.filters.gaussian(image, sigma=1)
        # image = skimage.exposure.equalize_adapthist(image)
        self.img_shape = image.shape
        self.img_ndim = len(self.img_shape)

        eval_kwargs, isZstack = self._get_eval_kwargs(
            image,
            diameter=diameter,
            flow_threshold=flow_threshold,
            cellprob_threshold=cellprob_threshold,
            stitch_threshold=stitch_threshold,
            min_size=min_size,
            anisotropy=anisotropy,
            normalize=normalize,
            resample=resample,
            segment_3D_volume=segment_3D_volume         
        )

        labels = self._eval_loop(
            image,
            segment_3D_volume=segment_3D_volume,
            isZstack=isZstack,
            **eval_kwargs
        )

        self.img_shape = None
        self.img_ndim = None

        return labels

    def _eval_loop(
            self, images, segment_3D_volume, isZstack, innit_imgs=True, **eval_kwargs
        ):
        """No support for time lapse. This is handles in self._segment3DT_eval

        Parameters
        ----------
        images : np.ndarray
            Input image to be segmented. It can be 2D, 3D or 4D.
        segment_3D_volume : bool
            If True, the image is assumed to be a 3D z-stack.
        isZstack : bool
            If True, the image is assumed to be a z-stack.
        innit_imgs : bool, optional
            If True, the image is initialized. Default is True.


        Returns
        -------
        np.ndarray
            Segmentation masks array. If `segment_3D_volume` is True, 
            the shape is (Z, Y, X) or (T, Z, Y, X). If `segment_3D_volume` 
            is False, the shape is (Y, X) or (T, Y, X).
        """
        if self.img_shape is None:
            self.img_shape = images.shape

        if not segment_3D_volume and isZstack:
            labels = np.zeros(self.img_shape, dtype=np.uint32)
            if innit_imgs:
                images, z_axis, channel_axis = _initialize_image(images, self.is_rgb, 
                                        iter_axis_zstack=0,
                                        isZstack=True,    
                                        )
                self.channel_axis = channel_axis -1
            for i, _img in enumerate(images):
                
                lab = self._eval(_img, **eval_kwargs)
                labels[i] = lab
            labels = skimage.measure.label(labels>0)
        else:
            if innit_imgs:
                images, z_axis, channel_axis = _initialize_image(images, self.is_rgb,
                                            isZstack=isZstack,
                                            )
                self.z_axis = z_axis
                self.channel_axis = channel_axis
            labels = self._eval(images, **eval_kwargs)
        
        return labels
    
    def _segment3DT_eval(
            self, video_data, isZstack, eval_kwargs, innit_imgs=True, **kwargs
        ):
        if not kwargs['segment_3D_volume'] and isZstack:
            if innit_imgs:
                images, z_axis, channel_axis = _initialize_image(video_data, self.is_rgb,
                                iter_axis_time=0,
                                iter_axis_zstack=1,
                                timelapse=True,
                                isZstack=isZstack,
                                )
                
                self.z_axis = z_axis - 2 if z_axis is not None else None # video doesnt count as dim
                self.channel_axis = channel_axis - 2
            # Passing entire 4D video and segmenting slice-by-slice is 
            # not possible --> iterate each frame and run normal segment
            labels = np.zeros(video_data.shape, dtype=np.uint32)
            for i, image in enumerate(video_data):
                lab = self._eval_loop(
                    image, segment_3D_volume=False,
                    isZstack=True,
                    innit_imgs=False,
                    **eval_kwargs
                )
                labels[i] = lab
        else:
            eval_kwargs['channels'] = [eval_kwargs['channels']]*len(video_data)
            if innit_imgs:
                images, z_axis, channel_axis = _initialize_image(video_data, self.is_rgb,
                                            iter_axis_time=0,
                                            timelapse=True,
                                            isZstack=isZstack,
                                            )
                self.z_axis = z_axis - 1 if z_axis is not None else None # video doesnt count as dim
                self.channel_axis = channel_axis - 1
            images = [image.astype(np.float32) for image in images]
            labels = np.array(self._eval(images, **eval_kwargs))

        return labels
    
    def segment3DT(self, video_data, signals=None, **kwargs):
        self.img_shape = video_data[0].shape
        self.img_ndim = len(self.img_shape)

        eval_kwargs, isZstack = self._get_eval_kwargs(video_data[0], **kwargs)

        labels = self._segment3DT_eval(
            video_data, isZstack, eval_kwargs, **kwargs
        )


        self.img_shape = None
        self.img_ndim = None
        return labels        
    
def _initialize_image(image:np.ndarray,
                      is_rgb:bool,
                    #   single_img_shape:Tuple[int],
                    #   single_img_ndim:int,
                      iter_axis_time:int=None,
                      iter_axis_zstack:int=None,
                      target_shape:Tuple[int]=None,
                      timelapse:bool=False,
                      isZstack:bool=False,
                      target_axis_iter:Tuple[int]=None,
                      ):
    """Tries to initialize image for cellpose.
    You will have to specify the target shape and the axis to iterate over.
    Target order of dimensions is (Z x nchan x Y x X) or (T x Z x nchan x Y x X)

    Parameters
    ----------
    image : np.ndarray
        Input image to be initialized. It can be 2D, 3D or 4D.
    is_rgb : bool
        If True, the image is assumed to be RGB.
    img_shape : Tuple[int]
        Shape of the true input image, i.e a single frame's dims.
    img_ndim : int
        Dim of the true input image, i.e a single frame's dims.
    iter_axis_time : int, optional
        axis to be iterated over if iteration over time is needed.
    iter_axis_zstack : int, optional
        axis to be iterated over if iteration over zstack is needed.
    target_shape : Tuple[int], optional
        Shape of the target image, depending if time lapse or not.
    timelapse : bool, optional
        If True, the image is assumed to be a time lapse. Default is False.
    isZstack : bool, optional
        If True, the image is assumed to be a z-stack. Default is False.

    target_axis_iter : Tuple[int], optional
        Output axes along the output should be stacked, by default None

    Returns
    -------
    np.ndarray
        Initialized image, with the shape of the target image.
        The image is normalized to [0, 255] and converted to float32.
        The image is also transposed to the target shape.
    """

    true_img_shape = image.shape
    iter_axis = None

    if timelapse and isZstack:
        if len(true_img_shape) < 4 or (is_rgb and len(true_img_shape) < 5):
            raise TypeError(
                f"Image is {len(true_img_shape)}D with shape {true_img_shape}. "
                "It was expected to have 4D shape (T x Z x Y x X x nchan)"
            )
        
        z_axis = 1
        channel_axis = 2

        target_shape = (true_img_shape[0], true_img_shape[1], 3, true_img_shape[2], true_img_shape[3])


        if iter_axis_time is not None and iter_axis_zstack is not None:
            iter_axis = [iter_axis_time, iter_axis_zstack]
            target_axis_iter = [0, 1]
        elif iter_axis_time  is not None and iter_axis_zstack is None:
            iter_axis = [iter_axis_time]
            target_axis_iter = [0]
        elif iter_axis_time is None and iter_axis_zstack is not None:
            iter_axis = [iter_axis_zstack]
            target_axis_iter = [1]
        else:
            iter_axis = None
            target_axis_iter = None
    
    elif timelapse and not isZstack:
        z_axis = None
        channel_axis = 1
        if len(true_img_shape) < 3 or (is_rgb and len(true_img_shape) < 4):
            raise TypeError(
                f"Image is {len(true_img_shape)}D with shape {true_img_shape}. "
                "It was expected to have 3D shape (T x Y x X x nchan)"
            )
        target_shape = (true_img_shape[0], 3, true_img_shape[1], true_img_shape[2])

        if iter_axis_time is not None:
            iter_axis = [iter_axis_time]
            target_axis_iter = [0]
        else:
            iter_axis = None
            target_axis_iter = None
    
    elif not timelapse and isZstack:
        z_axis = 0
        channel_axis = 1
        if len(true_img_shape) < 3 or (is_rgb and len(true_img_shape) < 4):
            raise TypeError(
                f"Image is {len(true_img_shape)}D with shape {true_img_shape}. "
                "It was expected to have 3D shape (Z x Y x X x nchan)"
            )
        target_shape = (true_img_shape[0], 3, true_img_shape[1], true_img_shape[2])
        if iter_axis_zstack is not None:
            iter_axis = [iter_axis_zstack]
            target_axis_iter = [0]
        else:
            iter_axis = None
            target_axis_iter = None
    
    elif not timelapse and not isZstack:
        z_axis = None
        channel_axis = 0

        if len(true_img_shape) < 2 or (is_rgb and len(true_img_shape) < 3):
            raise TypeError(
                f"Image is {len(true_img_shape)}D with shape {true_img_shape}. "
                "It was expected to have 2D shape (Y x X x nchan)"
            )
        target_shape = (3, true_img_shape[0], true_img_shape[1])

    if iter_axis is not None:
        # Build an index tuple: set first iter_axis to 0, others to slice(None)
        idx = [0 if i in iter_axis else slice(None) for i in range(len(true_img_shape))]
        single_img_from_iter_axis = image[tuple(idx)]
    else:
        single_img_from_iter_axis = image
    if single_img_from_iter_axis is not None:
        single_img_shape = single_img_from_iter_axis.shape
        single_img_ndim = len(single_img_shape)
    else:
        single_img_shape = true_img_shape
        single_img_ndim = len(single_img_shape)
    
    single_img_isZstack = isZstack if iter_axis_zstack is None else False
    
    from cellacdc._core import _initialize_single_image
    image = core.apply_func_to_imgs(
        image,
        _initialize_single_image,
        iter_axis=iter_axis,
        target_type=np.float32,
        target_shape=target_shape,
        target_axis_iter=target_axis_iter,
        is_rgb=is_rgb,
        isZstack=single_img_isZstack,
        img_shape=single_img_shape,
        img_ndim=single_img_ndim,
    )
    return image, z_axis, channel_axis

def url_help():
    return 'https://cellpose.readthedocs.io/en/latest/api.html'
