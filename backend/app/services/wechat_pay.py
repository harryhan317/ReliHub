"""
WeChat Pay Service

Implements WeChat Pay API v3.
Documentation: https://pay.weixin.qq.com/wiki/doc/apiv3/
"""

import base64
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

logger = logging.getLogger(__name__)


class WeChatPayService:
    """
    WeChat Pay Service (API v3)
    
    Features:
    - JSAPI 支付
    - APP 支付
    - Native 支付
    - 退款
    - 订单查询
    """
    
    def __init__(
        self,
        appid: str,
        mchid: str,
        api_key: str,
        private_key: str,
        serial_no: str,
        sandbox: bool = True
    ):
        """
        Initialize WeChat Pay Service
        
        Args:
            appid: 微信公众号/小程序 AppID
            mchid: 商户号
            api_key: API v3 密钥
            private_key: 商户 API 私钥 (PEM 格式)
            serial_no: 商户证书序列号
            sandbox: 是否使用沙箱环境
        """
        self.appid = appid
        self.mchid = mchid
        self.api_key = api_key
        self.private_key = serialization.load_pem_private_key(
            private_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        self.serial_no = serial_no
        self.sandbox = sandbox
        
        self.base_url = (
            "https://api.mch.weixin.qq.com" if not sandbox
            else "https://api.mch.weixin.qq.com/sandboxnew"
        )
        
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=30.0
        )
    
    def _generate_signature(self, message: str) -> str:
        """
        Generate RSA signature
        
        Args:
            message: Message to sign
            
        Returns:
            Base64 encoded signature
        """
        signature = self.private_key.sign(
            message.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    
    def _generate_authorization(
        self,
        method: str,
        url: str,
        body: Optional[str] = None,
        timestamp: Optional[str] = None,
        nonce: Optional[str] = None
    ) -> str:
        """
        Generate WeChat Pay authorization header
        
        Args:
            method: HTTP method
            url: URL path (including query string)
            body: Request body (JSON string)
            timestamp: Timestamp
            nonce: Nonce string
            
        Returns:
            Authorization header value
        """
        import secrets
        import time
        
        if timestamp is None:
            timestamp = str(int(time.time()))
        
        if nonce is None:
            nonce = secrets.token_hex(16)
        
        message = f"{method}\n{url}\n{timestamp}\n{nonce}\n"
        if body:
            message += f"{body}\n"
        else:
            message += "\n"
        
        signature = self._generate_signature(message)
        
        return (
            f'WECHATPAY2-SHA256-RSA2048 '
            f'mchid="{self.mchid}",'
            f'nonce_str="{nonce}",'
            f'signature="{signature}",'
            f'timestamp="{timestamp}",'
            f'serial_no="{self.serial_no}"'
        )
    
    def create_jsapi_order(
        self,
        out_trade_no: str,
        amount: float,
        subject: str,
        openid: str,
        body: Optional[str] = None,
        notify_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create JSAPI payment order
        
        Args:
            out_trade_no: Merchant order number
            amount: Amount (in CNY)
            subject: Order title
            openid: User's WeChat openid
            body: Order description
            notify_url: Payment notification URL
            
        Returns:
            Dict with prepay_id and JSAPI parameters
        """
        url = "/v3/pay/transactions/jsapi"
        
        payload = {
            "appid": self.appid,
            "mchid": self.mchid,
            "description": subject,
            "out_trade_no": out_trade_no,
            "notify_url": notify_url or "https://your-domain.com/api/v1/payment/wechat/notify",
            "amount": {
                "total": int(amount * 100),
                "currency": "CNY"
            },
            "payer": {
                "openid": openid
            }
        }
        
        if body:
            payload["attach"] = body
        
        body_json = json.dumps(payload, ensure_ascii=False)
        authorization = self._generate_authorization("POST", url, body_json)
        
        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = self.client.post(
            url,
            json=payload,
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"WeChat Pay error: {response.status_code} - {response.text}")
            raise Exception(f"WeChat Pay failed: {response.status_code}")
        
        result = response.json()
        prepay_id = result.get("prepay_id")
        
        timestamp = str(int(datetime.now().timestamp()))
        nonce = nonce_str(16)
        
        sign_payload = f"{self.appid}\n{timestamp}\n{nonce}\n{prepay_id}\n"
        sign = self._generate_signature(sign_payload)
        
        return {
            "appId": self.appid,
            "timeStamp": timestamp,
            "nonceStr": nonce,
            "package": f"prepay_id={prepay_id}",
            "signType": "RSA_SHA256",
            "paySign": sign,
            "prepay_id": prepay_id
        }
    
    def create_native_order(
        self,
        out_trade_no: str,
        amount: float,
        subject: str,
        body: Optional[str] = None,
        notify_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create Native payment order (QR code)
        
        Args:
            out_trade_no: Merchant order number
            amount: Amount (in CNY)
            subject: Order title
            body: Order description
            notify_url: Payment notification URL
            
        Returns:
            Dict with code_url (QR code link)
        """
        url = "/v3/pay/transactions/native"
        
        payload = {
            "appid": self.appid,
            "mchid": self.mchid,
            "description": subject,
            "out_trade_no": out_trade_no,
            "notify_url": notify_url or "https://your-domain.com/api/v1/payment/wechat/notify",
            "amount": {
                "total": int(amount * 100),
                "currency": "CNY"
            }
        }
        
        if body:
            payload["attach"] = body
        
        body_json = json.dumps(payload, ensure_ascii=False)
        authorization = self._generate_authorization("POST", url, body_json)
        
        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = self.client.post(
            url,
            json=payload,
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"WeChat Pay error: {response.status_code} - {response.text}")
            raise Exception(f"WeChat Pay failed: {response.status_code}")
        
        result = response.json()
        
        return {
            "code_url": result.get("code_url"),
            "prepay_id": result.get("prepay_id")
        }
    
    def query_order(
        self,
        out_trade_no: Optional[str] = None,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query order status
        
        Args:
            out_trade_no: Merchant order number
            transaction_id: WeChat transaction ID
            
        Returns:
            Order information
        """
        if not out_trade_no and not transaction_id:
            raise ValueError("Either out_trade_no or transaction_id is required")
        
        if out_trade_no:
            url = f"/v3/pay/transactions/out-trade-no/{out_trade_no}"
        else:
            url = f"/v3/pay/transactions/id/{transaction_id}"
        
        authorization = self._generate_authorization("GET", url)
        
        headers = {
            "Authorization": authorization,
            "Accept": "application/json"
        }
        
        response = self.client.get(
            url,
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"WeChat Pay query error: {response.status_code} - {response.text}")
            raise Exception(f"WeChat Pay query failed: {response.status_code}")
        
        return response.json()
    
    def refund(
        self,
        out_refund_no: str,
        out_trade_no: str,
        amount: float,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Refund order
        
        Args:
            out_refund_no: Merchant refund number
            out_trade_no: Merchant order number
            amount: Refund amount (in CNY)
            reason: Refund reason
            
        Returns:
            Refund information
        """
        url = "/v3/refund/domestic/refunds"
        
        order_info = self.query_order(out_trade_no=out_trade_no)
        total_amount = order_info["amount"]["total"] / 100
        
        payload = {
            "out_trade_no": out_trade_no,
            "out_refund_no": out_refund_no,
            "reason": reason or "用户申请退款",
            "amount": {
                "refund": int(amount * 100),
                "total": int(total_amount * 100),
                "currency": "CNY"
            }
        }
        
        body_json = json.dumps(payload, ensure_ascii=False)
        authorization = self._generate_authorization("POST", url, body_json)
        
        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = self.client.post(
            url,
            json=payload,
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"WeChat Pay refund error: {response.status_code} - {response.text}")
            raise Exception(f"WeChat Pay refund failed: {response.status_code}")
        
        return response.json()
    
    def close(self):
        """Close HTTP client"""
        self.client.close()


def nonce_str(length: int = 16) -> str:
    """Generate random nonce string"""
    import secrets
    return secrets.token_hex(length // 2)
