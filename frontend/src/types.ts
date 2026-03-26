export interface Detection {
    id: string;
    camera_id: string;
    detected_at: string;
    vehicle_class: string;
    confidence: number;
    bbox: number[];
    image_url?: string;
}

export interface CameraStats {
    camera_id: string;
    name?: string;
    lat: number;
    lon: number;
    total_detections: number;
    last_seen: string | null;
    image_url?: string;
    rsu_id?: string;
    vehicle_count_30s: number;
}
