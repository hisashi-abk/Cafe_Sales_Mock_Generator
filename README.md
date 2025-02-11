# Cafe Sales Mock Data Generator

このプロジェクトは、カフェの売上データのモックを生成するPythonスクリプトです。営業時間、天候、時間帯別の客数変動などの要素を考慮して、テストやデモ用のデータセットを簡単に作成することができます。

## 注意事項

### データの利用について

- このスクリプトが生成するデータは**モックデータ**であり、実際のビジネスデータを反映したものではありません
- 生成されるデータはテストやデモンストレーション目的にのみ使用してください
- 実際のビジネス分析や意思決定には使用しないでください

### セキュリティに関する注意

- 生成されたモックデータを本番環境で使用しないでください
- テストデータであっても、セキュアな場所に保存し、適切なアクセス制御を行ってください
- データファイルをバージョン管理システムにコミットする際は、機密情報が含まれていないことを確認してください

## 特徴

- 時間帯別（モーニング、ランチ、ティータイム、レギュラー）の客数設定
- 天候による来客数の変動
- セットメニュー価格の自動計算
- 豊富なメニューアイテム（ドリンク、サンドイッチ、ケーキ）
- テイクアウト注文の対応
- 複数フォーマット（JSON, CSV, Excel）でのデータ出力
- 生成するデータの年月を設定可能

## 必要要件

- Python 3.8以上
- 必要なパッケージは`requirements.txt`に記載

```bash
pip install -r requirements.txt
```

## インストール方法

```bash
git clone https://github.com/hisashi-abk/Cafe_Sales_Mock_Generator.git
cd Cafe_Sales_Mock_Generator
pip install -r requirements.txt
```

## 使用方法

1. 設定ファイルの準備
   - `config.yaml`をカスタマイズして、メニュー、価格、営業時間などを設定できます
   - デフォルトの設定をそのまま使用することも可能です

2. スクリプトの実行

   ```bash
   # デフォルト設定で実行
   python cafe_sales_mock_generator.py

   # 異なる設定ファイルを使用
   python cafe_sales_mock_generator.py --config custom_config.yaml
   ```

## 出力ファイル

生成されるファイルは以下の通りです：

- `master_data_YYYY-MM.json`: マスターデータ（メニュー、カテゴリなど）
- `orders_YYYY-MM.json`: 注文データ
- `order_items_YYYY-MM.json`: 注文詳細データ
- `cafe_data_YYYY_MM.xlsx`: 基本的な売上データ（Excel形式）
- `cafe_comprehensive_data_YYYY_MM.xlsx`: 詳細な売上データ（Excel形式）
- `orders_YYYY_MM.csv`: CSV形式の売上データ

## エンコーディングに関する注意点

### Windows環境での利用

- 生成されるファイルは UTF-8 でエンコードされます
- Windows環境でCSVファイルをExcelで開く場合、文字化けを防ぐため以下のいずれかの方法を使用してください：
  1. テキストエディタで開いてBOM付きUTF-8で保存し直す
  2. Excelでファイルを開く際に、データ取り込みウィザードでエンコーディングをUTF-8に指定する

## 設定カスタマイズ

`config.yaml`で以下の項目を調整できます：

### 基本設定

- `generate_period`: データを生成する年月
  - `year`: 生成する年（例：2024）
  - `month`: 生成する月（1-12）

### ビジネスルール設定

- `business_hours`: 営業時間の設定
- `max_daily_customers`: 1日の最大客数
- `weather_factors`: 天候による影響度
- `time_slots`: 時間帯ごとの設定
  - 営業時間
  - 客数範囲
  - セット価格

### メニュー設定

- `categories`: メニューカテゴリの定義
- `menu_items`: 各カテゴリの商品定義
  - 商品名
  - 価格
  - カテゴリID

### 出力データのカスタマイズ

スクリプトを修正することで、以下のようなカスタマイズが可能です：

- 新しい商品カテゴリの追加
- 注文パターンの変更
- 異なる時間帯の設定
- 追加の分析データの生成

## データ構造

### 注文データ（orders）

- `id`: 注文ID
- `timestamp`: 注文日時
- `gender_id`: 性別ID
- `order_type_id`: 注文タイプ（店内/テイクアウト）
- `weather_id`: 天候ID
- `time_slot_id`: 時間帯ID
- `total_price`: 合計金額
- `discount`: 割引額

### 注文詳細（order_items）

- `id`: 注文詳細ID
- `order_id`: 注文ID
- `menu_item_id`: メニューアイテムID
- `price`: 価格

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細については[LICENSE](LICENSE)ファイルを参照してください。

## コントリビューション

バグ報告や機能改善の提案は、GitHubのIssueやPull Requestsを通じて受け付けています。大きな変更を行う場合は、まずissueを作成して変更内容を議論してください。

## 作者

hisashi-abk
