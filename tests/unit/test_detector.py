from unittest.mock import patch, MagicMock
from src.worker.detector import detect_vehicles


def make_mock_box(cls_id: int, conf: float):
    box = MagicMock()
    box.cls = [cls_id]
    box.conf = [conf]
    box.xyxy = [MagicMock(tolist=lambda: [10, 20, 50, 80])]
    return box


@patch("src.worker.detector.model")
def test_detect_vehicles_returns_cars(mock_model):
    mock_result = MagicMock()
    mock_result.boxes = [make_mock_box(cls_id=2, conf=0.91)]
    mock_model.predict.return_value = [mock_result]
    mock_model.names = {2: "car"}
    valid_gif = b"GIF89a\x01\x00\x01\x00\x00\xff\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;"
    detections = detect_vehicles(valid_gif)

    assert len(detections) == 1
    assert detections[0]["class"] == "car"
    assert detections[0]["confidence"] == 0.91
