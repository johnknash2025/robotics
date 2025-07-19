# VRChat AI美少女対話相手プロジェクト

VRChatで自律的に動いて話して触れる美少女AI対話相手を作成するプロジェクトです。

## 主要機能
- 自然言語での対話
- 自律的なモーション・ジェスチャー
- 音声合成による発話
- 触覚インタラクション
- 感情表現

## 技術スタック
- Unity 2022.3 LTS
- VRChat SDK3
- Python (AI対話システム)
- OpenAI API / ローカルLLM
- VOICEVOX / 他の音声合成
- OSC (Open Sound Control) 通信

## プロジェクト構造
```
├── Unity/                 # Unityプロジェクト
├── AI/                   # AI対話システム
├── Models/               # 3Dモデルとアニメーション
├── Scripts/              # 各種スクリプト
└── Documentation/        # ドキュメント
```

## セットアップ手順
1. Unity環境の準備
2. VRChat SDKのインポート
3. AI対話システムの構築
4. OSC通信の設定
5. アバターの作成とアップロード