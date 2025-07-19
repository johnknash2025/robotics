#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VRChat AI美少女システム設定ファイル
"""

import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AIConfig:
    """AI設定クラス"""
    
    # OpenAI設定
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-3.5-turbo"
    max_tokens: int = 150
    temperature: float = 0.8
    
    # VRChat OSC設定
    vrchat_osc_ip: str = "127.0.0.1"
    vrchat_osc_port: int = 9000
    
    # 音声設定
    voice_engine: str = "pyttsx3"  # "pyttsx3", "voicevox", "elevenlabs"
    voice_rate: int = 150
    voice_volume: float = 0.8
    
    # VOICEVOX設定（使用する場合）
    voicevox_url: str = "http://localhost:50021"
    voicevox_speaker_id: int = 1  # ずんだもん
    
    # ElevenLabs設定（使用する場合）
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel
    
    # 性格設定
    personality_traits: Dict[str, float] = None
    
    # 対話設定
    max_conversation_history: int = 20
    response_delay: float = 1.0  # 応答遅延（秒）
    
    # 感情設定
    emotion_decay_rate: float = 0.1  # 感情の減衰率
    intimacy_growth_rate: float = 0.01  # 親密度の成長率
    
    # ログ設定
    log_level: str = "INFO"
    log_file: str = "ai_dialogue.log"
    
    def __post_init__(self):
        if self.personality_traits is None:
            self.personality_traits = {
                "friendliness": 0.8,    # 親しみやすさ
                "shyness": 0.6,         # 恥ずかしがり
                "playfulness": 0.7,     # 遊び心
                "intelligence": 0.9,    # 知性
                "curiosity": 0.8,       # 好奇心
                "empathy": 0.9,         # 共感性
                "humor": 0.6,           # ユーモア
                "romanticism": 0.5      # ロマンチック
            }

# グローバル設定インスタンス
config = AIConfig()

# 設定の検証
def validate_config():
    """設定の妥当性をチェック"""
    errors = []
    
    if not config.openai_api_key and config.voice_engine != "local":
        errors.append("OpenAI APIキーが設定されていません")
    
    if config.vrchat_osc_port < 1024 or config.vrchat_osc_port > 65535:
        errors.append("OSCポート番号が無効です")
    
    if not (0.0 <= config.temperature <= 2.0):
        errors.append("temperature値が範囲外です (0.0-2.0)")
    
    for trait, value in config.personality_traits.items():
        if not (0.0 <= value <= 1.0):
            errors.append(f"性格特性 '{trait}' の値が範囲外です (0.0-1.0)")
    
    return errors

# 設定のロード
def load_config_from_file(file_path: str = "config.json"):
    """JSONファイルから設定をロード"""
    import json
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 設定を更新
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        print(f"設定ファイル '{file_path}' をロードしました")
        
    except FileNotFoundError:
        print(f"設定ファイル '{file_path}' が見つかりません。デフォルト設定を使用します。")
    except json.JSONDecodeError as e:
        print(f"設定ファイルの解析エラー: {e}")

# 設定の保存
def save_config_to_file(file_path: str = "config.json"):
    """設定をJSONファイルに保存"""
    import json
    from dataclasses import asdict
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(config), f, indent=2, ensure_ascii=False)
        
        print(f"設定を '{file_path}' に保存しました")
        
    except Exception as e:
        print(f"設定保存エラー: {e}")

# 環境変数から設定を更新
def update_from_env():
    """環境変数から設定を更新"""
    env_mappings = {
        "VRCHAT_OSC_IP": "vrchat_osc_ip",
        "VRCHAT_OSC_PORT": "vrchat_osc_port",
        "VOICE_ENGINE": "voice_engine",
        "OPENAI_MODEL": "openai_model",
        "VOICEVOX_URL": "voicevox_url",
        "LOG_LEVEL": "log_level"
    }
    
    for env_var, config_attr in env_mappings.items():
        value = os.getenv(env_var)
        if value:
            # 型変換
            if config_attr.endswith("_port"):
                value = int(value)
            elif config_attr.endswith("_rate") or config_attr.endswith("_volume"):
                value = float(value)
            
            setattr(config, config_attr, value)

# 初期化時に環境変数から更新
update_from_env()

# デバッグ用の設定表示
def print_config():
    """現在の設定を表示"""
    print("=== AI美少女システム設定 ===")
    print(f"OpenAI Model: {config.openai_model}")
    print(f"VRChat OSC: {config.vrchat_osc_ip}:{config.vrchat_osc_port}")
    print(f"Voice Engine: {config.voice_engine}")
    print(f"Log Level: {config.log_level}")
    print("性格特性:")
    for trait, value in config.personality_traits.items():
        print(f"  {trait}: {value}")
    print("=" * 30)

if __name__ == "__main__":
    # 設定の検証
    errors = validate_config()
    if errors:
        print("設定エラー:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("設定は正常です")
    
    # 設定の表示
    print_config()