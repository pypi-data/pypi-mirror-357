#!/usr/bin/env python
#
# Copyright 2019-2022 Flávio Gonçalves Garcia
# Copyright 2016-2017 Veeti Paananen under MIT License
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
import locale
import sys


def confirm(msg, default=True, verbose=False):
    if verbose:
        print("Preferred encoding: %s" % locale.getpreferredencoding())
        print("Default locale:\n lang: %s, encoding: %s"
              % locale.getdefaultlocale())
        print("Current input encoding: %s" % sys.stdin.encoding)
        print("Current output encoding: %s" % sys.stdout.encoding)
        print("Byte order: %s\n" % sys.byteorder)
    no_encode_found = False
    while True:
        choices = "Y/n" if default else "y/N"
        try:
            answer, encoding = decode(input("%s [%s] " % (msg, choices)))
        except UnicodeDecodeError as ude:
            if verbose:
                print(ude)
                print("Setting answer to: UnicodeDecodeError")
            answer = "UnicodeDecodeError"
        except UnicodeEncodeError as uee:
            if verbose:
                print(uee)
            answer = "UnicodeEncodeError"
        if "no encode found" in answer:
            no_encode_found = True
        if no_encode_found:
            if verbose:
                print("Answer: %s" % answer)
            print("Not able to decode the input with utf-8, utf-16 nor "
                  "utf-32, please file a bug for that.")
            return False
        answer = answer.strip().lower()
        if answer in {"yes", "y"} or (default and not answer):
            return True
        if answer in {"no", "n"} or (not default and not answer):
            return False


def decode(answer: str, encoding="utf-8") -> (str, str):
    try:
        return answer.encode(encoding).decode(encoding), encoding
    except UnicodeDecodeError as ude:
        last_exception = "%s" % ude
    except UnicodeEncodeError as uee:
        last_exception = "%s" % uee
    if encoding != "utf-32":
        if encoding == "utf-8":
            return decode(answer, "utf-16")
        if encoding == "utf-16":
            return decode(answer, "utf-32")
    return "no encode found exception(%s)" % last_exception, encoding
