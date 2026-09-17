# Copyright © 2025-2026 Cognizant Technology Solutions Corp, www.cognizant.com.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# END COPYRIGHT

from unittest import TestCase

from coded_tools.basic.coffee_finder_advanced.order_api import OrderAPI


class TestOrderAPI(TestCase):
    """
    Unit tests for the OrderAPI class.
    """

    def test_invoke(self):
        """
        Tests the invoke method of the OrderAPI CodedTool.
        Checks the response is correctly generated when all params are provided and valid.
        """
        order_api = OrderAPI()
        order = {"customer_name": "Olivier", "shop_name": OrderAPI.SHOP_1, "order_details": "Black coffee"}
        response_1 = order_api.invoke(args=order, sly_data={})
        expected_resp_1 = f"Order 101 placed successfully for Olivier at {OrderAPI.SHOP_1}. Details: Black coffee"
        self.assertEqual(expected_resp_1, response_1)

    def test_invoke_customer_name(self):
        """
        Tests the invoke method of the OrderAPI CodedTool when no customer name is provided.
        Checks the fallback to sly data.
        """
        order_api = OrderAPI()
        order = {"shop_name": OrderAPI.SHOP_1, "order_details": "Black coffee"}
        response_1 = order_api.invoke(args=order, sly_data={})
        expected_error_1 = "Error: Please provide a valid customer name for the order."
        self.assertEqual(expected_error_1, response_1)

        sly_data = {"username": "Olivier"}
        response_2 = order_api.invoke(args=order, sly_data=sly_data)
        expected_resp_2 = f"Order 101 placed successfully for Olivier at {OrderAPI.SHOP_1}. Details: Black coffee"
        self.assertEqual(expected_resp_2, response_2)

    def test_invoke_customer_name_mismatch(self):
        """
        Regression test for a partial name (e.g. "Pixel") being silently accepted as a
        match for a full name already on file (e.g. "Pixel Smith"). See issue #557:
        a partial-name match must NOT be treated as the same customer.
        """
        order_api = OrderAPI()
        sly_data = {"username": "Pixel Smith"}
        order = {"customer_name": "Pixel", "shop_name": OrderAPI.SHOP_3, "order_details": "Black coffee"}
        response = order_api.invoke(args=order, sly_data=sly_data)
        expected_error = "Error: The name 'Pixel' does not match the name on file ('Pixel Smith')."
        self.assertTrue(response.startswith(expected_error))
        # The mismatched name must not overwrite the name already on file.
        self.assertEqual("Pixel Smith", sly_data["username"])

    def test_invoke_customer_name_match_is_case_and_whitespace_insensitive(self):
        """
        A name that matches the one on file, modulo case/leading-trailing whitespace,
        should still be accepted (this is not the "Pixel"-vs-"Pixel Smith" bug).
        """
        order_api = OrderAPI()
        customer_name = " pixel smith  "
        sly_data = {"username": "Pixel Smith"}
        order = {"customer_name": customer_name, "shop_name": OrderAPI.SHOP_3, "order_details": "Black coffee"}
        response = order_api.invoke(args=order, sly_data=sly_data)
        expected_resp = (
            f"Order 301 placed successfully for {customer_name} at {OrderAPI.SHOP_3}. Details: Black coffee"
        )
        self.assertEqual(expected_resp, response)

    def test_invoke_shop_name(self):
        """
        Tests the invoke method of the OrderAPI CodedTool when an invalid or no shop name is provided.
        """
        order_api = OrderAPI()
        order = {"customer_name": "Olivier", "order_details": "Black coffee"}
        response_1 = order_api.invoke(args=order, sly_data={})
        expected_error_1 = "Error: Please provide the name of the shop for the order."
        self.assertEqual(expected_error_1, response_1)

        order = {"customer_name": "Olivier", "shop_name": "Unknown shop", "order_details": "Black coffee"}
        response_2 = order_api.invoke(args=order, sly_data={})
        expected_error_2 = "Error: Please provide a valid shop name."
        self.assertTrue(response_2.startswith(expected_error_2))

    def test_invoke_order_id(self):
        """
        Tests the invoke method of the OrderAPI CodedTool.
        Checks the order id is different for each shop
        """
        order_api = OrderAPI()
        order = {"customer_name": "Olivier", "shop_name": OrderAPI.SHOP_1, "order_details": "Black coffee"}
        response_1 = order_api.invoke(args=order, sly_data={})
        expected_resp_1 = f"Order 101 placed successfully for Olivier at {OrderAPI.SHOP_1}. Details: Black coffee"
        self.assertEqual(expected_resp_1, response_1)

        order = {"customer_name": "Olivier", "shop_name": OrderAPI.SHOP_2, "order_details": "Black coffee"}
        response_2 = order_api.invoke(args=order, sly_data={})
        expected_resp_2 = f"Order 201 placed successfully for Olivier at {OrderAPI.SHOP_2}. Details: Black coffee"
        self.assertEqual(expected_resp_2, response_2)

        order = {"customer_name": "Olivier", "shop_name": OrderAPI.SHOP_3, "order_details": "Black coffee"}
        response_3 = order_api.invoke(args=order, sly_data={})
        expected_resp_3 = f"Order 301 placed successfully for Olivier at {OrderAPI.SHOP_3}. Details: Black coffee"
        self.assertEqual(expected_resp_3, response_3)
