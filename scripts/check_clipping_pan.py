import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import tarfile, json

pan_tar = 'c:/OCR - All/kaggle_cloud_pipeline/latest_cloud_output/shards/pan/pan_train_00000.tar'
clipping_samples = []
with tarfile.open(pan_tar, 'r') as tar:
    for m in tar.getmembers():
        if m.name.endswith('.json'):
            f = tar.extractfile(m)
            data = json.load(f)
            cw, ch = data.get('canvas_size', [0, 0])
            for t in data.get('tokens', []):
                bb = t.get('bbox', [0, 0, 0, 0])
                if len(bb) == 4:
                    x1, y1, x2, y2 = bb
                    if x2 > cw or y2 > ch or x1 < 0 or y1 < 0:
                        clipping_samples.append({
                            'sample': m.name,
                            'tier': data.get('tier'),
                            'canvas': (cw, ch),
                            'token': t.get('text'),
                            'bbox': bb,
                            'diff_x': max(0, x2 - cw),
                            'diff_y': max(0, y2 - ch)
                        })

print(f"Total clipping tokens found in Punjabi shard 0: {len(clipping_samples)}")
for cs in clipping_samples[:10]:
    print(f"Sample: {cs['sample']} ({cs['tier']}) | Canvas: {cs['canvas']} | Token: '{cs['token']}' | BBox: {cs['bbox']} | Diff: dx={cs['diff_x']}, dy={cs['diff_y']}")
