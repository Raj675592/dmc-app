import os
import pickle
import tempfile
import numpy as np
from PIL import Image


def load_model():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    import torch
    from ultralytics import YOLO

    _original_torch_load = torch.load

    def _patched_torch_load(*args, **kwargs):
        kwargs["weights_only"] = False
        kwargs.setdefault("map_location", "cpu")
        return _original_torch_load(*args, **kwargs)

    torch.load = _patched_torch_load

    model_path = os.path.join(script_dir, "model.pkl")

    with open(model_path, "rb") as f:
        payload = pickle.load(f)

    tmp = tempfile.NamedTemporaryFile(suffix=".pt", delete=False)
    tmp.write(payload["weights_bytes"])
    tmp.flush()
    tmp.close()

    my_model = YOLO(tmp.name)
    my_model.to("cpu")

    if hasattr(my_model, "model") and my_model.model is not None:
        my_model.model = my_model.model.cpu()
        my_model.model.float()

    torch.load = _original_torch_load

    os.unlink(tmp.name)

    return my_model


def predict(model, image_path):

    img = Image.open(image_path).convert("RGB")
    img = img.resize((512, 512))

    tmp_img = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img.save(tmp_img.name)
    tmp_img.close()

    results = model(
        tmp_img.name,
        imgsz   = 512,
        conf    = 0.2,
        device  = "cpu",
        verbose = False,
    )

    dustbin_present = False
    spill_detected  = False

    for r in results:
        if r.boxes is not None:
            for box in r.boxes:
                class_id = int(box.cls[0])

                if class_id == 0:
                    dustbin_present = True

                if class_id == 1:
                    spill_detected = True

    prediction = 1 if (dustbin_present and spill_detected) else 0

    os.unlink(tmp_img.name)
    return int(prediction)