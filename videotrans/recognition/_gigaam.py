# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import List, Union
import torch

from videotrans.configure.config import logger
from videotrans.recognition._base import BaseRecogn
from videotrans.task.taskcfg import SrtItem

_GIGAAM_MODEL_INSTANCE = None


@dataclass(repr=False)
class GigaamRecogn(BaseRecogn):
    """
    Sber GigaAM Speech Recognition Channel (SOTA for Russian speech).
    """

    def _exec(self) -> Union[List[SrtItem], None]:
        global _GIGAAM_MODEL_INSTANCE
        if self._exit():
            return None

        import gigaam

        if _GIGAAM_MODEL_INSTANCE is None:
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
            logger.info(f"Loading Sber GigaAM model on device: {device}")
            _GIGAAM_MODEL_INSTANCE = gigaam.load_model("v2_ctc", device=device)

        raws = self.cut_audio()
        if not raws:
            return []

        for i, it in enumerate(raws):
            if self._exit():
                return None
            try:
                text = _GIGAAM_MODEL_INSTANCE.transcribe(it["filename"]).strip()
                it["text"] = text
                self.signal(text=f"{i+1}/{len(raws)}")
                if text:
                    self.signal(text=f"{text}\n", type="subtitle")
            except Exception as e:
                logger.error(f"GigaAM chunk error: {e}")
                it["text"] = ""

        return raws
