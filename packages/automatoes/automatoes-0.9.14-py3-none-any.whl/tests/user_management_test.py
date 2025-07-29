# Copyright 2019-2024 Flavio Garcia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from . import get_absolute_path
from automatoes.crypto import generate_rsa_key
from automatoes.model import Account
from automatoes.protocol import AcmeV2Pesant, AcmeRequestsTransport
from cartola.security import random_string
from tornado import testing


def get_contacts(domain_name: str, num: int = 1):
    contacts = []
    for _ in range(0, num):
        user_name = (f"{random_string(5, False, False)}_"
                     f"{random_string(5, False, False)}")
        contacts.append(f"{user_name}@{domain_name}")
    return contacts


class UserManagementTestCase(testing.AsyncTestCase):
    """ Test letsencrypt new account
    """

    @testing.gen_test
    async def test_nonce(self):
        transport = AcmeRequestsTransport("https://localhost:14000")
        protocol = AcmeV2Pesant(
                transport,
                directory="dir",
                verify=get_absolute_path("certs/candango.minica.pem")
        )
        contacts = get_contacts("candango.org", 2)
        peeble_term = ("data:text/plain,Do%20what%20thou%20wilt")
        account = Account(key=generate_rsa_key(4096))

        print(contacts)
        # self.assertIsNotNone(protocol.new_nonce())
        # user_name = "candango_{}_{}@candango.org".format(
        #     security.random_string(5, False, False),
        #     security.random_string(5, False, False)
        # )
        # # To check against the get_registration method after
        # # TODO: check against more than one emails in the contacts
        # user_contacts = [user_name]
        # peeble_term = ("data:text/plain,Do%20what%20thou%20wilt")
        # context.acme_v2.set_account(Account(key=generate_rsa_key(4096)))
        # response = context.acme_v2.register(user_name, True)
        # context.tester.assertEqual(peeble_term, response.terms)
        # context.tester.assertEqual("valid", response.contents['status'])
        # context.tester.assertEqual(
        #     context.peeble_url, "/".join(response.uri.split("/")[0:3]))
        # context.tester.assertEqual(
        #     "my-account", "/".join(response.uri.split("/")[3:4]))
        # context.tester.assertIsInstance(response.uri.split("/")[4:5][0], str)
        # context.acme_v2.get_registration()
