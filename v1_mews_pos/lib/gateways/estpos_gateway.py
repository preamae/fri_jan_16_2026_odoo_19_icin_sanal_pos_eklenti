# -*- coding: utf-8 -*-

from .base_gateway import BaseGateway
from ..crypto_utils import CryptoUtils
from ..xml_utils import XmlUtils
import random
import logging

_logger = logging.getLogger(__name__)


class EstPosGateway(BaseGateway):
    """EstPos/EstV3Pos Gateway (Akbank, İşbank, TEB, Şekerbank, Finansbank)"""

    def prepare_3d_request(self, order, card):
        """3D Secure form verisi hazırla"""
        config = self.config
        rnd = str(random.randint(100000, 999999))
        
        # Hash oluştur
        hash_str = CryptoUtils.create_3d_hash_estpos(
            client_id=config['client_id'],
            order_id=order['id'],
            amount=self.format_amount(order['amount']),
            ok_url=order['success_url'],
            fail_url=order['fail_url'],
            trans_type='Auth',
            installment=self. format_installment(order. get('installment', 1)),
            rnd=rnd,
            store_key=config['store_key'],
            hash_algorithm='sha512'
        )

        form_data = {
            'clientid': config['client_id'],
            'storetype': '3d_pay',
            'hash': hash_str,
            'hashAlgorithm': 'ver3',
            'lang': order. get('lang', 'tr'),
            'TranType': 'Auth',
            'currency': self.map_currency(order.get('currency', 'TRY')),
            'oid': order['id'],
            'amount': self.format_amount(order['amount']),
            'okUrl': order['success_url'],
            'failUrl': order['fail_url'],
            'rnd': rnd,
            'pan': card['number'],
            'Ecom_Payment_Card_ExpDate_Year': card['year'],
            'Ecom_Payment_Card_ExpDate_Month': card['month'],
            'cv2': card['cvv'],
            'cardHolderName': card['name'],
        }

        # Taksit
        if order.get('installment', 1) > 1:
            form_data['taksit'] = str(order['installment'])

        return {
            'gateway_url': config['gateway_3d_url'],
            'method': 'POST',
            'inputs': form_data
        }

    def parse_3d_response(self, response_data):
        """3D yanıtını parse et"""
        md_status = response_data.get('mdStatus', '0')
        
        # mdStatus değerleri: 
        # 1: Tam doğrulama
        # 2,3,4: Kısmi doğrulama
        # 0,5,6,7,8,9: Başarısız
        
        approved = md_status in ['1', '2', '3', '4']
        
        return {
            'approved': approved,
            'order_id': response_data.get('oid'),
            'auth_code': response_data.get('AuthCode'),
            'host_ref_num': response_data.get('HostRefNum'),
            'proc_return_code': response_data.get('ProcReturnCode'),
            'md_status': md_status,
            'eci': response_data.get('eci'),
            'cavv':  response_data.get('cavv'),
            'xid': response_data.get('xid'),
            'error_code': response_data.get('ErrCode'),
            'error_message': response_data.get('ErrMsg') or response_data.get('mdErrorMsg'),
            'response': response_data. get('Response'),
        }

    def prepare_payment_request(self, order, card):
        """Non-secure ödeme isteği hazırla"""
        config = self.config
        
        xml_data = {
            'Name': config['username'],
            'Password': config['password'],
            'ClientId': config['client_id'],
            'Type': 'Auth',
            'IPAddress': order. get('ip_address', '127.0.0.1'),
            'Email': order.get('email', ''),
            'OrderId': order['id'],
            'Total': self.format_amount(order['amount']),
            'Currency': self.map_currency(order.get('currency', 'TRY')),
            'Taksit': self.format_installment(order.get('installment', 1)),
            'Number': card['number'],
            'Expires': f"{card['month']}/{card['year']}",
            'Cvv2Val': card['cvv'],
        }

        xml_string = XmlUtils.dict_to_xml({'CC5Request': xml_data}, root_name='CC5Request')

        return {
            'url': config['payment_api_url'],
            'data': {'DATA': xml_string},
            'headers': {'Content-Type': 'application/x-www-form-urlencoded'}
        }

    def parse_payment_response(self, response):
        """Ödeme yanıtını parse et"""
        xml_response = response.text
        parsed = XmlUtils.xml_to_dict(xml_response)
        
        if 'CC5Response' in parsed: 
            data = parsed['CC5Response']
            proc_return_code = data.get('ProcReturnCode', '')
            approved = proc_return_code == '00'
            
            return {
                'approved': approved,
                'order_id': data. get('OrderId'),
                'auth_code': data.get('AuthCode'),
                'host_ref_num': data.get('HostRefNum'),
                'proc_return_code': proc_return_code,
                'error_code': data.get('ErrCode'),
                'error_message': data.get('ErrMsg'),
                'response': data.get('Response'),
            }
        
        return {'approved': False, 'error_message': 'Geçersiz yanıt formatı'}

    def prepare_cancel_request(self, order):
        """İptal isteği hazırla"""
        config = self.config
        
        xml_data = {
            'Name': config['username'],
            'Password': config['password'],
            'ClientId': config['client_id'],
            'Type': 'Void',
            'OrderId': order['id'],
        }

        xml_string = XmlUtils.dict_to_xml({'CC5Request': xml_data}, root_name='CC5Request')

        return {
            'url': config['payment_api_url'],
            'data': {'DATA': xml_string},
            'headers': {'Content-Type':  'application/x-www-form-urlencoded'}
        }

    def prepare_refund_request(self, order, amount=None):
        """İade isteği hazırla"""
        config = self. config
        refund_amount = amount if amount else order['amount']
        
        xml_data = {
            'Name':  config['username'],
            'Password': config['password'],
            'ClientId': config['client_id'],
            'Type': 'Credit',
            'OrderId': order['id'],
            'Total': self.format_amount(refund_amount),
            'Currency': self.map_currency(order.get('currency', 'TRY')),
        }

        xml_string = XmlUtils.dict_to_xml({'CC5Request': xml_data}, root_name='CC5Request')

        return {
            'url': config['payment_api_url'],
            'data': {'DATA': xml_string},
            'headers': {'Content-Type':  'application/x-www-form-urlencoded'}
        }