import secrets
import hashlib
import json
import logging

from django.conf import settings
from django.http import Http404
from importlib import import_module


module, _class = settings.PZ_SERVICE_CLASS.rsplit(".", 1)
Service = getattr(import_module(module), _class)

logger = logging.getLogger(__name__)


class CheckoutService(Service):

    def get_form_data(self, request):
        salt = self.generate_salt(length=10)
        session_id = request.GET.get("sessionId")
        
        hash_ = self.generate_hash(salt, session_id)
        body = self._get_form_data(request)
        body.update({
            "hash": hash_,
            "salt": salt,
        })
        return json.dumps(body, ensure_ascii=False)

    def generate_salt(self, length=0):
        salt = secrets.token_hex(10)
        return salt if not length else salt[:length]

    def generate_hash(self, salt, *args):
        hash_key = getattr(settings, "HASH_SECRET_KEY")
        hash_body = "|".join(args)
        return hashlib.sha512(
            f"{salt}|{hash_body}|{hash_key}".encode("utf-8")
        ).hexdigest()

    def _validate_checkout_step(self, response, required_page="PaymentOptionSelectionPage"):
        if "pre_order" not in response.data:
            raise Http404()
        
        if response.data["pre_order"].get("shipping_option") is None:
            raise Http404()

        if required_page:
            page_names = [page["page_name"] for page in response.data["context_list"]]
            if "PaymentOptionSelectionPage" not in page_names:
                raise Http404()

    def _get_address(self, address_response):
        if not address_response:
            return {}
        return {
            "city": address_response["city"]["name"],
            "country": address_response["country"]["code"].upper(),
            "zip_code": address_response["postcode"],
        }

    def _get_form_data(self, request):
        response = self._retrieve_pre_order(request)
        self._validate_checkout_step(response=response)

        pre_order = response.data.get("pre_order", {})
        payment_option = pre_order.get("payment_option", {})
        payment_option_slug = payment_option.get("slug", "")

        multisafe_payment_methods_map = getattr(settings, "MULTISAFEPAY_PAYMENT_METHODS", {})
        gateway = multisafe_payment_methods_map.get(payment_option_slug)

        address = pre_order.get("billing_address") or pre_order.get("shipping_address")

        return {
            "gateway": gateway,
            "customer": self._get_address(address)
        }

    def _retrieve_pre_order(self, request):
        path = "/orders/checkout/"
        response = self.get(
            path, request=request, headers={"X-Requested-With": "XMLHttpRequest"}
        )
        return self.normalize_response(response)
