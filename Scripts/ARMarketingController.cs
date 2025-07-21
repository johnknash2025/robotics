

using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using VRC.SDKBase;
using VRC.Udon;
using VRC.Udon.Common.Interfaces;
using VRC.SDK3.Components;
using VRC.SDK3.Video.Components;
using UdonSharp;

namespace ARMarketing
{
    [UdonBehaviourSyncMode(BehaviourSyncMode.None)]
    public class ARMarketingController : UdonSharpBehaviour
    {
        [Header("AR Marketing Settings")]
        public GameObject floatingBannerPrefab;
        public GameObject productShowcasePrefab;
        public GameObject socialProofPrefab;
        public Transform arContentParent;
        
        [Header("OSC Settings")]
        public OSCReceiver oscReceiver;
        public string oscAddress = "/ar/marketing";
        
        [Header("Animation Settings")]
        public float fadeInDuration = 1.0f;
        public float displayDuration = 5.0f;
        public AnimationCurve fadeCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
        
        private Dictionary<string, GameObject> activeARElements = new Dictionary<string, GameObject>();
        private Queue<ARMessage> messageQueue = new Queue<ARMessage>();
        private bool isProcessingQueue = false;
        
        [System.Serializable]
        public class ARMessage
        {
            public string userId;
            public string elementType;
            public string content;
            public Vector3 position;
            public Vector3 rotation;
            public Vector3 scale;
            public float duration;
            public Dictionary<string, string> metadata;
        }
        
        void Start()
        {
            if (oscReceiver == null)
            {
                oscReceiver = GetComponent<OSCReceiver>();
            }
            
            if (oscReceiver != null)
            {
                oscReceiver.SetAddress(oscAddress);
                oscReceiver.AddListener(OnOSCMessageReceived);
            }
            
            Debug.Log("[AR Marketing] Controller initialized");
        }
        
        public void OnOSCMessageReceived(OSCMessage message)
        {
            if (message.address == oscAddress)
            {
                ProcessOSCData(message);
            }
        }
        
        private void ProcessOSCData(OSCMessage message)
        {
            try
            {
                ARMessage arMessage = new ARMessage();
                
                // OSCメッセージからAR要素データを抽出
                foreach (var data in message.data)
                {
                    if (data is string strData)
                    {
                        ParseARMessage(strData, arMessage);
                    }
                }
                
                messageQueue.Enqueue(arMessage);
                
                if (!isProcessingQueue)
                {
                    StartCoroutine(ProcessMessageQueue());
                }
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[AR Marketing] Error processing OSC: {e.Message}");
            }
        }
        
        private void ParseARMessage(string data, ARMessage arMessage)
        {
            // JSON形式のデータを解析
            try
            {
                var jsonData = JsonUtility.FromJson<Dictionary<string, object>>(data);
                
                arMessage.userId = jsonData.ContainsKey("user_id") ? jsonData["user_id"].ToString() : "";
                arMessage.elementType = jsonData.ContainsKey("element_type") ? jsonData["element_type"].ToString() : "floating_banner";
                arMessage.content = jsonData.ContainsKey("content") ? jsonData["content"].ToString() : "";
                
                if (jsonData.ContainsKey("position"))
                {
                    var posData = JsonUtility.FromJson<Vector3Data>(jsonData["position"].ToString());
                    arMessage.position = new Vector3(posData.x, posData.y, posData.z);
                }
                
                arMessage.duration = jsonData.ContainsKey("duration") ? float.Parse(jsonData["duration"].ToString()) : displayDuration;
            }
            catch
            {
                // フォールバック処理
                arMessage.content = data;
                arMessage.elementType = "floating_banner";
            }
        }
        
        private IEnumerator ProcessMessageQueue()
        {
            isProcessingQueue = true;
            
            while (messageQueue.Count > 0)
            {
                ARMessage arMessage = messageQueue.Dequeue();
                yield return StartCoroutine(DisplayARElement(arMessage));
            }
            
            isProcessingQueue = false;
        }
        
        private IEnumerator DisplayARElement(ARMessage arMessage)
        {
            GameObject arElement = null;
            
            switch (arMessage.elementType)
            {
                case "floating_banner":
                    arElement = CreateFloatingBanner(arMessage);
                    break;
                case "product_showcase":
                    arElement = CreateProductShowcase(arMessage);
                    break;
                case "social_proof":
                    arElement = CreateSocialProof(arMessage);
                    break;
                default:
                    arElement = CreateGenericARElement(arMessage);
                    break;
            }
            
            if (arElement != null)
            {
                string elementId = System.Guid.NewGuid().ToString();
                activeARElements[elementId] = arElement;
                
                // フェードインアニメーション
                yield return StartCoroutine(FadeInElement(arElement));
                
                // 表示期間待機
                yield return new WaitForSeconds(arMessage.duration);
                
                // フェードアウトアニメーション
                yield return StartCoroutine(FadeOutElement(arElement));
                
                // 要素を削除
                if (activeARElements.ContainsKey(elementId))
                {
                    activeARElements.Remove(elementId);
                    Destroy(arElement);
                }
            }
        }
        
        private GameObject CreateFloatingBanner(ARMessage arMessage)
        {
            if (floatingBannerPrefab == null) return null;
            
            GameObject banner = Instantiate(floatingBannerPrefab, arContentParent);
            banner.transform.position = arMessage.position;
            
            // テキスト設定
            var textMesh = banner.GetComponentInChildren<TMPro.TextMeshProUGUI>();
            if (textMesh != null)
            {
                textMesh.text = arMessage.content;
            }
            
            // 初期状態を透明に
            SetAlpha(banner, 0f);
            
            return banner;
        }
        
        private GameObject CreateProductShowcase(ARMessage arMessage)
        {
            if (productShowcasePrefab == null) return null;
            
            GameObject showcase = Instantiate(productShowcasePrefab, arContentParent);
            showcase.transform.position = arMessage.position;
            
            // 製品情報を設定
            var productDisplay = showcase.GetComponent<ProductDisplayController>();
            if (productDisplay != null)
            {
                productDisplay.SetProductData(arMessage.content, arMessage.metadata);
            }
            
            SetAlpha(showcase, 0f);
            
            return showcase;
        }
        
        private GameObject CreateSocialProof(ARMessage arMessage)
        {
            if (socialProofPrefab == null) return null;
            
            GameObject socialProof = Instantiate(socialProofPrefab, arContentParent);
            socialProof.transform.position = arMessage.position;
            
            // ソーシャルプルーフ情報を設定
            var socialController = socialProof.GetComponent<SocialProofController>();
            if (socialController != null)
            {
                socialController.SetSocialData(arMessage.content);
            }
            
            SetAlpha(socialProof, 0f);
            
            return socialProof;
        }
        
        private GameObject CreateGenericARElement(ARMessage arMessage)
        {
            GameObject genericElement = new GameObject("AR_Element");
            genericElement.transform.SetParent(arContentParent);
            genericElement.transform.position = arMessage.position;
            
            // 基本の3Dテキストを追加
            var textMesh = genericElement.AddComponent<TMPro.TextMeshPro>();
            textMesh.text = arMessage.content;
            textMesh.fontSize = 2f;
            
            return genericElement;
        }
        
        private IEnumerator FadeInElement(GameObject element)
        {
            float elapsed = 0f;
            CanvasGroup canvasGroup = element.GetComponent<CanvasGroup>();
            
            if (canvasGroup == null)
            {
                canvasGroup = element.AddComponent<CanvasGroup>();
            }
            
            while (elapsed < fadeInDuration)
            {
                elapsed += Time.deltaTime;
                float alpha = fadeCurve.Evaluate(elapsed / fadeInDuration);
                canvasGroup.alpha = alpha;
                yield return null;
            }
            
            canvasGroup.alpha = 1f;
        }
        
        private IEnumerator FadeOutElement(GameObject element)
        {
            float elapsed = 0f;
            CanvasGroup canvasGroup = element.GetComponent<CanvasGroup>();
            
            if (canvasGroup == null)
            {
                canvasGroup = element.AddComponent<CanvasGroup>();
            }
            
            while (elapsed < fadeInDuration)
            {
                elapsed += Time.deltaTime;
                float alpha = 1f - fadeCurve.Evaluate(elapsed / fadeInDuration);
                canvasGroup.alpha = alpha;
                yield return null;
            }
            
            canvasGroup.alpha = 0f;
        }
        
        private void SetAlpha(GameObject obj, float alpha)
        {
            CanvasGroup canvasGroup = obj.GetComponent<CanvasGroup>();
            if (canvasGroup == null)
            {
                canvasGroup = obj.AddComponent<CanvasGroup>();
            }
            canvasGroup.alpha = alpha;
        }
        
        // ユーザーがAR要素をクリックしたとき
        public void OnARElementClicked(string elementId)
        {
            if (activeARElements.ContainsKey(elementId))
            {
                GameObject element = activeARElements[elementId];
                
                // クリックイベントを処理
                var clickable = element.GetComponent<IClickableARElement>();
                if (clickable != null)
                {
                    clickable.OnClicked();
                }
                
                // OSCでクリックイベントを送信
                SendClickEvent(elementId);
            }
        }
        
        private void SendClickEvent(string elementId)
        {
            if (oscReceiver != null)
            {
                OSCMessage message = new OSCMessage("/ar/element_clicked");
                message.Add(elementId);
                oscReceiver.Send(message);
            }
        }
        
        // 全てのAR要素をクリア
        public void ClearAllARElements()
        {
            foreach (var kvp in activeARElements)
            {
                Destroy(kvp.Value);
            }
            activeARElements.Clear();
        }
        
        // 特定のユーザーのAR要素のみを表示
        public void ShowElementsForUser(string userId)
        {
            // ユーザーIDに基づいてフィルタリング
            foreach (var element in activeARElements.Values)
            {
                var userFilter = element.GetComponent<UserSpecificARElement>();
                if (userFilter != null)
                {
                    userFilter.SetVisibility(userId);
                }
            }
        }
    }
    
    [System.Serializable]
    public class Vector3Data
    {
        public float x;
        public float y;
        public float z;
    }
    
    public interface IClickableARElement
    {
        void OnClicked();
    }
    
    public interface UserSpecificARElement
    {
        void SetVisibility(string userId);
    }
}

