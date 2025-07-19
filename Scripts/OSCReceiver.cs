using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

/// <summary>
/// OSC通信でAIシステムからデータを受信するクラス
/// </summary>
public class OSCReceiver : MonoBehaviour
{
    [Header("OSC設定")]
    public int listenPort = 9000;
    public VRChatAIController aiController;
    
    private UdpClient udpClient;
    private Thread receiveThread;
    private bool isReceiving = false;
    
    void Start()
    {
        StartOSCReceiver();
    }
    
    void StartOSCReceiver()
    {
        try
        {
            udpClient = new UdpClient(listenPort);
            isReceiving = true;
            
            receiveThread = new Thread(ReceiveOSCData);
            receiveThread.IsBackground = true;
            receiveThread.Start();
            
            Debug.Log($"OSCレシーバー開始 - ポート: {listenPort}");
        }
        catch (Exception e)
        {
            Debug.LogError($"OSCレシーバー開始エラー: {e.Message}");
        }
    }
    
    void ReceiveOSCData()
    {
        while (isReceiving)
        {
            try
            {
                IPEndPoint remoteEndPoint = new IPEndPoint(IPAddress.Any, 0);
                byte[] data = udpClient.Receive(ref remoteEndPoint);
                
                // OSCメッセージをパース
                string message = ParseOSCMessage(data);
                
                // メインスレッドで処理するためにキューに追加
                lock (messageQueue)
                {
                    messageQueue.Enqueue(message);
                }
            }
            catch (Exception e)
            {
                if (isReceiving)
                {
                    Debug.LogError($"OSC受信エラー: {e.Message}");
                }
            }
        }
    }
    
    private Queue<string> messageQueue = new Queue<string>();
    
    void Update()
    {
        // メインスレッドでOSCメッセージを処理
        lock (messageQueue)
        {
            while (messageQueue.Count > 0)
            {
                string message = messageQueue.Dequeue();
                ProcessOSCMessage(message);
            }
        }
    }
    
    string ParseOSCMessage(byte[] data)
    {
        // 簡単なOSCメッセージパーサー
        // 実際の実装ではより堅牢なOSCライブラリを使用することを推奨
        try
        {
            string message = Encoding.UTF8.GetString(data);
            return message;
        }
        catch
        {
            return "";
        }
    }
    
    void ProcessOSCMessage(string message)
    {
        if (aiController == null || string.IsNullOrEmpty(message))
            return;
        
        try
        {
            // OSCアドレスパターンに基づいて処理
            if (message.Contains("/avatar/parameters/emotion"))
            {
                string emotion = ExtractStringValue(message);
                aiController.OnEmotionReceived(emotion);
            }
            else if (message.Contains("/avatar/parameters/gesture"))
            {
                string gesture = ExtractStringValue(message);
                aiController.OnGestureReceived(gesture);
            }
            else if (message.Contains("/avatar/parameters/intimacy"))
            {
                float intimacy = ExtractFloatValue(message);
                aiController.OnIntimacyReceived(intimacy);
            }
            else if (message.Contains("/avatar/parameters/voice_tone"))
            {
                float voiceTone = ExtractFloatValue(message);
                aiController.OnVoiceToneReceived(voiceTone);
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"OSCメッセージ処理エラー: {e.Message}");
        }
    }
    
    string ExtractStringValue(string message)
    {
        // OSCメッセージから文字列値を抽出
        // 実装は使用するOSCライブラリに依存
        string[] parts = message.Split(' ');
        if (parts.Length > 1)
        {
            return parts[1].Trim('"');
        }
        return "";
    }
    
    float ExtractFloatValue(string message)
    {
        // OSCメッセージから浮動小数点値を抽出
        string[] parts = message.Split(' ');
        if (parts.Length > 1)
        {
            if (float.TryParse(parts[1], out float value))
            {
                return value;
            }
        }
        return 0.0f;
    }
    
    void OnDestroy()
    {
        StopOSCReceiver();
    }
    
    void OnApplicationQuit()
    {
        StopOSCReceiver();
    }
    
    void StopOSCReceiver()
    {
        isReceiving = false;
        
        if (receiveThread != null && receiveThread.IsAlive)
        {
            receiveThread.Join(1000); // 1秒待機
            if (receiveThread.IsAlive)
            {
                receiveThread.Abort();
            }
        }
        
        if (udpClient != null)
        {
            udpClient.Close();
            udpClient = null;
        }
        
        Debug.Log("OSCレシーバー停止");
    }
}