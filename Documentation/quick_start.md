# 🌸 VRChat AI美少女 クイックスタートガイド

## 🚀 最速セットアップ（5分で開始）

### 1. 必要なソフトウェアのインストール

```bash
# Python依存関係のインストール
pip install openai python-osc SpeechRecognition pyttsx3 pygame

# または
pip install -r AI/requirements.txt
```

### 2. 基本テストの実行

```bash
# システムテスト
python3 tmp_rovodev_test_system.py

# AIシステムの起動
python3 Scripts/launch_ai_system.py
```

### 3. VRChat設定

1. **VRChatでOSCを有効化**
   - VRChatの起動オプションに追加: `--enable-sdk-log-levels --enable-debug-gui`

2. **アバターの準備**
   - VRoid Studioで美少女アバターを作成
   - または既存のアバターを使用

### 4. Unity設定（簡易版）

1. **新しいUnityプロジェクト作成**
2. **VRChat SDK3をインポート**
3. **スクリプトを配置**
   - `Scripts/VRChatAIController.cs` をアバターに
   - `Scripts/OSCReceiver.cs` をシーンに

## 🎮 使用方法

### 基本的な対話
```
💬 あなた: こんにちは
🤖 AI: こんにちは！お会いできて嬉しいです♪
   感情: happy | ジェスチャー: wave_happy | 親密度: 0.01
```

### コマンド
- `help` - ヘルプ表示
- `status` - システム状態確認
- `config show` - 設定表示
- `quit` - 終了

## 🔧 カスタマイズ

### 性格の調整
`AI/config.py`を編集:
```python
personality_traits = {
    "friendliness": 0.9,  # より親しみやすく
    "shyness": 0.3,       # 恥ずかしがりを減らす
    "playfulness": 0.8,   # より遊び心を
    "intelligence": 0.9   # 知性レベル
}
```

### 音声エンジンの変更
```python
# config.py
voice_engine = "voicevox"  # または "elevenlabs", "pyttsx3"
```

## 🎭 感情とジェスチャー

### 利用可能な感情
- `happy` - 嬉しい
- `excited` - 興奮
- `shy` - 恥ずかしい
- `love` - 愛情
- `calm` - 落ち着いている
- `sad` - 悲しい
- `angry` - 怒り
- `surprised` - 驚き

### ジェスチャー
- `wave_happy` - 嬉しそうに手を振る
- `heart_hands` - ハートを作る
- `cover_face` - 顔を隠す（恥ずかしがり）
- `jump_excited` - 興奮して飛び跳ねる
- `gentle_nod` - 優しくうなずく

## 🔗 VRChat連携

### OSCパラメータ
```
/avatar/parameters/emotion     - 感情状態
/avatar/parameters/gesture     - ジェスチャー
/avatar/parameters/intimacy    - 親密度 (0.0-1.0)
/avatar/parameters/voice_tone  - 音声トーン (0.0-1.0)
```

### アニメーターパラメータ
```
Emotion (Float): -2.0 to 3.0
Gesture (Float): 0.0 to 6.0
Intimacy (Float): 0.0 to 1.0
VoiceTone (Float): 0.0 to 1.0
```

## 🐛 トラブルシューティング

### よくある問題

**Q: OSC通信ができない**
```bash
# ポート確認
netstat -an | grep 9000

# ファイアウォール確認
sudo ufw allow 9000
```

**Q: 音声が出ない**
```bash
# 音声デバイス確認
python3 -c "import pyttsx3; engine = pyttsx3.init(); voices = engine.getProperty('voices'); [print(v.name) for v in voices]"
```

**Q: AIが応答しない**
- OpenAI APIキーを確認
- インターネット接続を確認
- ログファイル `ai_dialogue.log` を確認

### ログの確認
```bash
tail -f ai_dialogue.log
```

## 🎨 高度なカスタマイズ

### 新しい感情の追加
1. `ai_dialogue_system.py`の`EmotionState`に追加
2. `VRChatAIController.cs`の感情マッピングに追加
3. アニメーターに対応するアニメーションを追加

### カスタム音声の使用
```python
# voice_synthesis.py
class CustomVoiceSynthesizer(VoiceSynthesizer):
    async def synthesize(self, text: str, emotion: str = "neutral") -> bool:
        # カスタム音声合成ロジック
        pass
```

### 外部APIとの連携
```python
# 天気情報、ニュースなどの外部データを取得
async def get_weather_info():
    # 天気API呼び出し
    pass
```

## 📚 参考リンク

- [VRChat OSC Documentation](https://docs.vrchat.com/docs/osc-overview)
- [Unity Animator Controller](https://docs.unity3d.com/Manual/class-AnimatorController.html)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [VOICEVOX](https://voicevox.hiroshiba.jp/)

## 💝 コミュニティ

- GitHub Issues: バグ報告・機能要望
- Discord: リアルタイムサポート
- Twitter: 最新情報・アップデート

---

**楽しいVRChatライフを！** 🌸✨