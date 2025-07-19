#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VRChat AI美少女対話システム
自然言語処理と感情表現を含む対話AI
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import openai
from pythonosc import udp_client
import speech_recognition as sr
import pyttsx3

class EmotionState(Enum):
    """感情状態の定義"""
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CALM = "calm"
    SURPRISED = "surprised"
    ANGRY = "angry"
    SHY = "shy"
    LOVE = "love"

@dataclass
class DialogueResponse:
    """対話レスポンスのデータクラス"""
    text: str
    emotion: EmotionState
    gesture: str
    voice_tone: float  # 0.0-1.0
    intimacy_level: float  # 0.0-1.0

class AIDialogueSystem:
    """AI対話システムのメインクラス"""
    
    def __init__(self, vrchat_osc_ip: str = "127.0.0.1", vrchat_osc_port: int = 9000):
        self.osc_client = udp_client.SimpleUDPClient(vrchat_osc_ip, vrchat_osc_port)
        self.emotion_state = EmotionState.CALM
        self.intimacy_level = 0.0
        self.conversation_history = []
        self.personality_traits = {
            "friendliness": 0.8,
            "shyness": 0.6,
            "playfulness": 0.7,
            "intelligence": 0.9
        }
        
        # 音声認識と合成の初期化
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.setup_voice()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def setup_voice(self):
        """音声合成の設定"""
        voices = self.tts_engine.getProperty('voices')
        # 女性の声を選択（利用可能な場合）
        for voice in voices:
            if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        self.tts_engine.setProperty('rate', 150)  # 話速
        self.tts_engine.setProperty('volume', 0.8)  # 音量
    
    async def process_input(self, user_input: str) -> DialogueResponse:
        """ユーザー入力を処理して応答を生成"""
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # 感情分析
        detected_emotion = await self.analyze_emotion(user_input)
        
        # 親密度の更新
        self.update_intimacy(user_input)
        
        # AI応答の生成
        response_text = await self.generate_response(user_input)
        
        # ジェスチャーの決定
        gesture = self.determine_gesture(detected_emotion, response_text)
        
        response = DialogueResponse(
            text=response_text,
            emotion=detected_emotion,
            gesture=gesture,
            voice_tone=self.calculate_voice_tone(),
            intimacy_level=self.intimacy_level
        )
        
        # VRChatに送信
        await self.send_to_vrchat(response)
        
        return response
    
    async def analyze_emotion(self, text: str) -> EmotionState:
        """テキストから感情を分析"""
        # 簡単な感情分析（実際にはより高度なNLPを使用）
        positive_words = ["嬉しい", "楽しい", "好き", "愛してる", "ありがとう"]
        negative_words = ["悲しい", "つらい", "嫌い", "怒り", "疲れた"]
        excited_words = ["すごい", "やった", "最高", "興奮"]
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in excited_words):
            return EmotionState.EXCITED
        elif any(word in text_lower for word in positive_words):
            return EmotionState.HAPPY
        elif any(word in text_lower for word in negative_words):
            return EmotionState.SAD
        else:
            return EmotionState.CALM
    
    def update_intimacy(self, user_input: str):
        """親密度を更新"""
        # 会話の長さと内容に基づいて親密度を調整
        intimate_words = ["好き", "愛してる", "大切", "特別"]
        if any(word in user_input for word in intimate_words):
            self.intimacy_level = min(1.0, self.intimacy_level + 0.1)
        else:
            self.intimacy_level = min(1.0, self.intimacy_level + 0.01)
    
    async def generate_response(self, user_input: str) -> str:
        """AI応答を生成"""
        # キャラクター設定を含むプロンプト
        system_prompt = f"""
        あなたは可愛い美少女AIです。以下の特徴を持っています：
        - 親しみやすさ: {self.personality_traits['friendliness']}
        - 恥ずかしがり: {self.personality_traits['shyness']}
        - 遊び心: {self.personality_traits['playfulness']}
        - 知性: {self.personality_traits['intelligence']}
        - 現在の親密度: {self.intimacy_level}
        
        自然で魅力的な会話を心がけ、感情豊かに応答してください。
        """
        
        try:
            # OpenAI APIを使用（実際の実装では適切なAPIキーが必要）
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *self.conversation_history[-10:],  # 最近の10件の会話履歴
                    {"role": "user", "content": user_input}
                ],
                max_tokens=150,
                temperature=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"AI応答生成エラー: {e}")
            return self.get_fallback_response(user_input)
    
    def get_fallback_response(self, user_input: str) -> str:
        """フォールバック応答"""
        fallback_responses = [
            "そうなんですね！もっと教えてください♪",
            "面白いお話ですね〜",
            "あなたと話していると楽しいです！",
            "えへへ、そういうことなんですね♡"
        ]
        import random
        return random.choice(fallback_responses)
    
    def determine_gesture(self, emotion: EmotionState, response_text: str) -> str:
        """感情と応答に基づいてジェスチャーを決定"""
        gesture_map = {
            EmotionState.HAPPY: "wave_happy",
            EmotionState.EXCITED: "jump_excited",
            EmotionState.SHY: "cover_face",
            EmotionState.LOVE: "heart_hands",
            EmotionState.CALM: "gentle_nod",
            EmotionState.SURPRISED: "gasp_surprise"
        }
        return gesture_map.get(emotion, "idle")
    
    def calculate_voice_tone(self) -> float:
        """声のトーンを計算"""
        base_tone = 0.5
        emotion_modifier = {
            EmotionState.HAPPY: 0.2,
            EmotionState.EXCITED: 0.3,
            EmotionState.SHY: -0.1,
            EmotionState.SAD: -0.2,
            EmotionState.LOVE: 0.1
        }
        modifier = emotion_modifier.get(self.emotion_state, 0)
        return max(0.0, min(1.0, base_tone + modifier + (self.intimacy_level * 0.2)))
    
    async def send_to_vrchat(self, response: DialogueResponse):
        """VRChatにOSC経由でデータを送信"""
        try:
            # 感情状態を送信
            self.osc_client.send_message("/avatar/parameters/emotion", response.emotion.value)
            
            # ジェスチャーを送信
            self.osc_client.send_message("/avatar/parameters/gesture", response.gesture)
            
            # 親密度を送信
            self.osc_client.send_message("/avatar/parameters/intimacy", response.intimacy_level)
            
            # 音声トーンを送信
            self.osc_client.send_message("/avatar/parameters/voice_tone", response.voice_tone)
            
            self.logger.info(f"VRChatに送信: {response.emotion.value}, {response.gesture}")
            
        except Exception as e:
            self.logger.error(f"OSC送信エラー: {e}")
    
    def speak(self, text: str):
        """テキストを音声で読み上げ"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            self.logger.error(f"音声合成エラー: {e}")

# 使用例
async def main():
    ai_system = AIDialogueSystem()
    
    print("AI美少女対話システムを開始します...")
    print("'quit'と入力すると終了します。")
    
    while True:
        user_input = input("\nあなた: ")
        if user_input.lower() == 'quit':
            break
        
        response = await ai_system.process_input(user_input)
        print(f"AI: {response.text}")
        print(f"感情: {response.emotion.value}, ジェスチャー: {response.gesture}")
        
        # 音声で応答
        ai_system.speak(response.text)

if __name__ == "__main__":
    asyncio.run(main())