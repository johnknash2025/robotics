# VRChat AI美少女セットアップガイド

## 必要な環境

### Unity環境
- Unity 2022.3 LTS
- VRChat SDK3 (Avatars)
- UdonSharp

### Python環境
- Python 3.8以上
- 必要なライブラリ（requirements.txtを参照）

### その他
- VRChatアカウント
- OpenAI APIキー（またはローカルLLM）
- マイク（音声入力用）

## セットアップ手順

### 1. Unity プロジェクトの準備

1. Unity Hub で新しい3Dプロジェクトを作成
2. VRChat SDK3をインポート
   ```
   https://vrchat.com/home/download
   ```
3. UdonSharpをインポート
   ```
   https://github.com/vrchat-community/UdonSharp
   ```

### 2. アバターの準備

#### 推奨3Dモデル
- VRoid Studio で作成
- Booth で購入
- 自作モデル

#### 必要なコンポーネント
- Humanoid リグ
- 表情用ブレンドシェイプ
- アニメーターコントローラー

### 3. アニメーターコントローラーの設定

```
Parameters:
- Emotion (Float): 感情状態 (-2.0 to 3.0)
- Gesture (Float): ジェスチャー (0.0 to 6.0)
- Intimacy (Float): 親密度 (0.0 to 1.0)
- VoiceTone (Float): 音声トーン (0.0 to 1.0)
```

#### レイヤー構成
1. Base Layer: 基本アニメーション
2. Emotion Layer: 表情制御
3. Gesture Layer: ジェスチャー
4. Additive Layer: 追加エフェクト

### 4. スクリプトの配置

1. `VRChatAIController.cs` をアバターのルートオブジェクトにアタッチ
2. `OSCReceiver.cs` をシーン内の空のGameObjectにアタッチ
3. 必要なコンポーネントを設定:
   - Animator
   - AudioSource
   - ParticleSystem
   - SkinnedMeshRenderer

### 5. Python AI システムの設定

1. 依存関係のインストール:
   ```bash
   pip install -r AI/requirements.txt
   ```

2. 環境変数の設定:
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```

3. 設定ファイルの作成:
   ```python
   # config.py
   VRCHAT_OSC_IP = "127.0.0.1"
   VRCHAT_OSC_PORT = 9000
   AI_MODEL = "gpt-3.5-turbo"
   VOICE_ENGINE = "pyttsx3"  # または "voicevox"
   ```

### 6. VRChat OSC設定

1. VRChatでOSCを有効化:
   - Launch Options: `--enable-sdk-log-levels --enable-debug-gui --enable-udon-debug-logging`

2. OSCアプリケーションの設定:
   - ポート: 9000 (受信)
   - ポート: 9001 (送信)

### 7. アバターのアップロード

1. VRChat SDKのControl Panelを開く
2. アバターを設定:
   - Descriptor設定
   - Expression Parameters設定
   - Expression Menu設定

3. Build & Publishでアップロード

## 使用方法

### 1. AIシステムの起動
```bash
cd AI
python ai_dialogue_system.py
```

### 2. VRChatでアバターを着用

### 3. 音声入力またはテキスト入力で対話開始

## トラブルシューティング

### OSC通信が動作しない場合
1. ファイアウォール設定を確認
2. ポート番号が正しいか確認
3. VRChatのOSC設定を確認

### アニメーションが動作しない場合
1. Animator Controllerの設定を確認
2. パラメータ名が一致しているか確認
3. レイヤーの重みを確認

### AI応答が遅い場合
1. OpenAI APIの応答時間を確認
2. ローカルLLMの使用を検討
3. キャッシュ機能の実装

## カスタマイズ

### 性格の調整
`ai_dialogue_system.py`の`personality_traits`を編集:
```python
self.personality_traits = {
    "friendliness": 0.9,  # 親しみやすさ
    "shyness": 0.3,       # 恥ずかしがり
    "playfulness": 0.8,   # 遊び心
    "intelligence": 0.9   # 知性
}
```

### 新しいジェスチャーの追加
1. アニメーターにアニメーションを追加
2. `VRChatAIController.cs`の`ExecuteSpecialGesture`に処理を追加
3. `ai_dialogue_system.py`の`determine_gesture`に条件を追加

### 音声合成の変更
VOICEVOXを使用する場合:
```python
import requests

def speak_with_voicevox(text, speaker_id=1):
    # VOICEVOX APIを使用した音声合成
    pass
```