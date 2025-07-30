from typing import Optional, List, Literal
import logging
from pydantic import BaseModel, field_serializer, Field, ConfigDict

# ロガーの設定
logger = logging.getLogger('nijivoice_mcp.models')


class RecommendedParameters(BaseModel):
    """にじボイスの推奨パラメータモデル"""
    emotional_level: Optional[float] = Field(1.0, alias="emotionalLevel")
    sound_duration: Optional[float] = Field(1.0, alias="soundDuration")

    # 未知のフィールドをスキップする設定
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"  # 未知のフィールドを無視する
    )

class VoiceStyle(BaseModel):
    """にじボイスのVoice Styleモデル"""
    id: int
    style: str
    
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"  # 未知のフィールドを無視する
    )

class VoiceActor(BaseModel):
    """にじボイスのVoice Actorモデル"""
    id: str
    name: str
    name_reading: Optional[str] = Field(None, alias="nameReading")
    age: Optional[int] = None
    gender: Optional[str] = None
    birth_month: Optional[int] = Field(None, alias="birthMonth")
    birth_day: Optional[int] = Field(None, alias="birthDay")
    description: Optional[str] = ""
    
    # 画像URL
    small_image_url: Optional[str] = Field(None, alias="smallImageUrl")
    medium_image_url: Optional[str] = Field(None, alias="mediumImageUrl")
    large_image_url: Optional[str] = Field(None, alias="largeImageUrl")
    image_url: Optional[str] = Field(None, alias="imageUrl")  # 後方互換性のため
    
    # 音声サンプル
    sample_voice_url: Optional[str] = Field(None, alias="sampleVoiceUrl")
    sample_audio_url: Optional[str] = Field(None, alias="sampleAudioUrl")  # 後方互換性のため
    sample_script: Optional[str] = Field(None, alias="sampleScript")
    
    # 推奨パラメータ
    recommended_voice_speed: Optional[float] = Field(None, alias="recommendedVoiceSpeed")
    recommended_emotional_level: Optional[float] = Field(None, alias="recommendedEmotionalLevel")
    recommended_sound_duration: Optional[float] = Field(None, alias="recommendedSoundDuration")
    recommended_parameters: Optional[RecommendedParameters] = Field(None, alias="recommendedParameters")
    
    # ボイススタイル
    voice_styles: Optional[List[VoiceStyle]] = Field(None, alias="voiceStyles")
    
    # 未知のフィールドをスキップする設定
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"  # 未知のフィールドを無視する
    )

class VoiceGenerationRequest(BaseModel):
    """音声生成リクエストモデル"""
    id: str = Field(default="5c7f729f-5814-436f-9e81-95aa837f9737", description="Voice Actor ID")
    script: str = Field(default="これはにじボイスMCPで生成しました", description="生成する音声のテキスト")
    speed: float = Field(default=1.0, description="話速", ge=0.4, le=3.0)
    emotional_level: Optional[float] = Field(
        default=None,
        alias="emotionalLevel",
        description="感情レベル",
        ge=0.0,
        le=1.5
    )
    sound_duration: Optional[float] = Field(
        default=None,
        alias="soundDuration",
        description="音の継続時間",
        ge=0.0,
        le=1.7
    )
    format: Literal["mp3", "wav"] = Field(
        default="mp3",
        description="音声フォーマット"
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @field_serializer('speed')
    def serialize_speed(self, speed: float) -> str:
        return str(speed)
        
    @field_serializer('emotional_level')
    def serialize_emotional_level(self, emotional_level: Optional[float]) -> Optional[str]:
        return str(emotional_level) if emotional_level is not None else None
        
    @field_serializer('sound_duration')
    def serialize_sound_duration(self, sound_duration: Optional[float]) -> Optional[str]:
        return str(sound_duration) if sound_duration is not None else None

    @field_serializer('format')
    def serialize_format(self, fmt: str):
        return fmt.lower()
        
    def model_dump(self, **kwargs):
        """カスタムdump処理: Noneの値を持つフィールドは除外"""
        data = super().model_dump(**kwargs)
        # Noneの値を持つフィールドを削除
        return {k: v for k, v in data.items() if v is not None}


class Balance(BaseModel):
    """クレジット残高モデル"""
    balance: Optional[int] = None
    balances: Optional[dict] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"  # 未知のフィールドを無視する
    )
    
    def get_credit(self) -> int:
        """異なるレスポンス形式に対応してクレジット残高を取得する"""
        # 直接balanceフィールドがある場合
        if self.balance is not None:
            return self.balance
        
        # balancesオブジェクト内の様々な構造に対応
        if self.balances and isinstance(self.balances, dict):
            # remainingBalanceがある場合
            if 'remainingBalance' in self.balances:
                return self.balances['remainingBalance']
            # balanceがある場合
            elif 'balance' in self.balances:
                return self.balances['balance']
            
            # creditsリストがあり、その中にbalanceがある場合
            if 'credits' in self.balances and isinstance(self.balances['credits'], list) and len(self.balances['credits']) > 0:
                for credit in self.balances['credits']:
                    if isinstance(credit, dict) and 'balance' in credit:
                        return credit['balance']
        
        # どのフィールドにも残高情報がない場合
        logger.warning("クレジット残高情報が見つかりませんでした")
        return 0
