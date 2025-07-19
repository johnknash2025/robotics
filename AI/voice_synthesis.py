#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音声合成システム
複数の音声エンジンに対応
"""

import asyncio
import logging
import requests
import json
from abc import ABC, abstractmethod
from typing import Optional
import pyttsx3
from config import config

class VoiceSynthesizer(ABC):
    """音声合成の抽象基底クラス"""
    
    @abstractmethod
    async def synthesize(self, text: str, emotion: str = "neutral") -> bool:
        """テキストを音声合成して再生"""
        pass

class PyttsxVoiceSynthesizer(VoiceSynthesizer):
    """pyttsx3を使用した音声合成"""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        self.setup_voice()
        self.logger = logging.getLogger(__name__)
    
    def setup_voice(self):
        """音声設定"""
        voices = self.engine.getProperty('voices')
        
        # 日本語または女性の声を優先選択
        for voice in voices:
            if ('japanese' in voice.name.lower() or 
                'female' in voice.name.lower() or 
                'woman' in voice.name.lower()):
                self.engine.setProperty('voice', voice.id)
                break
        
        self.engine.setProperty('rate', config.voice_rate)
        self.engine.setProperty('volume', config.voice_volume)
    
    async def synthesize(self, text: str, emotion: str = "neutral") -> bool:
        """音声合成と再生"""
        try:
            # 感情に応じて音声パラメータを調整
            self.adjust_voice_for_emotion(emotion)
            
            # 非同期で音声合成
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._speak, text)
            
            return True
        except Exception as e:
            self.logger.error(f"pyttsx3音声合成エラー: {e}")
            return False
    
    def _speak(self, text: str):
        """同期的な音声合成"""
        self.engine.say(text)
        self.engine.runAndWait()
    
    def adjust_voice_for_emotion(self, emotion: str):
        """感情に応じて音声パラメータを調整"""
        emotion_settings = {
            "happy": {"rate": config.voice_rate + 20, "volume": config.voice_volume + 0.1},
            "excited": {"rate": config.voice_rate + 40, "volume": config.voice_volume + 0.2},
            "sad": {"rate": config.voice_rate - 30, "volume": config.voice_volume - 0.1},
            "shy": {"rate": config.voice_rate - 10, "volume": config.voice_volume - 0.2},
            "angry": {"rate": config.voice_rate + 30, "volume": config.voice_volume + 0.1},
            "calm": {"rate": config.voice_rate, "volume": config.voice_volume}
        }
        
        settings = emotion_settings.get(emotion, emotion_settings["calm"])
        
        self.engine.setProperty('rate', max(50, min(300, settings["rate"])))
        self.engine.setProperty('volume', max(0.0, min(1.0, settings["volume"])))

class VoicevoxVoiceSynthesizer(VoiceSynthesizer):
    """VOICEVOXを使用した音声合成"""
    
    def __init__(self):
        self.base_url = config.voicevox_url
        self.speaker_id = config.voicevox_speaker_id
        self.logger = logging.getLogger(__name__)
        
        # 感情とスピーカーIDのマッピング
        self.emotion_speakers = {
            "happy": 1,      # ずんだもん（ノーマル）
            "excited": 7,    # ずんだもん（ツンツン）
            "sad": 6,        # ずんだもん（悲しみ）
            "shy": 5,        # ずんだもん（ささやき）
            "angry": 4,      # ずんだもん（怒り）
            "calm": 1,       # ずんだもん（ノーマル）
            "love": 3        # ずんだもん（あまあま）
        }
    
    async def synthesize(self, text: str, emotion: str = "neutral") -> bool:
        """VOICEVOX APIを使用した音声合成"""
        try:
            speaker_id = self.emotion_speakers.get(emotion, self.speaker_id)
            
            # 音声クエリの生成
            audio_query = await self._create_audio_query(text, speaker_id)
            if not audio_query:
                return False
            
            # 音声合成
            audio_data = await self._synthesize_audio(audio_query, speaker_id)
            if not audio_data:
                return False
            
            # 音声再生
            await self._play_audio(audio_data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"VOICEVOX音声合成エラー: {e}")
            return False
    
    async def _create_audio_query(self, text: str, speaker_id: int) -> Optional[dict]:
        """音声クエリを作成"""
        try:
            url = f"{self.base_url}/audio_query"
            params = {"text": text, "speaker": speaker_id}
            
            response = requests.post(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"音声クエリ作成エラー: {e}")
            return None
    
    async def _synthesize_audio(self, audio_query: dict, speaker_id: int) -> Optional[bytes]:
        """音声データを合成"""
        try:
            url = f"{self.base_url}/synthesis"
            params = {"speaker": speaker_id}
            
            response = requests.post(
                url, 
                params=params,
                data=json.dumps(audio_query),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            self.logger.error(f"音声合成エラー: {e}")
            return None
    
    async def _play_audio(self, audio_data: bytes):
        """音声データを再生"""
        try:
            import pygame
            import io
            
            pygame.mixer.init()
            audio_file = io.BytesIO(audio_data)
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # 再生完了まで待機
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
        except ImportError:
            self.logger.warning("pygame未インストール。音声ファイルを保存します。")
            with open("temp_voice.wav", "wb") as f:
                f.write(audio_data)
        except Exception as e:
            self.logger.error(f"音声再生エラー: {e}")

class ElevenLabsVoiceSynthesizer(VoiceSynthesizer):
    """ElevenLabsを使用した音声合成"""
    
    def __init__(self):
        self.api_key = config.elevenlabs_api_key
        self.voice_id = config.elevenlabs_voice_id
        self.base_url = "https://api.elevenlabs.io/v1"
        self.logger = logging.getLogger(__name__)
    
    async def synthesize(self, text: str, emotion: str = "neutral") -> bool:
        """ElevenLabs APIを使用した音声合成"""
        try:
            if not self.api_key:
                self.logger.error("ElevenLabs APIキーが設定されていません")
                return False
            
            # 音声合成リクエスト
            audio_data = await self._generate_speech(text, emotion)
            if not audio_data:
                return False
            
            # 音声再生
            await self._play_audio(audio_data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"ElevenLabs音声合成エラー: {e}")
            return False
    
    async def _generate_speech(self, text: str, emotion: str) -> Optional[bytes]:
        """音声を生成"""
        try:
            url = f"{self.base_url}/text-to-speech/{self.voice_id}"
            
            # 感情に応じた設定
            voice_settings = self._get_voice_settings_for_emotion(emotion)
            
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": voice_settings
            }
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            self.logger.error(f"ElevenLabs音声生成エラー: {e}")
            return None
    
    def _get_voice_settings_for_emotion(self, emotion: str) -> dict:
        """感情に応じた音声設定"""
        emotion_settings = {
            "happy": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.3},
            "excited": {"stability": 0.3, "similarity_boost": 0.9, "style": 0.5},
            "sad": {"stability": 0.8, "similarity_boost": 0.6, "style": 0.1},
            "shy": {"stability": 0.9, "similarity_boost": 0.5, "style": 0.2},
            "angry": {"stability": 0.4, "similarity_boost": 0.9, "style": 0.6},
            "calm": {"stability": 0.7, "similarity_boost": 0.7, "style": 0.2}
        }
        
        return emotion_settings.get(emotion, emotion_settings["calm"])
    
    async def _play_audio(self, audio_data: bytes):
        """音声データを再生"""
        try:
            import pygame
            import io
            
            pygame.mixer.init()
            audio_file = io.BytesIO(audio_data)
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"音声再生エラー: {e}")

class VoiceSynthesisManager:
    """音声合成マネージャー"""
    
    def __init__(self):
        self.synthesizer = self._create_synthesizer()
        self.logger = logging.getLogger(__name__)
    
    def _create_synthesizer(self) -> VoiceSynthesizer:
        """設定に基づいて音声合成エンジンを作成"""
        engine = config.voice_engine.lower()
        
        if engine == "voicevox":
            return VoicevoxVoiceSynthesizer()
        elif engine == "elevenlabs":
            return ElevenLabsVoiceSynthesizer()
        else:  # デフォルトはpyttsx3
            return PyttsxVoiceSynthesizer()
    
    async def speak(self, text: str, emotion: str = "neutral") -> bool:
        """テキストを音声で読み上げ"""
        try:
            self.logger.info(f"音声合成開始: {text[:50]}...")
            success = await self.synthesizer.synthesize(text, emotion)
            
            if success:
                self.logger.info("音声合成完了")
            else:
                self.logger.warning("音声合成失敗")
            
            return success
            
        except Exception as e:
            self.logger.error(f"音声合成マネージャーエラー: {e}")
            return False

# 使用例
async def test_voice_synthesis():
    """音声合成のテスト"""
    manager = VoiceSynthesisManager()
    
    test_phrases = [
        ("こんにちは！私はAI美少女です♪", "happy"),
        ("今日はとても嬉しいです！", "excited"),
        ("少し恥ずかしいです...", "shy"),
        ("ありがとうございます", "calm"),
        ("愛してます♡", "love")
    ]
    
    for text, emotion in test_phrases:
        print(f"再生中: {text} (感情: {emotion})")
        await manager.speak(text, emotion)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_voice_synthesis())