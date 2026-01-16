# -*- coding: utf-8 -*-

from .estpos_gateway import EstPosGateway
from .garanti_gateway import GarantiGateway
from .posnet_gateway import PosNetGateway
from .payfor_gateway import PayForGateway
from .kuveyt_gateway import KuveytPosGateway
from .payflex_gateway import PayFlexGateway
from .interpos_gateway import InterPosGateway
from .akbank_gateway import AkbankGateway
from .tosla_gateway import ToslaGateway
import logging

_logger = logging.getLogger(__name__)


class GatewayFactory:
    """Gateway factory sınıfı - Doğru gateway'i oluşturur"""
    
    GATEWAY_MAP = {
        'akbank_pos': AkbankGateway,
        'estv3_pos': EstPosGateway,
        'estpos': EstPosGateway,
        'garanti_pos': GarantiGateway,
        'posnet': PosNetGateway,
        'posnet_v1': PosNetGateway,
        'payfor': PayForGateway,
        'payflex_mpi': PayFlexGateway,
        'payflex_common': PayFlexGateway,
        'interpos': InterPosGateway,
        'kuveyt_pos': KuveytPosGateway,
        'tosla': ToslaGateway,
        'param_pos': EstPosGateway,  # ParamPos da EstPos benzeri
        'vakif_katilim': PayFlexGateway,  # VakıfKatılım da PayFlex benzeri
    }
    
    @staticmethod
    def create(gateway_type, config):
        """
        Gateway oluştur
        
        Args:
            gateway_type (str): Gateway tipi (akbank_pos, garanti_pos, vb.)
            config (dict): Gateway konfigürasyonu
            
        Returns:
            BaseGateway: İlgili gateway instance
            
        Raises:
            ValueError: Desteklenmeyen gateway tipi
        """
        gateway_class = GatewayFactory.GATEWAY_MAP.get(gateway_type)
        
        if not gateway_class:
            _logger.error(f"Desteklenmeyen gateway tipi: {gateway_type}")
            raise ValueError(f"Desteklenmeyen gateway tipi: {gateway_type}")
        
        _logger.info(f"Gateway oluşturuluyor: {gateway_type}")
        return gateway_class(config)
    
    @staticmethod
    def get_supported_gateways():
        """Desteklenen gateway listesini döndür"""
        return list(GatewayFactory.GATEWAY_MAP.keys())
    
    @staticmethod
    def is_supported(gateway_type):
        """Gateway'in desteklenip desteklenmediğini kontrol et"""
        return gateway_type in GatewayFactory.GATEWAY_MAP