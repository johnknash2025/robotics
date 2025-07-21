


using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine.UI;
using VRC.SDKBase;
using VRC.Udon;
using UdonSharp;

namespace ARMarketing
{
    [UdonBehaviourSyncMode(BehaviourSyncMode.None)]
    public class ProductDisplayController : UdonSharpBehaviour
    {
        [Header("Product Display Settings")]
        public GameObject productModel;
        public TextMeshProUGUI productNameText;
        public TextMeshProUGUI productDescriptionText;
        public TextMeshProUGUI priceText;
        public Image productImage;
        public Button actionButton;
        
        [Header("Animation Settings")]
        public float rotationSpeed = 30f;
        public float hoverHeight = 0.5f;
        public float hoverSpeed = 2f;
        
        [Header("Interaction Settings")]
        public GameObject detailsPanel;
        public Button closeButton;
        public Button purchaseButton;
        
        private ProductData currentProduct;
        private bool isExpanded = false;
        private Vector3 originalPosition;
        private Quaternion originalRotation;
        
        [System.Serializable]
        public class ProductData
        {
            public string id;
            public string name;
            public string description;
            public float price;
            public string imageUrl;
            public string modelPath;
            public Dictionary<string, string> features;
            public string purchaseUrl;
        }
        
        void Start()
        {
            originalPosition = transform.position;
            originalRotation = transform.rotation;
            
            if (actionButton != null)
            {
                actionButton.onClick.AddListener(OnActionButtonClicked);
            }
            
            if (closeButton != null)
            {
                closeButton.onClick.AddListener(OnCloseButtonClicked);
            }
            
            if (purchaseButton != null)
            {
                purchaseButton.onClick.AddListener(OnPurchaseButtonClicked);
            }
            
            if (detailsPanel != null)
            {
                detailsPanel.SetActive(false);
            }
            
            SetupInitialState();
        }
        
        public void SetProductData(string productJson, Dictionary<string, string> metadata)
        {
            try
            {
                currentProduct = JsonUtility.FromJson<ProductData>(productJson);
                UpdateProductDisplay();
            }
            catch
            {
                // フォールバック: メタデータから直接設定
                if (metadata != null)
                {
                    currentProduct = new ProductData
                    {
                        name = metadata.ContainsKey("name") ? metadata["name"] : "Product",
                        description = metadata.ContainsKey("description") ? metadata["description"] : "No description available",
                        price = metadata.ContainsKey("price") ? float.Parse(metadata["price"]) : 0f
                    };
                    UpdateProductDisplay();
                }
            }
        }
        
        private void UpdateProductDisplay()
        {
            if (currentProduct == null) return;
            
            if (productNameText != null)
            {
                productNameText.text = currentProduct.name;
            }
            
            if (productDescriptionText != null)
            {
                productDescriptionText.text = currentProduct.description;
            }
            
            if (priceText != null)
            {
                priceText.text = $"¥{currentProduct.price:N0}";
            }
            
            if (productImage != null && !string.IsNullOrEmpty(currentProduct.imageUrl))
            {
                StartCoroutine(LoadProductImage(currentProduct.imageUrl));
            }
            
            if (productModel != null && !string.IsNullOrEmpty(currentProduct.modelPath))
            {
                StartCoroutine(LoadProductModel(currentProduct.modelPath));
            }
        }
        
        private IEnumerator LoadProductImage(string imageUrl)
        {
            // 画像読み込みの実装
            // 実際の実装では、VRChatの制限に注意が必要
            yield return null;
            
            // デフォルト画像を設定
            if (productImage != null)
            {
                productImage.color = Color.white;
            }
        }
        
        private IEnumerator LoadProductModel(string modelPath)
        {
            // 3Dモデル読み込みの実装
            yield return null;
            
            // デフォルトモデルを回転させる
            if (productModel != null)
            {
                productModel.SetActive(true);
            }
        }
        
        private void SetupInitialState()
        {
            // 初期アニメーション設定
            if (productModel != null)
            {
                productModel.transform.localPosition = Vector3.zero;
                productModel.transform.localRotation = Quaternion.identity;
            }
        }
        
        void Update()
        {
            if (productModel != null && productModel.activeSelf)
            {
                // 製品モデルを回転させる
                productModel.transform.Rotate(Vector3.up, rotationSpeed * Time.deltaTime);
                
                // ホバリング効果
                float hoverOffset = Mathf.Sin(Time.time * hoverSpeed) * hoverHeight;
                productModel.transform.localPosition = new Vector3(0, hoverOffset, 0);
            }
        }
        
        public void OnActionButtonClicked()
        {
            if (!isExpanded)
            {
                ExpandProductDetails();
            }
            else
            {
                CollapseProductDetails();
            }
        }
        
        private void ExpandProductDetails()
        {
            isExpanded = true;
            
            if (detailsPanel != null)
            {
                detailsPanel.SetActive(true);
                
                // 拡大アニメーション
                StartCoroutine(AnimateExpansion());
            }
            
            // OSCで拡張イベントを送信
            SendInteractionEvent("product_expanded", currentProduct.id);
        }
        
        private void CollapseProductDetails()
        {
            isExpanded = false;
            
            if (detailsPanel != null)
            {
                StartCoroutine(AnimateCollapse());
            }
            
            SendInteractionEvent("product_collapsed", currentProduct.id);
        }
        
        public void OnCloseButtonClicked()
        {
            CollapseProductDetails();
        }
        
        public void OnPurchaseButtonClicked()
        {
            // 購入アクション
            SendInteractionEvent("purchase_clicked", currentProduct.id);
            
            // 外部URLを開く（VRChatの制限に注意）
            if (!string.IsNullOrEmpty(currentProduct.purchaseUrl))
            {
                Application.OpenURL(currentProduct.purchaseUrl);
            }
        }
        
        private IEnumerator AnimateExpansion()
        {
            Vector3 startScale = transform.localScale;
            Vector3 targetScale = startScale * 1.5f;
            float elapsed = 0f;
            float duration = 0.3f;
            
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / duration;
                transform.localScale = Vector3.Lerp(startScale, targetScale, t);
                yield return null;
            }
            
            transform.localScale = targetScale;
        }
        
        private IEnumerator AnimateCollapse()
        {
            Vector3 startScale = transform.localScale;
            Vector3 targetScale = Vector3.one;
            float elapsed = 0f;
            float duration = 0.3f;
            
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / duration;
                transform.localScale = Vector3.Lerp(startScale, targetScale, t);
                yield return null;
            }
            
            transform.localScale = targetScale;
            
            if (detailsPanel != null)
            {
                detailsPanel.SetActive(false);
            }
        }
        
        private void SendInteractionEvent(string eventType, string productId)
        {
            // OSCメッセージを送信
            if (Networking.LocalPlayer != null)
            {
                // インタラクションログを送信
                Debug.Log($"[AR Marketing] Product interaction: {eventType} for {productId}");
            }
        }
        
        // ユーザーが近づいたときの処理
        public void OnUserApproach(VRCPlayerApi player)
        {
            if (player.isLocal) return;
            
            // 近くのユーザーに対して特別な表示
            StartCoroutine(ShowSpecialOffer());
        }
        
        private IEnumerator ShowSpecialOffer()
        {
            // 特別オファーを表示
            if (priceText != null)
            {
                string originalText = priceText.text;
                priceText.text = "SPECIAL OFFER!";
                priceText.color = Color.red;
                
                yield return new WaitForSeconds(3f);
                
                priceText.text = originalText;
                priceText.color = Color.white;
            }
        }
        
        // 製品をハイライト
        public void HighlightProduct(bool highlight)
        {
            if (productModel != null)
            {
                var renderer = productModel.GetComponent<Renderer>();
                if (renderer != null)
                {
                    if (highlight)
                    {
                        renderer.material.EnableKeyword("_EMISSION");
                        renderer.material.SetColor("_EmissionColor", Color.yellow * 0.5f);
                    }
                    else
                    {
                        renderer.material.DisableKeyword("_EMISSION");
                    }
                }
            }
        }
    }
}


