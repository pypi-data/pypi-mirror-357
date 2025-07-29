"""ffmpeg_webcam_frame_reader - module for ffmopeg-based webcam functionality"""
from io import IOBase
import numpy as np
from .frame_reader import FrameReader

class FdFrameReader(FrameReader):
    """Implements FrameReader using ffmpeg for webcams from /dev/videoX"""
    def __init__(self, data: IOBase, resolution: tuple[int, int]=(360, 1280), fps: int=30):
        assert isinstance(data, IOBase), type(data)
        super().__init__()
        self.data = data
        self._fps = fps
        self.resolution = (self.height, self.width) = resolution

    @property
    def shape(self) -> tuple[int, int, int, int]:
        return (1, self.height, self.width, 3)

    @property
    def fps(self):
        return self._fps

    @property
    def path(self) -> str:
        return str(self.data)

    def __getitem__(self, ix: int | list[int] | np.ndarray | slice) -> np.ndarray:
        if isinstance(ix, slice):
            assert (ix.start - ix.stop) == 1, f"cannot have batches in webcam, got: {list(ix)}"
            ix = [0]
        raw_frame = self.data.read(self.width * self.height * 3)
        if not raw_frame:
            raise StopIteration
        frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((self.height, self.width, 3))
        if isinstance(ix, (list, np.ndarray)):
            assert len(ix) == 1, f"cannot have batches in webcam, got: {ix}"
            frame = frame[None] # return a batch of one for other tools
        return frame
