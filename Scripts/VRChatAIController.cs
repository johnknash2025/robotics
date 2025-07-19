using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using VRC.SDKBase;
using VRC.Udon;
using VRC.SDK3.Components;

/// <summary>
/// VRChat AI美少女コントローラー
/// OSC通信でAIシステムからデータを受信し、アバターの動作を制御
/// </summary>
public class VRChatAIController : UdonSharpBehaviour
{
    [Header("AI設定")]
    public Animator avatarAnimator;
    public AudioSource voiceAudioSource;
    public ParticleSystem emotionParticles;
    
    [Header("感情表現")]
    public Material[] emotionMaterials;
    public SkinnedMeshRenderer faceRenderer;
    
    [Header("ジェスチャー設定")]
    public float gestureTransitionSpeed = 2.0f;
    public Transform[] gestureTargets;
    
    [Header("親密度設定")]
    public float maxIntimacyDistance = 2.0f;
    public GameObject[] intimacyEffects;
    
    // 内部状態
    private string currentEmotion = "calm";
    private string currentGesture = "idle";
    private float intimacyLevel = 0.0f;
    private float voiceTone = 0.5f;
    
    // アニメーションパラメータ
    private readonly string EMOTION_PARAM = "Emotion";
    private readonly string GESTURE_PARAM = "Gesture";
    private readonly string INTIMACY_PARAM = "Intimacy";
    private readonly string VOICE_TONE_PARAM = "VoiceTone";
    
    // プレイヤー検出
    private VRCPlayerApi nearestPlayer;
    private float lastInteractionTime;
    
    void Start()
    {
        InitializeAI();
        StartCoroutine(AIBehaviorLoop());
    }
    
    void InitializeAI()
    {
        // 初期状態の設定
        if (avatarAnimator != null)
        {
            avatarAnimator.SetFloat(EMOTION_PARAM, 0);
            avatarAnimator.SetFloat(GESTURE_PARAM, 0);
            avatarAnimator.SetFloat(INTIMACY_PARAM, 0);
            avatarAnimator.SetFloat(VOICE_TONE_PARAM, 0.5f);
        }
        
        Debug.Log("AI美少女システム初期化完了");
    }
    
    /// <summary>
    /// OSCから感情状態を受信
    /// </summary>
    public void OnEmotionReceived(string emotion)
    {
        currentEmotion = emotion;
        UpdateEmotionDisplay();
        Debug.Log($"感情更新: {emotion}");
    }
    
    /// <summary>
    /// OSCからジェスチャーを受信
    /// </summary>
    public void OnGestureReceived(string gesture)
    {
        currentGesture = gesture;
        PlayGesture(gesture);
        Debug.Log($"ジェスチャー実行: {gesture}");
    }
    
    /// <summary>
    /// OSCから親密度を受信
    /// </summary>
    public void OnIntimacyReceived(float intimacy)
    {
        intimacyLevel = Mathf.Clamp01(intimacy);
        UpdateIntimacyEffects();
        Debug.Log($"親密度更新: {intimacy}");
    }
    
    /// <summary>
    /// OSCから音声トーンを受信
    /// </summary>
    public void OnVoiceToneReceived(float tone)
    {
        voiceTone = Mathf.Clamp01(tone);
        UpdateVoiceParameters();
        Debug.Log($"音声トーン更新: {tone}");
    }
    
    void UpdateEmotionDisplay()
    {
        if (avatarAnimator != null)
        {
            float emotionValue = GetEmotionValue(currentEmotion);
            avatarAnimator.SetFloat(EMOTION_PARAM, emotionValue);
        }
        
        // 表情の変更
        if (faceRenderer != null && emotionMaterials.Length > 0)
        {
            int materialIndex = GetEmotionMaterialIndex(currentEmotion);
            if (materialIndex >= 0 && materialIndex < emotionMaterials.Length)
            {
                faceRenderer.material = emotionMaterials[materialIndex];
            }
        }
        
        // パーティクルエフェクト
        if (emotionParticles != null)
        {
            var main = emotionParticles.main;
            main.startColor = GetEmotionColor(currentEmotion);
            
            if (currentEmotion == "happy" || currentEmotion == "excited")
            {
                if (!emotionParticles.isPlaying)
                    emotionParticles.Play();
            }
            else
            {
                if (emotionParticles.isPlaying)
                    emotionParticles.Stop();
            }
        }
    }
    
    void PlayGesture(string gesture)
    {
        if (avatarAnimator != null)
        {
            float gestureValue = GetGestureValue(gesture);
            avatarAnimator.SetFloat(GESTURE_PARAM, gestureValue);
            
            // ジェスチャーのトリガー
            avatarAnimator.SetTrigger(gesture);
        }
        
        // 特別なジェスチャーの処理
        StartCoroutine(ExecuteSpecialGesture(gesture));
    }
    
    IEnumerator ExecuteSpecialGesture(string gesture)
    {
        switch (gesture)
        {
            case "wave_happy":
                yield return StartCoroutine(WaveGesture());
                break;
            case "heart_hands":
                yield return StartCoroutine(HeartHandsGesture());
                break;
            case "cover_face":
                yield return StartCoroutine(CoverFaceGesture());
                break;
            case "jump_excited":
                yield return StartCoroutine(JumpGesture());
                break;
        }
    }
    
    IEnumerator WaveGesture()
    {
        // 手を振るアニメーション
        for (int i = 0; i < 3; i++)
        {
            // 右手を上げる
            yield return new WaitForSeconds(0.3f);
            // 右手を下げる
            yield return new WaitForSeconds(0.3f);
        }
    }
    
    IEnumerator HeartHandsGesture()
    {
        // ハートの形を作るジェスチャー
        yield return new WaitForSeconds(2.0f);
        
        // ハートパーティクルを生成
        if (emotionParticles != null)
        {
            var shape = emotionParticles.shape;
            shape.shapeType = ParticleSystemShapeType.Circle;
            emotionParticles.Play();
        }
    }
    
    IEnumerator CoverFaceGesture()
    {
        // 顔を隠すジェスチャー（恥ずかしがり）
        yield return new WaitForSeconds(1.5f);
    }
    
    IEnumerator JumpGesture()
    {
        // 興奮して飛び跳ねる
        Vector3 originalPos = transform.position;
        for (int i = 0; i < 2; i++)
        {
            transform.position = originalPos + Vector3.up * 0.2f;
            yield return new WaitForSeconds(0.2f);
            transform.position = originalPos;
            yield return new WaitForSeconds(0.2f);
        }
    }
    
    void UpdateIntimacyEffects()
    {
        if (avatarAnimator != null)
        {
            avatarAnimator.SetFloat(INTIMACY_PARAM, intimacyLevel);
        }
        
        // 親密度に応じたエフェクトの表示
        for (int i = 0; i < intimacyEffects.Length; i++)
        {
            if (intimacyEffects[i] != null)
            {
                float threshold = (float)(i + 1) / intimacyEffects.Length;
                intimacyEffects[i].SetActive(intimacyLevel >= threshold);
            }
        }
    }
    
    void UpdateVoiceParameters()
    {
        if (avatarAnimator != null)
        {
            avatarAnimator.SetFloat(VOICE_TONE_PARAM, voiceTone);
        }
        
        if (voiceAudioSource != null)
        {
            voiceAudioSource.pitch = 0.8f + (voiceTone * 0.4f); // 0.8-1.2の範囲
        }
    }
    
    /// <summary>
    /// AI行動ループ
    /// </summary>
    IEnumerator AIBehaviorLoop()
    {
        while (true)
        {
            // 近くのプレイヤーを検出
            DetectNearbyPlayers();
            
            // 自律的な行動
            if (Time.time - lastInteractionTime > 10.0f)
            {
                PerformIdleBehavior();
            }
            
            // プレイヤーとの距離に基づく反応
            if (nearestPlayer != null)
            {
                ReactToPlayerProximity();
            }
            
            yield return new WaitForSeconds(1.0f);
        }
    }
    
    void DetectNearbyPlayers()
    {
        VRCPlayerApi[] players = new VRCPlayerApi[VRCPlayerApi.GetPlayerCount()];
        VRCPlayerApi.GetPlayers(players);
        
        float nearestDistance = float.MaxValue;
        VRCPlayerApi nearest = null;
        
        foreach (var player in players)
        {
            if (player != null && player.IsValid())
            {
                float distance = Vector3.Distance(transform.position, player.GetPosition());
                if (distance < nearestDistance && distance < maxIntimacyDistance)
                {
                    nearestDistance = distance;
                    nearest = player;
                }
            }
        }
        
        nearestPlayer = nearest;
    }
    
    void ReactToPlayerProximity()
    {
        if (nearestPlayer == null) return;
        
        float distance = Vector3.Distance(transform.position, nearestPlayer.GetPosition());
        
        // プレイヤーの方を向く
        Vector3 lookDirection = (nearestPlayer.GetPosition() - transform.position).normalized;
        lookDirection.y = 0; // Y軸回転のみ
        transform.rotation = Quaternion.Slerp(transform.rotation, 
            Quaternion.LookRotation(lookDirection), Time.deltaTime * 2.0f);
        
        // 距離に応じた反応
        if (distance < 0.5f)
        {
            // 非常に近い - 恥ずかしがる
            OnGestureReceived("cover_face");
            OnEmotionReceived("shy");
        }
        else if (distance < 1.0f)
        {
            // 近い - 嬉しそうにする
            OnEmotionReceived("happy");
        }
    }
    
    void PerformIdleBehavior()
    {
        // アイドル時の自律的な行動
        string[] idleBehaviors = { "look_around", "stretch", "yawn", "gentle_nod" };
        string randomBehavior = idleBehaviors[Random.Range(0, idleBehaviors.Length)];
        
        OnGestureReceived(randomBehavior);
        lastInteractionTime = Time.time;
    }
    
    // ヘルパーメソッド
    float GetEmotionValue(string emotion)
    {
        switch (emotion)
        {
            case "happy": return 1.0f;
            case "sad": return -1.0f;
            case "excited": return 2.0f;
            case "calm": return 0.0f;
            case "surprised": return 1.5f;
            case "angry": return -2.0f;
            case "shy": return 0.5f;
            case "love": return 3.0f;
            default: return 0.0f;
        }
    }
    
    int GetEmotionMaterialIndex(string emotion)
    {
        switch (emotion)
        {
            case "happy": return 0;
            case "sad": return 1;
            case "excited": return 2;
            case "calm": return 3;
            case "surprised": return 4;
            case "angry": return 5;
            case "shy": return 6;
            case "love": return 7;
            default: return 3; // calm
        }
    }
    
    Color GetEmotionColor(string emotion)
    {
        switch (emotion)
        {
            case "happy": return Color.yellow;
            case "sad": return Color.blue;
            case "excited": return Color.red;
            case "calm": return Color.green;
            case "surprised": return Color.white;
            case "angry": return Color.red;
            case "shy": return Color.magenta;
            case "love": return Color.red;
            default: return Color.white;
        }
    }
    
    float GetGestureValue(string gesture)
    {
        switch (gesture)
        {
            case "wave_happy": return 1.0f;
            case "heart_hands": return 2.0f;
            case "cover_face": return 3.0f;
            case "jump_excited": return 4.0f;
            case "gentle_nod": return 5.0f;
            case "gasp_surprise": return 6.0f;
            default: return 0.0f; // idle
        }
    }
}