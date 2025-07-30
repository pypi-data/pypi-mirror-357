import os
import httpx
import logging
from typing import List, Optional, Union, BinaryIO
import base64
from .models import VoiceActor, VoiceGenerationRequest, Balance
from .exceptions import NijiVoiceAPIError

# ロガーの設定
logger = logging.getLogger('nijivoice_mcp.api')

class NijiVoiceClient:
    """にじボイスAPIクライアント"""
    
    BASE_URL = "https://api.nijivoice.com/api/platform/v1"
    
    def __init__(self, api_key: Optional[str] = None, timeout: Optional[float] = 30.0):
        """
        初期化
        
        Args:
            api_key: APIキー。指定しない場合は環境変数 NIJIVOICE_API_KEY から読み込みます。
            timeout: HTTPリクエストのタイムアウト時間（秒）
        """
        self.api_key = api_key or os.environ.get("NIJIVOICE_API_KEY")
        if not self.api_key:
            raise ValueError("APIキーが指定されていません。引数で指定するか、NIJIVOICE_API_KEY 環境変数を設定してください。")
        
        self.timeout = timeout
        self.headers = {
            "x-api-key": self.api_key,
            "Accept": "application/json",
        }
    
    async def get_voice_actors(self) -> List[VoiceActor]:
        """
        利用可能なVoice Actorの一覧を取得します。
        
        Returns:
            Voice Actorのリスト
        
        Raises:
            NijiVoiceAPIError: API呼び出しに失敗した場合
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.BASE_URL}/voice-actors", headers=self.headers)
                
                if response.status_code != 200:
                    raise NijiVoiceAPIError(
                        f"Voice Actor一覧の取得に失敗しました: {response.text}",
                        status_code=response.status_code
                    )
                
                data = response.json()
                # APIがvoiceActorsキーの中に配列を返す場合の対応
                if isinstance(data, dict):
                    actors_data = data.get("voiceActors", data)
                else:
                    actors_data = data
                
                if not isinstance(actors_data, list):
                    # データがリストでない場合は空リストを返す
                    logger.warning(f"予期しないデータ形式です: {data}")
                    return []
                    
                return [VoiceActor.model_validate(actor) for actor in actors_data]
        except TimeoutError:
            raise NijiVoiceAPIError("APIリクエストがタイムアウトしました", status_code=408)
        except NijiVoiceAPIError:
            raise
        except Exception as e:
            raise NijiVoiceAPIError(f"API呼び出し中にエラーが発生しました: {str(e)}", status_code=500)
    
    async def generate_voice(
        self, 
        request: VoiceGenerationRequest,
    ) -> dict:
        """
        指定されたVoice Actorの声で音声を生成します。
        
        Args:
            voice_actor_id: Voice Actor ID
            request: 音声生成リクエスト
            
        Returns:
            APIレスポンス
        """
        url = f"{self.BASE_URL}/voice-actors/{request.id}/generate-voice"
        
        # リクエストデータを準備（None値のフィールドは除外）
        request_data = request.model_dump(by_alias=True)
        logger.debug("Sending request data to API: %s", request_data)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url, 
                headers=self.headers,
                json=request_data,
            )
            
            if response.status_code != 200:
                raise NijiVoiceAPIError(f"音声生成に失敗しました: {response.text}", status_code=response.status_code)
            
            data = response.json()
            logger.debug("generate_voice API response: %s", data)
            
            return data

    
    async def get_balance(self) -> Balance:
        """
        クレジット残高を取得します。
        
        Returns:
            クレジット残高
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.BASE_URL}/balances", headers=self.headers)
            
            if response.status_code != 200:
                raise NijiVoiceAPIError(f"クレジット残高の取得に失敗しました: {response.text}", status_code=response.status_code)
            
            data = response.json()
            # APIレスポンスの構造をログに出力
            logger.debug(f"Balance API response: {data}")
            
            # モデル検証
            balance = Balance.model_validate(data)
            return balance
