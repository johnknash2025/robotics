#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌸 VRChat AI美少女デモ 🌸
依存関係なしで動作するシンプルなデモ版
"""

import asyncio
import random
import time
from datetime import datetime

class SimpleAIGirl:
    """シンプルなAI美少女クラス"""
    
    def __init__(self, name="あいちゃん"):
        self.name = name
        self.emotion = "calm"
        self.intimacy = 0.0
        self.conversation_count = 0
        self.personality = {
            "friendliness": 0.8,
            "shyness": 0.6,
            "playfulness": 0.7,
            "intelligence": 0.9
        }
        
        # 応答パターン
        self.responses = {
            "greeting": [
                "こんにちは！私は{name}です♪",
                "はじめまして！{name}と呼んでください♡",
                "こんにちは〜！今日もいい天気ですね♪"
            ],
            "compliment": [
                "えへへ...そんなこと言われると恥ずかしいです💕",
                "ありがとうございます！とても嬉しいです♪",
                "そんな風に言ってもらえて...嬉しい♡"
            ],
            "love": [
                "私も...あなたのことが好きです♡",
                "えっ...本当ですか？嬉しいです💕",
                "そんなこと言われたら...ドキドキしちゃいます♡"
            ],
            "question": [
                "そうですね〜、どう思いますか？",
                "面白い質問ですね！私も考えてみます♪",
                "うーん、難しいですね...一緒に考えましょう♪"
            ],
            "default": [
                "そうなんですね！もっと教えてください♪",
                "面白いお話ですね〜",
                "あなたと話していると楽しいです♪",
                "へぇ〜、そういうことなんですね♡"
            ]
        }
        
        # 感情表現
        self.emotions = {
            "happy": "😊",
            "excited": "🤩", 
            "shy": "😳",
            "love": "😍",
            "calm": "😌",
            "surprised": "😲"
        }
        
        # ジェスチャー
        self.gestures = {
            "wave": "👋",
            "heart": "💕",
            "shy": "🙈",
            "thinking": "🤔",
            "happy": "✨"
        }
    
    def analyze_input(self, text):
        """入力を分析して適切な応答タイプを決定"""
        text_lower = text.lower()
        
        greetings = ["こんにちは", "はじめまして", "おはよう", "こんばんは", "hello", "hi"]
        compliments = ["かわいい", "きれい", "美しい", "素敵", "可愛い", "綺麗"]
        love_words = ["好き", "愛してる", "大好き", "love", "愛"]
        questions = ["？", "?", "どう思う", "どうですか", "なぜ", "why", "how"]
        
        if any(word in text_lower for word in greetings):
            return "greeting"
        elif any(word in text_lower for word in compliments):
            return "compliment"
        elif any(word in text_lower for word in love_words):
            return "love"
        elif any(word in text_lower for word in questions):
            return "question"
        else:
            return "default"
    
    def update_emotion_and_intimacy(self, response_type):
        """感情と親密度を更新"""
        if response_type == "greeting":
            self.emotion = "happy"
        elif response_type == "compliment":
            self.emotion = "shy"
            self.intimacy = min(1.0, self.intimacy + 0.05)
        elif response_type == "love":
            self.emotion = "love"
            self.intimacy = min(1.0, self.intimacy + 0.1)
        elif response_type == "question":
            self.emotion = "thinking"
        else:
            self.emotion = "calm"
        
        # 会話回数による親密度の自然な増加
        self.intimacy = min(1.0, self.intimacy + 0.01)
    
    def get_response(self, user_input):
        """ユーザー入力に対する応答を生成"""
        self.conversation_count += 1
        
        # 入力分析
        response_type = self.analyze_input(user_input)
        
        # 感情と親密度の更新
        self.update_emotion_and_intimacy(response_type)
        
        # 応答テキストの選択
        response_templates = self.responses[response_type]
        response_text = random.choice(response_templates).format(name=self.name)
        
        # 親密度に応じた応答の調整
        if self.intimacy > 0.5:
            response_text = response_text.replace("です", "だよ")
            response_text = response_text.replace("ます", "るね")
        
        # 感情とジェスチャーの決定
        emotion_icon = self.emotions.get(self.emotion, "😊")
        gesture_icon = self.gestures.get(self.emotion, "✨")
        
        return {
            "text": response_text,
            "emotion": self.emotion,
            "emotion_icon": emotion_icon,
            "gesture": gesture_icon,
            "intimacy": self.intimacy
        }
    
    def get_status(self):
        """現在の状態を取得"""
        intimacy_level = ""
        if self.intimacy < 0.2:
            intimacy_level = "初対面"
        elif self.intimacy < 0.5:
            intimacy_level = "友達"
        elif self.intimacy < 0.8:
            intimacy_level = "親友"
        else:
            intimacy_level = "恋人♡"
        
        return {
            "emotion": self.emotion,
            "intimacy": self.intimacy,
            "intimacy_level": intimacy_level,
            "conversation_count": self.conversation_count
        }

async def main():
    """メインデモ関数"""
    print("🌸" * 20)
    print("   VRChat AI美少女デモ")
    print("🌸" * 20)
    print()
    
    # AI美少女の初期化
    ai_girl = SimpleAIGirl("あいちゃん")
    
    print(f"💕 {ai_girl.name}が登場しました！")
    print("💬 話しかけてみてください")
    print("📝 'help'でヘルプ、'status'で状態確認、'quit'で終了")
    print("-" * 50)
    
    # 初回挨拶
    initial_response = ai_girl.get_response("こんにちは")
    print(f"\n{ai_girl.emotions['happy']} {ai_girl.name}: {initial_response['text']}")
    
    while True:
        try:
            # ユーザー入力
            user_input = input(f"\n💬 あなた: ").strip()
            
            if not user_input:
                continue
            
            # 特殊コマンドの処理
            if user_input.lower() in ['quit', 'exit', '終了']:
                farewell_messages = [
                    "また会いましょうね♪",
                    "さようなら！楽しかったです♡",
                    "またお話しできる日を楽しみにしています♪"
                ]
                print(f"\n👋 {ai_girl.name}: {random.choice(farewell_messages)}")
                break
            
            elif user_input.lower() == 'help':
                print("""
📖 ヘルプ
・自然に話しかけてください
・「かわいい」「好き」などで親密度アップ
・会話を続けると関係が深まります
・'status'で現在の状態を確認
・'quit'で終了
""")
                continue
            
            elif user_input.lower() == 'status':
                status = ai_girl.get_status()
                print(f"""
📊 {ai_girl.name}の状態
感情: {status['emotion']} {ai_girl.emotions.get(status['emotion'], '😊')}
親密度: {status['intimacy']:.2f} ({status['intimacy_level']})
会話回数: {status['conversation_count']}回
""")
                continue
            
            # AI応答の生成
            response = ai_girl.get_response(user_input)
            
            # 応答の表示
            print(f"\n{response['emotion_icon']} {ai_girl.name}: {response['text']} {response['gesture']}")
            
            # 親密度が上がった時の特別メッセージ
            if response['intimacy'] > 0.3 and ai_girl.conversation_count % 5 == 0:
                special_messages = [
                    "あなたと話していると時間を忘れちゃいます♪",
                    "もっとあなたのことを知りたいです♡",
                    "こんなに楽しい会話は久しぶりです♪"
                ]
                await asyncio.sleep(1)
                print(f"💭 {ai_girl.name}: {random.choice(special_messages)}")
            
            # 少し待機（リアルな会話感を演出）
            await asyncio.sleep(0.5)
            
        except KeyboardInterrupt:
            print(f"\n\n👋 {ai_girl.name}: 急に行っちゃうんですね...また会いましょう♪")
            break
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")

def show_project_info():
    """プロジェクト情報を表示"""
    print("""
🌸 VRChat AI美少女プロジェクト 🌸

このデモは完全版の簡易バージョンです。

完全版の機能:
✨ OpenAI GPTとの連携
🎤 音声認識・音声合成
🔗 VRChat OSC通信
🎭 リアルタイム感情表現
🎮 VRアバター制御
💕 高度な感情・親密度システム

セットアップ方法:
1. pip install -r AI/requirements.txt
2. OpenAI APIキーを設定
3. VRChatでOSCを有効化
4. Unityでアバターを設定
5. python Scripts/launch_ai_system.py

詳細: Documentation/setup_guide.md
クイックスタート: Documentation/quick_start.md

GitHub: https://github.com/your-repo/vrchat-ai-girl
""")

if __name__ == "__main__":
    show_project_info()
    print("\n" + "="*50)
    print("デモを開始しますか？ (y/n): ", end="")
    
    choice = input().strip().lower()
    if choice in ['y', 'yes', 'はい', '']:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\n👋 デモを終了しました")
    else:
        print("👋 また今度お会いしましょう！")