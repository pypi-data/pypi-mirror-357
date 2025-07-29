# Claude++ ワンコマンドインストール詳細ガイド

## 🎯 概要

Claude++は、真のワンコマンドインストールを実現しました。Python環境の問題を完全に解決し、初心者でも確実にインストールできます。

## 🚀 基本的な使用方法

```bash
curl -fsSL https://simeji03.github.io/Claude-Plus/install.sh | bash
```

## ⚙️ 内部動作詳細

### 自動検出・自動インストール

**OS検出**:
- macOS (Darwin)
- Linux (Ubuntu, CentOS, Fedora, Arch等)
- Windows WSL

**パッケージマネージャー検出**:
- Homebrew (macOS)
- apt (Ubuntu/Debian)
- yum/dnf (CentOS/Fedora)
- pacman (Arch Linux)

**Python 3.10+インストール方式**:
1. **既存確認**: 既にPython 3.10+があればスキップ
2. **パッケージマネージャー**: brew, apt等での自動インストール
3. **公式インストーラー**: macOSの場合、python.orgから直接
4. **pyenv**: 上記が利用できない場合のフォールバック

**tmuxインストール**:
- 各パッケージマネージャーを使用して自動インストール
- 既にインストール済みの場合はスキップ

**Claude++インストール**:
- PyPIから最新版を`pip install --user claude-plus`
- インストール後の動作確認を自動実行

## 🔧 技術的詳細

### エラーハンドリング

```bash
set -euo pipefail  # 厳格なエラーハンドリング
trap 'print_error; exit 1' ERR  # エラー時の自動クリーンアップ
```

### セキュリティ機能

- **HTTPS必須**: SSL/TLS暗号化での配信
- **構文チェック**: 実行前のスクリプト検証
- **段階的確認**: 各ステップでの動作確認
- **ロールバック**: エラー時の自動復旧

### 環境設定

**PATHの自動設定**:
```bash
# ~/.bashrc / ~/.zshrc への自動追加
export PATH="$HOME/.local/bin:$PATH"
```

**設定ディレクトリ**:
- インストール: `~/.local/bin/`
- 設定: `~/.claude-plus/`

## ⚠️ 制約・注意事項

### 技術的制約

**URL長い**:
- `https://simeji03.github.io/Claude-Plus/install.sh`
- 覚えにくいがコピペで問題なし

**反映タイムラグ**:
- GitHub Pagesの更新: 数分のタイムラグ
- キャッシュクリア推奨: `curl -H "Cache-Control: no-cache"`

**GitHub依存**:
- GitHubサービス停止時はアクセス不可
- 99.9%の稼働率（GitHub実績）

### 対応OS制限

**サポート対象**:
- ✅ macOS 10.14以降
- ✅ Ubuntu 18.04以降
- ✅ CentOS 7以降
- ✅ Fedora 30以降
- ✅ Arch Linux
- ✅ Windows WSL (Ubuntu/Debian)

**非対応**:
- ❌ Windows (native)
- ❌ 非常に古いLinuxディストリビューション

### 権限要件

**sudo権限が必要な場合**:
- システムのPython/tmuxインストール時
- パッケージマネージャーの使用時

**権限不要な場合**:
- pyenvを使用したPython管理
- ユーザーディレクトリへのインストール

## 🔄 更新・メンテナンス

### スクリプト更新

**更新方法**:
1. GitHubリポジトリでinstall.shを更新
2. GitHub Pagesが自動で反映（数分）
3. ユーザーは常に最新版を取得

**バージョン管理**:
- ファイル内でバージョン情報管理
- 更新履歴はGitコミットログで追跡

### Claude++本体更新

**自動取得**:
- スクリプト実行時にPyPIから最新版を取得
- `pip install --upgrade claude-plus`で手動更新も可能

## 🔍 トラブルシューティング

### よくある問題

**1. 権限エラー**
```bash
# 解決方法
sudo chown -R $USER ~/.local
```

**2. Python環境競合**
```bash
# 解決方法: pyenvを優先
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
```

**3. ネットワークエラー**
```bash
# キャッシュクリアしてリトライ
curl -H "Cache-Control: no-cache" -fsSL https://simeji03.github.io/Claude-Plus/install.sh | bash
```

### ログとデバッグ

**詳細ログ有効化**:
```bash
# デバッグモードで実行
CLAUDE_PLUS_DEBUG=1 curl -fsSL ... | bash
```

**手動デバッグ**:
```bash
# スクリプトダウンロード後に手動実行
curl -fsSL https://simeji03.github.io/Claude-Plus/install.sh > install.sh
bash -x install.sh  # 詳細ログ付き実行
```

## 📊 使用統計（将来実装予定）

**収集予定データ**:
- OS/ディストリビューション分布
- インストール成功率
- エラーパターン分析

**プライバシー**:
- 個人情報は一切収集しません
- 統計データのみ（匿名化）

## 🎯 将来計画

### 短期改善（1-3ヶ月）

- **CDN配信**: 高速化・安定性向上
- **カスタムドメイン**: `install.claude-plus.dev` 等
- **エラー統計**: 自動分析・改善

### 長期ビジョン（6ヶ月以上）

- **パッケージマネージャー登録**: apt, yum等への正式登録
- **Homebrew Formula**: 公式tap作成
- **Docker Image**: コンテナ対応

---

**最終更新**: 2025年6月22日  
**対象バージョン**: Claude++ 2.9.2以降