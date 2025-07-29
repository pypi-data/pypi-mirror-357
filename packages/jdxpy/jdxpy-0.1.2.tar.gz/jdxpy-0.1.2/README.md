# JDxPy

[![PyPI version](https://badge.fury.io/py/jdxpy.svg)](https://badge.fury.io/py/jdxpy)
[![Python Support](https://img.shields.io/pypi/pyversions/jdxpy.svg)](https://pypi.org/project/jdxpy/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Python library for development experience enhancement - 開発体験を向上させるPythonライブラリ

**注意**: このプロジェクトは現在初期開発段階のため、CI/CDパイプラインは無効化されています。プロジェクトが成熟した際に有効化されます。

## 概要

JDxPyは開発者の生産性と開発体験を向上させることを目的としたPythonライブラリです。

日常的な開発作業を効率化し、コードの品質を向上させるためのツールを提供します。

## 特徴

- **高パフォーマンス**: 効率的なアルゴリズムと最適化された実装
- **セキュリティ重視**: セキュリティベストプラクティスを考慮した設計
- **多機能**: 様々な開発シーンで使用可能な豊富な機能
- **豊富なドキュメント**: 詳細なドキュメントと使用例
- **テスト済み**: 高いテストカバレッジ
- **Python 3.11+**: Python3.11以上をサポート

## インストール

### PyPIからインストール

```bash
pip install jdxpy
```

### 開発版のインストール

```bash
git clone https://github.com/sugarperson-net/jdxpy.git
cd jdxpy
pip install -e .
```

### 開発環境のセットアップ

```bash
git clone https://github.com/sugarperson-net/jdxpy.git
cd jdxpy
pip install -e ".[dev]"
pre-commit install
```

## 使用方法

### 基本的な使用例

```python
import jdxpy

# 基本的な機能の使用
result = jdxpy.hello_jdxpy()
print(result)  # Hello from JDxPy!
```

### より詳細な使用例

```python
from jdxpy.core import hello_jdxpy

# コア機能の直接インポート
message = hello_jdxpy()
print(f"JDxPy says: {message}")
```

## ドキュメント

### はじめる
- **[クイックスタートガイド](docs/このプロジェクトについて/クイックスタート.md)** - 新規参加者向け5分セットアップ
- **[プロジェクト構造ガイド](docs/このプロジェクトについて/プロジェクト構成.md)** - ディレクトリ構造の詳細説明
- **[運用手順書](docs/このプロジェクトについて/運用手順.md)** - 開発からリリースまでの完全手順

### 技術資料
- **[Issue対応マニュアル](docs/このプロジェクトについて/ISSUE対応マニュアル.md)** - GitHub Issues管理と対応手順
- **[リリースノート運用ガイド](docs/このプロジェクトについて/リリースノート運用ガイド.md)** - リリースノート作成・管理手順
- **[CI/CDセットアップガイド](docs/このプロジェクトについて/GiHubActionsセットアップガイド.md)** - GitHub Actions設定方法（現在無効化）
- [CHANGELOG.md](CHANGELOG.md) - バージョン履歴
- [LICENSE](LICENSE) - Apache 2.0ライセンス

## API リファレンス

### 現在利用可能な機能

#### `hello_jdxpy() -> str`

基本的な例示関数です。

**戻り値:**
- `str`: 実行結果のメッセージ

**使用例:**
```python
from jdxpy import hello_jdxpy

result = hello_jdxpy()
print(result)  # "Hello from JDxPy!"
```

## 開発

### 要件

- Python 3.11以上
- pip またはpipenv/poetry

### セットアップ

```bash
# リポジトリのクローン
git clone https://github.com/sugarperson-net/jdxpy.git
cd jdxpy

# 開発依存関係のインストール
pip install -e ".[dev]"

# pre-commitフックの設定
pre-commit install
```

### テストの実行

```bash
# 全テストの実行
pytest

# カバレッジ付きテストの実行
pytest --cov=jdxpy

# 特定のテストファイルの実行
pytest tests/test_core.py
```

### コード品質チェック

```bash
# コードフォーマット
black src/ tests/

# リンティング
flake8 src/ tests/

# タイプチェック
mypy src/
```

### 利用可能なMakeタスク

```bash
# 全テストとリンティングの実行
make test

# フォーマットの実行
make format

# リンティングの実行
make lint

# ビルドの実行
make build

# クリーンアップ
make clean
```

## 貢献

プロジェクトへの貢献を歓迎します！以下の手順に従ってください：

1. リポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

### 貢献ガイドライン

- コードスタイルはBlackとFlake8に従ってください
- テストを追加して機能をカバーしてください
- ドキュメントを更新してください
- セキュリティベストプラクティスを遵守してください

## ライセンス

このプロジェクトはApache License 2.0の下でライセンスされています。
詳細は [LICENSE](LICENSE) ファイルをご覧ください。

## サポート

- **バグ報告**: [GitHub Issues](https://github.com/sugarperson-net/jdxpy/issues)
- **機能要望**: [GitHub Issues](https://github.com/sugarperson-net/jdxpy/issues)
- **メール**: jdxpy-developers@sugarperson.net

## 変更履歴

最新の変更については [CHANGELOG.md](CHANGELOG.md) をご覧ください。

## 謝辞

このプロジェクトは以下のオープンソースプロジェクトに支えられています：

- [Python](https://python.org/)
- [PyPI](https://pypi.org/)
- その他の依存関係（pyproject.tomlを参照）

---

JDxPy Team ©2025
