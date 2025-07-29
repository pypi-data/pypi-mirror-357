#!/usr/bin/env python3
"""
Claude++ 日本語UI管理システム
全ての技術用語を日常用語に翻訳し、初心者にも分かりやすいメッセージを提供します。
"""

import logging
import random
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import re


class MessageType(Enum):
    """メッセージの種類"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    PROGRESS = "progress"
    HELP = "help"


class UIContext(Enum):
    """UI表示の文脈"""
    STARTUP = "起動時"
    WORK_START = "作業開始"
    WORK_PROGRESS = "作業中"
    WORK_SAVE = "保存"
    WORK_COMPLETE = "完了"
    ERROR_RECOVERY = "エラー復旧"
    HELP = "ヘルプ"


class JapaneseUIManager:
    """日本語UI管理システム - 技術用語を完全に隠蔽"""
    
    def __init__(self):
        self.logger = logging.getLogger('claude-plus.japanese_ui')
        
        # 基本メッセージテンプレート
        self.base_messages = {
            # 作業開始関連
            'work_start_new': [
                "新しい作業を開始しました ✨",
                "作業を始めます 🚀",
                "新しいプロジェクトをスタートしました 📝"
            ],
            'work_start_continue': [
                "前回の続きから開始します 🔄",
                "中断していた作業を再開します ▶️",
                "前の作業を引き続き行います 📖"
            ],
            'work_folder_ready': [
                "新しい作業フォルダを準備しました 📁",
                "専用の作業スペースを用意しました 🏗️",
                "作業環境のセットアップが完了しました 🛠️"
            ],
            
            # 保存関連
            'auto_save': [
                "作業内容を自動保存しました 💾",
                "進捗を安全に保存しました 🔒",
                "作業データをバックアップしました 📦"
            ],
            'manual_save': [
                "作業を手動保存しました ✅",
                "現在の状態を記録しました 📋",
                "進捗を確定しました 🎯"
            ],
            
            # バックアップ関連
            'cloud_backup': [
                "クラウドにバックアップしました ☁️",
                "オンラインストレージに保存しました 🌐",
                "リモートサーバーに同期しました 🔄"
            ],
            'local_backup': [
                "ローカルにバックアップしました 💽",
                "このコンピューター内に保存しました 🖥️",
                "作業データを複製しました 📋"
            ],
            
            # 完了関連
            'work_complete': [
                "作業が完了しました 🎉",
                "お疲れさまでした！作業終了です 👏",
                "プロジェクトが完成しました ✨"
            ],
            'session_end': [
                "作業セッションを終了します 🔚",
                "今日の作業を締めくくります 🌅",
                "作業を一旦終了します ⏸️"
            ],
            
            # エラー・復旧関連
            'auto_recovery': [
                "自動で問題を解決しました 🔧",
                "エラーを自動修復しました ⚡",
                "システムが自動対応しました 🛡️"
            ],
            'safe_recovery': [
                "安全な状態に戻しました 🔄",
                "前の安定した状態に復旧しました 📚",
                "問題発生前の状況に復元しました ⏪"
            ],
            'emergency_save': [
                "緊急保存を実行しました ⚡",
                "作業データを緊急避難させました 🚨",
                "大切な作業を守りました 🛡️"
            ],
            
            # 進捗・状態関連
            'analyzing': [
                "状況を確認中です... 🔍",
                "現在の作業を分析中... 📊",
                "システムが状況を把握中... 🤔"
            ],
            'preparing': [
                "準備中です... ⚙️",
                "環境をセットアップ中... 🛠️",
                "作業の準備をしています... 📋"
            ],
            'processing': [
                "処理中です... ⏳",
                "作業を実行中... 🔄",
                "システムが動作中... ⚡"
            ]
        }
        
        # エラーメッセージの日本語化（Claude Code特有のエラーを含む）
        self.error_translations = {
            # Claude Code特有エラー
            'api key not found': "Claude APIキーが設定されていません。設定ファイルを確認してください。",
            'api quota exceeded': "Claude APIの使用量制限に達しました。しばらく待ってから再試行してください。",
            'model not available': "指定されたAIモデルが利用できません。別のモデルを試します。",
            'input must be provided': "入力が必要です。プロンプトまたはファイル入力を確認してください。",
            'context length exceeded': "入力内容が長すぎます。内容を分割して処理します。",
            'rate limit exceeded': "リクエスト数の制限に達しました。少し待ってから再試行します。",
            'invalid request': "リクエストの形式が正しくありません。内容を確認して再試行します。",
            'authentication error': "Claude APIの認証に失敗しました。APIキーを確認してください。",
            
            # ファイル操作エラー（Claude Code関連）
            'file already exists': "ファイルが既に存在します。上書きするか別の名前で保存してください。",
            'overwrite confirmation': "既存のファイルを上書きしますか？自動で「Yes」を選択しました。",
            'directory not found': "指定されたフォルダが見つかりません。新しく作成します。",
            'read only file': "ファイルが読み取り専用です。編集権限を確認してください。",
            'file in use': "ファイルが他のアプリで使用中です。しばらく待ってから再試行します。",
            'encoding error': "ファイルの文字エンコーディングに問題があります。UTF-8で保存します。",
            
            # プロジェクト関連エラー
            'module not found': "必要なモジュールが見つかりません。自動でインストールを試みます。",
            'dependency error': "依存関係に問題があります。package.jsonやrequirements.txtを確認します。",
            'build failed': "プロジェクトのビルドに失敗しました。設定ファイルを確認してください。",
            'test failed': "テストの実行に失敗しました。コードを確認して修正します。",
            'linting error': "コードの品質チェックでエラーが発見されました。自動で修正を試みます。",
            'syntax error': "コードの文法にエラーがあります。該当箇所を確認して修正してください。",
            
            # tmux/画面分割関連エラー
            'tmux not found': "画面分割ツール（tmux）が見つかりません。単一画面モードで動作します。",
            'session already exists': "同名のセッションが既に存在します。新しい名前で作成します。",
            'pane creation failed': "画面分割に失敗しました。単一画面モードに切り替えます。",
            'terminal too small': "ターミナルが小さすぎます。ウィンドウを大きくしてください。",
            'mouse mode error': "マウス操作の設定でエラーが発生しました。キーボード操作をご利用ください。",
            
            # Git関連エラー
            'git not found': "作業管理ツールが見つかりません。セットアップが必要です。",
            'not a git repository': "このフォルダは作業管理の対象外です。初期設定を行います。",
            'merge conflict': "ファイルの競合が発生しました。自動で解決を試みます。",
            'push failed': "クラウドへの保存に失敗しました。インターネット接続を確認してください。",
            'pull failed': "最新版の取得に失敗しました。後でもう一度試します。",
            'branch exists': "同じ名前の作業フォルダが既に存在します。別の名前で作成します。",
            'uncommitted changes': "未保存の変更があります。先に保存してから続行します。",
            
            # ネットワーク関連エラー
            'connection timeout': "インターネット接続がタイムアウトしました。しばらく待ってから再試行します。",
            'network error': "ネットワークエラーが発生しました。接続状況を確認してください。",
            'authentication failed': "認証に失敗しました。アカウント設定を確認してください。",
            'ssl error': "セキュア接続でエラーが発生しました。証明書を確認してください。",
            'proxy error': "プロキシ設定でエラーが発生しました。ネットワーク管理者に確認してください。",
            
            # ファイル関連エラー
            'file not found': "ファイルが見つかりません。削除または移動された可能性があります。",
            'permission denied': "ファイルへのアクセス権限がありません。管理者に確認してください。",
            'disk full': "ディスク容量が不足しています。不要なファイルを削除してください。",
            'path too long': "ファイルパスが長すぎます。より短いパスに移動してください。",
            
            # システム関連エラー
            'command not found': "コマンドが見つかりません。必要なツールがインストールされているか確認してください。",
            'out of memory': "メモリが不足しています。他のアプリを終了してから再試行してください。",
            'timeout': "処理時間が長すぎます。システムが自動でタイムアウトしました。",
            'unexpected error': "予期しないエラーが発生しました。作業を安全に保存します。",
            'process killed': "プロセスが強制終了されました。自動で再起動を試みます。",
            'signal received': "システムシグナルを受信しました。安全に終了処理を行います。"
        }
        
        # エラー解決方法の詳細提示
        self.error_solutions = {
            # Claude Code特有エラーの解決方法
            'api key not found': {
                'steps': [
                    "1. ~/.claude/config.yaml を確認してください",
                    "2. APIキーが正しく設定されているか確認",
                    "3. 環境変数 ANTHROPIC_API_KEY を設定",
                    "4. claude --configure でAPIキーを再設定"
                ],
                'auto_fix': True,
                'priority': 'high'
            },
            'api quota exceeded': {
                'steps': [
                    "1. しばらく時間を置いてから再試行",
                    "2. Anthropicアカウントのプラン確認",
                    "3. 使用量制限の確認・アップグレード検討"
                ],
                'auto_fix': False,
                'priority': 'medium'
            },
            'input must be provided': {
                'steps': [
                    "1. 入力ファイルまたはプロンプトを指定",
                    "2. コマンド引数を確認",
                    "3. パイプ入力の場合は適切な形式を確認"
                ],
                'auto_fix': True,
                'priority': 'high'
            },
            
            # ファイル操作エラーの解決方法
            'file already exists': {
                'steps': [
                    "1. 自動で上書き確認プロンプトに「Yes」で応答",
                    "2. 別のファイル名での保存も可能",
                    "3. バックアップを作成してから上書き"
                ],
                'auto_fix': True,
                'priority': 'low'
            },
            'permission denied': {
                'steps': [
                    "1. sudo権限でファイルアクセスを試行",
                    "2. ファイル所有者・権限の確認",
                    "3. chmod コマンドで権限変更",
                    "4. 管理者に権限変更を依頼"
                ],
                'auto_fix': False,
                'priority': 'medium'
            },
            
            # tmux関連エラーの解決方法
            'tmux not found': {
                'steps': [
                    "1. 単一画面モードで動作継続",
                    "2. tmuxインストール: brew install tmux (macOS)",
                    "3. tmuxインストール: apt install tmux (Ubuntu)",
                    "4. フォールバックモードで全機能利用可能"
                ],
                'auto_fix': True,
                'priority': 'low'
            },
            'session already exists': {
                'steps': [
                    "1. 一意なセッション名で自動再作成",
                    "2. 既存セッションを確認: tmux list-sessions",
                    "3. 不要なセッションを削除: tmux kill-session"
                ],
                'auto_fix': True,
                'priority': 'low'
            },
            
            # Git関連エラーの解決方法
            'merge conflict': {
                'steps': [
                    "1. 自動マージの試行",
                    "2. 手動でコンフリクト解決が必要な場合は通知",
                    "3. git status で状況確認",
                    "4. コンフリクトファイルを編集後 git add"
                ],
                'auto_fix': True,
                'priority': 'medium'
            },
            'not a git repository': {
                'steps': [
                    "1. 自動で git init を実行",
                    "2. 初期設定の自動実行",
                    "3. 透明Git機能の有効化"
                ],
                'auto_fix': True,
                'priority': 'high'
            }
        }
        
        # 技術用語の翻訳辞書
        self.tech_translations = {
            # Git用語
            'git': '作業管理',
            'repository': 'プロジェクト',
            'repo': 'プロジェクト',
            'branch': '作業フォルダ',
            'commit': '保存',
            'push': 'クラウド保存',
            'pull': '最新版取得',
            'merge': '統合',
            'clone': '複製',
            'fork': '分岐',
            'pull request': '統合提案',
            'issue': '課題',
            'tag': '版番号',
            'release': 'リリース',
            
            # プログラミング用語
            'code': 'プログラム',
            'script': 'スクリプト',
            'function': '機能',
            'class': 'クラス',
            'variable': '変数',
            'debug': '問題解決',
            'test': 'テスト',
            'build': '構築',
            'deploy': '公開',
            'config': '設定',
            'api': 'インターフェース',
            
            # システム用語
            'daemon': 'バックグラウンド処理',
            'process': '処理',
            'thread': '並行処理',
            'server': 'サーバー',
            'client': 'クライアント',
            'database': 'データベース',
            'cache': 'キャッシュ',
            'log': 'ログ',
            'error': 'エラー',
            'warning': '警告'
        }
        
        # ヘルプメッセージ
        self.help_messages = {
            'getting_started': """
🌟 Claude++システムへようこそ！

このシステムは、あなたの作業を自動で安全に管理します。
特別な操作は必要ありません - ただ`claude`と入力するだけです。

✨ 自動で行われること:
• 新しい作業フォルダの作成
• 30分ごとの自動保存
• 作業完了時のバックアップ
• エラー時の自動復旧

🛡️ あなたの作業は常に安全に保護されています。
""",
            
            'work_flow': """
📋 作業の流れ:

1. ターミナルで `claude` と入力
2. 作業内容をClaudeCodeで説明
3. 自動で適切な作業環境が準備されます
4. 普通にプログラミング作業を行う
5. 定期的に自動保存されます
6. 作業完了時に自動でバックアップされます

🎯 あなたは作業内容だけに集中してください！
""",
            
            'troubleshooting': """
🔧 よくある質問:

Q: 作業が消えてしまう心配はありませんか？
A: 30分ごとの自動保存と緊急時の自動保護があるので安心です。

Q: インターネット接続が切れたらどうなりますか？
A: ローカルに保存され、接続復旧時に自動でバックアップされます。

Q: 間違って何かを削除してしまったら？
A: 自動で前の安全な状態に戻すことができます。

🆘 問題が発生した場合は、システムが自動で対処します。
"""
        }
        
    def get_message(self, message_key: str, context: UIContext = None, **kwargs) -> str:
        """メッセージを取得（ランダム選択で自然性を向上）"""
        try:
            if message_key in self.base_messages:
                messages = self.base_messages[message_key]
                selected = random.choice(messages)
                
                # 動的な値の挿入
                if kwargs:
                    try:
                        selected = selected.format(**kwargs)
                    except KeyError:
                        pass  # フォーマット失敗時はそのまま返す
                        
                return selected
            else:
                # メッセージが見つからない場合のフォールバック
                return f"メッセージ: {message_key}"
                
        except Exception as e:
            self.logger.error(f"メッセージ取得エラー: {e}")
            return "システムメッセージの取得に失敗しました"
            
    def translate_error(self, error_message: str) -> str:
        """エラーメッセージを分かりやすい日本語に翻訳"""
        error_lower = error_message.lower()
        
        # 既定の翻訳から検索
        for tech_term, japanese in self.error_translations.items():
            if tech_term in error_lower:
                return f"💡 {japanese}"
                
        # 技術用語の置き換え
        translated = error_message
        for tech_term, japanese in self.tech_translations.items():
            pattern = re.compile(re.escape(tech_term), re.IGNORECASE)
            translated = pattern.sub(japanese, translated)
            
        return f"⚠️ {translated}"
        
    def translate_tech_term(self, text: str) -> str:
        """技術用語を日常用語に翻訳"""
        translated = text
        
        for tech_term, japanese in self.tech_translations.items():
            pattern = re.compile(re.escape(tech_term), re.IGNORECASE)
            translated = pattern.sub(japanese, translated)
            
        return translated
        
    def format_progress_message(self, current: int, total: int, action: str) -> str:
        """進捗メッセージのフォーマット"""
        percentage = int((current / total) * 100) if total > 0 else 0
        
        # 進捗バーの生成
        bar_length = 20
        filled = int(bar_length * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        
        return f"{action} [{bar}] {percentage}% ({current}/{total})"
        
    def format_time_message(self, start_time: datetime, action: str = "作業") -> str:
        """時間ベースのメッセージフォーマット"""
        now = datetime.now()
        elapsed = now - start_time
        
        if elapsed.total_seconds() < 60:
            return f"{action}を開始しました"
        elif elapsed.total_seconds() < 3600:
            minutes = int(elapsed.total_seconds() / 60)
            return f"{action}中です（{minutes}分経過）"
        else:
            hours = int(elapsed.total_seconds() / 3600)
            minutes = int((elapsed.total_seconds() % 3600) / 60)
            return f"{action}中です（{hours}時間{minutes}分経過）"
            
    def get_encouraging_message(self) -> str:
        """励ましのメッセージを取得"""
        encouraging_messages = [
            "順調に進んでいます！ 💪",
            "素晴らしい作業ぶりです！ ⭐",
            "このまま続けていきましょう！ 🚀",
            "いい感じです！ 👍",
            "作業が進んでいますね！ 📈",
            "がんばっていますね！ 🌟",
            "着実に進歩しています！ 📊",
            "このペースで行きましょう！ ⚡"
        ]
        return random.choice(encouraging_messages)
        
    def get_completion_message(self, work_type: str = "作業") -> str:
        """完了時のメッセージを取得"""
        completion_messages = [
            f"{work_type}お疲れさまでした！ 🎉",
            f"素晴らしい{work_type}でした！ ⭐",
            f"{work_type}完了です！よくできました！ 👏",
            f"お見事です！{work_type}が完成しました！ ✨",
            f"{work_type}終了！お疲れさまでした！ 🏆"
        ]
        return random.choice(completion_messages)
        
    def get_help_message(self, topic: str = 'getting_started') -> str:
        """ヘルプメッセージを取得"""
        return self.help_messages.get(topic, "ヘルプ情報が見つかりません")
        
    def format_notification_title(self, message_type: MessageType, context: UIContext) -> str:
        """通知タイトルのフォーマット"""
        type_names = {
            MessageType.INFO: "情報",
            MessageType.SUCCESS: "完了",
            MessageType.WARNING: "注意",
            MessageType.ERROR: "エラー",
            MessageType.PROGRESS: "進行中",
            MessageType.HELP: "ヘルプ"
        }
        
        context_names = {
            UIContext.STARTUP: "起動",
            UIContext.WORK_START: "作業開始",
            UIContext.WORK_PROGRESS: "作業中",
            UIContext.WORK_SAVE: "保存",
            UIContext.WORK_COMPLETE: "完了",
            UIContext.ERROR_RECOVERY: "復旧",
            UIContext.HELP: "ヘルプ"
        }
        
        type_name = type_names.get(message_type, "システム")
        context_name = context_names.get(context, "")
        
        if context_name:
            return f"Claude++ {context_name}"
        else:
            return f"Claude++ {type_name}"
            
    def create_user_friendly_summary(self, technical_summary: str) -> str:
        """技術的な要約をユーザーフレンドリーに変換"""
        # 技術用語の置き換え
        friendly = self.translate_tech_term(technical_summary)
        
        # 文章の調整
        friendly = re.sub(r'successfully?', '正常に', friendly, flags=re.IGNORECASE)
        friendly = re.sub(r'failed?', '失敗しました', friendly, flags=re.IGNORECASE)
        friendly = re.sub(r'error', 'エラー', friendly, flags=re.IGNORECASE)
        friendly = re.sub(r'warning', '警告', friendly, flags=re.IGNORECASE)
        
        return friendly


# グローバルインスタンス
_ui_manager = JapaneseUIManager()

def get_ui_manager() -> JapaneseUIManager:
    """UIマネージャーのシングルトンインスタンスを取得"""
    return _ui_manager


# 便利な関数
def translate_to_japanese(text: str) -> str:
    """テキストを日本語に翻訳"""
    return _ui_manager.translate_tech_term(text)

def get_friendly_error(error: str) -> str:
    """エラーを分かりやすく翻訳"""
    return _ui_manager.translate_error(error)

def get_work_message(message_type: str, **kwargs) -> str:
    """作業関連メッセージを取得"""
    return _ui_manager.get_message(message_type, **kwargs)


# テスト用コード
if __name__ == "__main__":
    ui = JapaneseUIManager()
    
    print("日本語UI管理システムのテスト:")
    print("-" * 40)
    
    # メッセージテスト
    print("作業開始:", ui.get_message('work_start_new'))
    print("自動保存:", ui.get_message('auto_save'))
    print("バックアップ:", ui.get_message('cloud_backup'))
    print("完了:", ui.get_message('work_complete'))
    print()
    
    # エラー翻訳テスト
    print("エラー翻訳テスト:")
    print("Git error →", ui.translate_error("git not found"))
    print("Network error →", ui.translate_error("connection timeout"))
    print("File error →", ui.translate_error("permission denied"))
    print()
    
    # 技術用語翻訳テスト
    print("技術用語翻訳テスト:")
    print("Original: Create a new branch for this feature")
    print("Translated:", ui.translate_tech_term("Create a new branch for this feature"))
    print()
    
    # ヘルプメッセージテスト
    print("ヘルプメッセージ:")
    print(ui.get_help_message('getting_started'))