# Claude++ System 使い方ガイド

## 🚀 インストールと初回セットアップ

### 1. インストール

```bash
# プロジェクトディレクトリで実行
./install.sh
```

### 2. 環境変数の設定

```bash
# シェルを再起動、または以下を実行
source ~/.bashrc    # Bashの場合
source ~/.zshrc     # Zshの場合
```

### 3. 動作確認

```bash
# ヘルプを表示
claude-plus --claude-plus-help

# 任意のディレクトリで使用可能
cd /path/to/your/project
claude-plus
```

## 💡 基本的な使い方

### 対話モード（推奨）

```bash
$ claude-plus
🇯🇵 Claude++ へようこそ！
> main.pyのバグを修正して
```

### バッチモード

```bash
echo "テストを作成して" | claude-plus
```

## ✨ 主な機能

### 🛡️ 自動保護システム
- **30分自動保存**: 作業内容を自動的にGitに保存
- **緊急保護**: エラー時の自動バックアップ
- **透明Git**: Gitを意識せずに安全な作業

### 🇯🇵 日本語UI
- **完全日本語化**: すべてのメッセージが自然な日本語
- **エラー翻訳**: 英語エラーを分かりやすく翻訳
- **初心者フレンドリー**: 技術用語を避けた表現

### 📊 画面分割モード（tmux利用時）
```
╔════════════ Claude Code (70%) ════════════╗
║ 実際のClaude Codeの動作                    ║
╠════════ Claude++ Panel (30%) ════════╣
║ 🇯🇵 日本語コントロールパネル               ║
║ 💾 自動保存: 25分後                        ║
║ 🌿 ブランチ: feature/new-function          ║
╚════════════════════════════════════════════╝
```

## 🎯 使用例

### ファイル編集
```bash
> main.pyのバグを修正して
🔧 バグ修正中...
✅ calculate関数の演算子を修正しました
```

### テスト作成
```bash
> テストを作成して
🧪 テストコード生成中...
✅ test_main.py を作成しました
```

### ドキュメント更新
```bash
> READMEを更新して
📄 ドキュメント更新中...
✅ プロジェクトの説明を追加しました
```

## ⚙️ 設定

設定ファイル: `~/.claude-plus/config.yaml`

```yaml
# 主要設定
transparent_git:
  auto_save_interval: 30    # 自動保存間隔（分）

notifications:
  sound: true              # 音声通知
  visual: true             # 視覚通知
  verbosity: verbose       # 詳細度

auto_protection:
  protection_level: HIGH   # 保護レベル
```

## 🔧 オプション

```bash
# ヘルプ表示
claude-plus --claude-plus-help

# デバッグモード
claude-plus --claude-plus-debug

# 通知無効
claude-plus --claude-plus-no-notifications

# 自動Yes無効
claude-plus --claude-plus-no-auto-yes

# 設定ファイル指定
claude-plus --claude-plus-config /path/to/config.yaml
```

## 🆘 トラブルシューティング

### よくある問題

1. **コマンドが見つからない**
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

2. **モジュールエラー**
   ```bash
   export CLAUDE_PLUS_HOME="/path/to/claude-plus"
   ```

3. **tmuxが無い**
   ```bash
   brew install tmux  # macOS
   sudo apt install tmux  # Ubuntu
   ```

### ログ確認
```bash
tail -f /tmp/claude-plus.log
```

## 🎉 始めましょう！

```bash
# 今すぐ開始
claude-plus
```

すべての技術的な複雑さは Claude++ が自動処理します。
あなたはコーディングに集中するだけです！ 🚀