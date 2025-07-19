#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VRChat AI美少女システム起動スクリプト
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "AI"))

from ai_dialogue_system import AIDialogueSystem
from config import config, validate_config, print_config

def setup_logging():
    """ログ設定"""
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

async def main():
    """メイン関数"""
    print("🌸 VRChat AI美少女システム 🌸")
    print("=" * 40)
    
    # 設定の検証
    errors = validate_config()
    if errors:
        print("❌ 設定エラーが見つかりました:")
        for error in errors:
            print(f"   - {error}")
        print("\n設定を確認してください。")
        return
    
    # 設定の表示
    print_config()
    
    # ログ設定
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # AIシステムの初期化
        logger.info("AIシステムを初期化中...")
        ai_system = AIDialogueSystem(
            vrchat_osc_ip=config.vrchat_osc_ip,
            vrchat_osc_port=config.vrchat_osc_port
        )
        
        print("✅ AIシステムの初期化完了")
        print("\n使用方法:")
        print("- テキスト入力で対話")
        print("- 'quit' または 'exit' で終了")
        print("- 'help' でヘルプ表示")
        print("-" * 40)
        
        # 対話ループ
        while True:
            try:
                user_input = input("\n💬 あなた: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', '終了']:
                    print("👋 さようなら！")
                    break
                
                if user_input.lower() == 'help':
                    show_help()
                    continue
                
                if user_input.lower() == 'status':
                    show_status(ai_system)
                    continue
                
                if user_input.lower().startswith('config'):
                    handle_config_command(user_input, ai_system)
                    continue
                
                # AI応答の生成
                logger.info(f"ユーザー入力: {user_input}")
                response = await ai_system.process_input(user_input)
                
                # 応答の表示
                print(f"🤖 AI: {response.text}")
                print(f"   感情: {response.emotion.value} | "
                      f"ジェスチャー: {response.gesture} | "
                      f"親密度: {response.intimacy_level:.2f}")
                
                # 音声出力
                if hasattr(ai_system, 'speak'):
                    ai_system.speak(response.text)
                
                logger.info(f"AI応答: {response.text}")
                
            except KeyboardInterrupt:
                print("\n\n👋 システムを終了します...")
                break
            except Exception as e:
                logger.error(f"エラーが発生しました: {e}")
                print(f"❌ エラー: {e}")
    
    except Exception as e:
        logger.error(f"システム初期化エラー: {e}")
        print(f"❌ システム初期化エラー: {e}")

def show_help():
    """ヘルプを表示"""
    help_text = """
📖 ヘルプ

基本コマンド:
  help     - このヘルプを表示
  status   - システム状態を表示
  quit     - システムを終了

設定コマンド:
  config show              - 現在の設定を表示
  config personality       - 性格設定を表示
  config intimacy <値>     - 親密度を設定 (0.0-1.0)

対話のコツ:
  - 自然な日本語で話しかけてください
  - 感情を込めた表現をすると、AIも感情豊かに応答します
  - 継続的な対話で親密度が上がります

VRChat連携:
  - VRChatでOSCを有効にしてください
  - アバターにAIコントローラーを設定してください
  - リアルタイムで感情とジェスチャーが反映されます
"""
    print(help_text)

def show_status(ai_system):
    """システム状態を表示"""
    print("\n📊 システム状態")
    print(f"感情状態: {ai_system.emotion_state.value}")
    print(f"親密度: {ai_system.intimacy_level:.2f}")
    print(f"会話履歴: {len(ai_system.conversation_history)}件")
    print(f"OSC接続: {ai_system.osc_client._sock is not None}")
    
    print("\n性格特性:")
    for trait, value in ai_system.personality_traits.items():
        bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
        print(f"  {trait:12}: {bar} {value:.1f}")

def handle_config_command(command, ai_system):
    """設定コマンドを処理"""
    parts = command.split()
    
    if len(parts) == 2 and parts[1] == "show":
        print_config()
    
    elif len(parts) == 2 and parts[1] == "personality":
        print("\n🎭 性格設定:")
        for trait, value in ai_system.personality_traits.items():
            print(f"  {trait}: {value}")
    
    elif len(parts) == 3 and parts[1] == "intimacy":
        try:
            new_intimacy = float(parts[2])
            if 0.0 <= new_intimacy <= 1.0:
                ai_system.intimacy_level = new_intimacy
                print(f"✅ 親密度を {new_intimacy} に設定しました")
            else:
                print("❌ 親密度は 0.0-1.0 の範囲で指定してください")
        except ValueError:
            print("❌ 無効な数値です")
    
    else:
        print("❌ 無効な設定コマンドです。'help' でヘルプを確認してください。")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 システムを終了しました")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        logging.error(f"予期しないエラー: {e}", exc_info=True)