# 🎯 Claude-Plus 超かんたんセットアップ

## 💡 たった10分で完了！

> **大丈夫です！** 順番にやれば必ずできます 🌟

---

## 🚀 3ステップで完了

### ✅ **ステップ1: 基本ツールを入れる（5分）**

> **ターミナルを開く**: Command + スペース → 「Terminal」と入力 → Enter

**3行コピペするだけ！**
```bash
# Homebrew をインストール
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 必要なツールを一括インストール  
brew install python tmux node

# Claude CLI をインストール
npm install -g @anthropic-ai/claude-cli
```

**✅ 成功すると**: `Successfully installed` と表示されます

### ✅ **ステップ2: Claude とつなげる（3分）**

1. **[ここをクリック](https://console.anthropic.com/)** → 「Sign up」でアカウント作成
2. **「API Keys」** → 「Create Key」→ **キーをコピー** 📋
3. **ターミナルで**:
```bash
claude login
# ↑ さっきコピーしたキーを貼り付けてEnter
```

**✅ 成功すると**: `Successfully authenticated!` と表示されます

### ✅ **ステップ3: Claude-Plus をインストール（1分）**

```bash
pip install claude-plus
```

**✅ 成功すると**: `Successfully installed claude-plus` と表示されます

---

## 🎉 完成！使ってみよう

```bash
claude-plus
```

**この画面が出たら成功！**
```
╔══════════════════════════════════════════╗
║         Claude++ System 起動中...        ║
╚══════════════════════════════════════════╝
```

**試しに話しかけてみて:**
```
> じゃんけんゲームを作って
> 勝敗をカウントして
> テストも作って  
> 実行してみて
```

**自然な日本語で話すだけで、プロ級のプログラムができあがります！** ✨

---

## 🆘 困った時（クリックして開く）

<details>
<summary><strong>📱 Windows を使っている</strong></summary>

**Windows の場合:**
1. [Python.org](https://www.python.org/downloads/) から Python をダウンロード
2. [Git for Windows](https://gitforwindows.org/) をインストール（bashが使える）
3. [Node.js](https://nodejs.org/) をダウンロード
4. PowerShell で：
```bash
npm install -g @anthropic-ai/claude-cli
pip install claude-plus
```

</details>

<details>
<summary><strong>📵 「command not found」と出る</strong></summary>

**Python が見つからない:**
- [Python.org](https://www.python.org/downloads/) からダウンロード

**brew が見つからない:**
- ステップ1の最初のコマンドをもう一度実行

**npm が見つからない:**
```bash
brew install node
```

</details>

<details>
<summary><strong>「Permission denied」と出る</strong></summary>

```bash
# ユーザー権限でインストール
pip install --user claude-plus
```

</details>

<details>
<summary><strong>API キーがうまくいかない</strong></summary>

1. [Console.anthropic.com](https://console.anthropic.com/) で新しいキーを作成
2. `claude login` をもう一度実行
3. 新しいキーを貼り付け

</details>

---

## ⚡ さあ、プログラミングを楽しみましょう！

**終了するとき:** `Ctrl + C` を2回押す

**困った時の魔法の言葉:**
- 「エラーを直して」
- 「説明して」  
- 「もっと簡単にして」

**Claude-Plus があなたの開発を全自動化します！** ✨