# Mapiry

[![PyPI version](https://badge.fury.io/py/mapiry.svg)](https://badge.fury.io/py/mapiry)
[![Python versions](https://img.shields.io/pypi/pyversions/mapiry)](https://pypi.org/project/mapiry/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Mapiry** は Mapillary API v4 の全機能を網羅した、使いやすい Python SDK です。ストリートレベル画像、シーケンス、オブジェクト検出、ベクタータイルなど、Mapillary の豊富なデータにアクセスできます。

## 🚀 特徴

- **完全な API カバレッジ**: Mapillary API v4 の全エンドポイントをサポート
- **直感的なインターフェース**: メソッドチェーンによる使いやすい API 設計
- **型安全**: Python の型ヒントとデータクラスを使用
- **自動エラーハンドリング**: リトライ機能付きの堅牢なエラー処理
- **豊富なサンプル**: 実用的なコード例を多数提供

## 📦 インストール

```bash
pip install mapiry
```

## 🔑 API キーの取得

1. [Mapillary Developer Dashboard](https://www.mapillary.com/dashboard/developers) でアカウントを作成
2. 新しいアプリケーションを登録
3. アクセストークンを生成

## 🏁 クイックスタート

```python
from mapiry import MapillaryClient

# API キーを設定
client = MapillaryClient(api_key="YOUR_API_KEY")

# 指定座標周辺の画像を取得
images = client.images().close_to(
    longitude=139.7673068,  # 東京駅
    latitude=35.6809591,
    radius=100
).limit(10).get()

print(f"見つかった画像: {len(images.data)}枚")
for image in images.data:
    print(f"- {image.id}: {image.captured_at}")
```

## 📚 主要機能

### 🖼️ 画像検索

```python
# 座標周辺の画像
images = client.images().close_to(longitude=139.76, latitude=35.68, radius=500).get()

# 境界矩形内の画像
images = client.images().in_bbox(
    west=139.75, south=35.67, east=139.77, north=35.69
).get()

# パノラマ画像のみ
images = client.images().panoramic_only().get()

# 日付範囲でフィルタ
images = client.images().captured_between("2023-01-01", "2023-12-31").get()

# カメラメーカーとユーザー名でフィルタ
images = client.images().camera_make("Apple").by_usernames("user1", "user2").get()

# 特定の方向を向いている画像
images = client.images().lookat(longitude=139.77, latitude=35.69).get()

# プライベート画像のみ
images = client.images().private_images().get()

# ページング設定
images = client.images().per_page(500).get()
```

### 🛣️ シーケンス操作

```python
# 座標周辺のシーケンス
sequences = client.sequences().close_to(longitude=139.76, latitude=35.68).get()

# 最小画像数でフィルタ
sequences = client.sequences().min_images(20).get()

# シーケンスの画像を取得
images = client.sequences().get_images(sequence_id="sequence_123")
```

### 🗺️ マップ機能

```python
# ベンチの検索
benches = client.map_features().benches().in_bbox(
    west=139.75, south=35.67, east=139.77, north=35.69
).min_confidence(0.8).get()

# 複数のオブジェクトタイプ
features = client.map_features().object_values(
    "object--bench", "object--fire-hydrant", "object--trash-can"
).close_to(longitude=139.76, latitude=35.68, radius=500).get()

# 特定の日付範囲
features = client.map_features().first_seen_after("2023-01-01").get()
```

### 🚦 オブジェクト検出

```python
# 交通標識の検出
signs = client.detections().traffic_signs().close_to(
    longitude=139.76, latitude=35.68, radius=1000
).min_confidence(0.8).get()

# 特定の標識タイプ
stop_signs = client.detections().object_value("stop").get()

# 信頼度でフィルタ
high_conf = client.detections().min_confidence(0.9).get()
```

### 🗺️ ベクタータイル

```python
# 画像タイルを取得
tile_data = client.vector_tiles().get_image_tiles(z=14, x=4823, y=6160)

# カバレッジタイル
coverage_tile = client.vector_tiles().get_coverage_tiles(z=14, x=4823, y=6160)

# マップ機能ポイントタイル
feature_tile = client.vector_tiles().get_map_feature_point_tiles(z=14, x=4823, y=6160)

# 交通標識タイル
traffic_tile = client.vector_tiles().get_map_feature_traffic_sign_tiles(z=14, x=4823, y=6160)

# タイル境界を取得
bounds = client.vector_tiles().get_tile_bounds(z=14, x=4823, y=6160)
```

### 🏢 組織データ

```python
# 組織情報を取得
org = client.organizations().get_by_id("org_id")

# 組織の画像を取得
org_images = client.organizations().get_organization_images("org_id")

# 組織の統計情報
stats = client.organizations().get_organization_stats("org_id")
```

## 🔗 メソッドチェーン

Mapiry は流暢なインターフェースをサポートしています：

```python
result = (client.images()
          .in_bbox(west=-74.01, south=40.74, east=-73.98, north=40.76)
          .image_type("pano")
          .captured_after("2023-01-01")
          .by_usernames("photographer1", "photographer2")
          .lookat(longitude=-74.00, latitude=40.75)
          .public_images()
          .min_confidence(0.8)
          .fields("id", "captured_at", "compass_angle")
          .per_page(50)
          .get())
```

## 📊 データモデル

すべてのレスポンスは構造化されたデータクラスとして返されます：

```python
# 画像オブジェクト
image = images.data[0]
print(image.id)              # 画像ID
print(image.captured_at)     # 撮影日時
print(image.compass_angle)   # コンパス角度
print(image.is_pano)         # パノラマ画像かどうか
print(image.camera_make)     # カメラメーカー
print(image.geometry)        # 位置情報

# 検出オブジェクト
detection = detections.data[0]
print(detection.object_type)   # オブジェクトタイプ
print(detection.object_value)  # オブジェクト値
print(detection.confidence)    # 信頼度
```

## 🎯 実用例

### 交通標識マッピング

```python
# 特定エリアの交通標識をマッピング
signs = client.detections().traffic_signs().in_bbox(
    west=-73.99, south=40.75, east=-73.97, north=40.76
).min_confidence(0.7).get()

# 標識タイプ別集計
from collections import defaultdict
sign_counts = defaultdict(int)
for sign in signs.data:
    sign_counts[sign.object_value] += 1

for sign_type, count in sign_counts.items():
    print(f"{sign_type}: {count}個")
```

### 画像ダウンロード

```python
# 画像のサムネイルをダウンロード
images = client.images().close_to(longitude=139.76, latitude=35.68).limit(5).get()

for image in images.data:
    # 1024px のサムネイルをダウンロード
    image_data = client.images().download_image(image.id, size="thumb_1024_url")
    
    with open(f"image_{image.id}.jpg", "wb") as f:
        f.write(image_data)
```

## ⚙️ 設定オプション

```python
# カスタム設定でクライアントを初期化
client = MapillaryClient(
    api_key="your_api_key",
    timeout=60,           # リクエストタイムアウト（秒）
    max_retries=5,        # 最大リトライ回数
    retry_backoff=2.0     # リトライ間隔係数
)

# コンテキストマネージャーとして使用
with MapillaryClient(api_key="your_api_key") as client:
    images = client.images().close_to(longitude=139.76, latitude=35.68).get()
```

## 🚫 エラーハンドリング

```python
from mapiry.exceptions import AuthenticationError, RateLimitError, APIError

try:
    images = client.images().close_to(longitude=139.76, latitude=35.68).get()
except AuthenticationError:
    print("API キーが無効です")
except RateLimitError:
    print("レート制限に達しました")
except APIError as e:
    print(f"API エラー: {e.message}")
```

## 📝 利用可能なフィールド

### 画像フィールド
- `id`, `geometry`, `camera_make`, `camera_model`
- `captured_at`, `compass_angle`, `sequence_id`
- `organization_id`, `creator_id`, `creator_username`
- `is_pano`, `thumb_256_url`, `thumb_1024_url`, `thumb_2048_url`
- `width`, `height`, `exif_orientation`

### シーケンスフィールド
- `id`, `geometry`, `created_at`, `captured_at`
- `organization_id`, `creator_id`, `creator_username`
- `camera_make`, `camera_model`, `image_count`

### 検出フィールド
- `id`, `geometry`, `image_id`, `sequence_id`
- `object_type`, `object_value`, `confidence`
- `created_at`, `first_seen_at`, `last_seen_at`

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルをご覧ください。

## 🔗 関連リンク

- [Mapillary API ドキュメント](https://www.mapillary.com/developer/api-documentation/)
- [Mapillary Developer Dashboard](https://www.mapillary.com/dashboard/developers)
- [GitHub リポジトリ](https://github.com/tikipiya/Mapiry)
- [PyPI パッケージ](https://pypi.org/project/mapiry/)

## 📧 サポート

質問やサポートが必要な場合は、[GitHub Issues](https://github.com/tikipiya/Mapiry/issues) でお気軽にお問い合わせください。

---

Made by [tikisan](https://github.com/tikipiya)